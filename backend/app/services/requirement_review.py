"""Requirement-centric review engine: the second review path.

The finding-centric pipeline asks ten agents "what do you notice?" and then
tries to tame the resulting list (redundancy rate 0.85, ~20 findings per case
after clustering). This engine asks the inverse question, once per requirement:
"is this obligation fulfilled, violated or unclear in these documents, and
where is the evidence?" The unit of output is the requirement verdict, so a
duplicate has no place to exist.

Three layers, in order of trust:

1. Server-side applicability. Requirements whose document type or process area
   does not match the set are answered NOT_APPLICABLE without a model call.
2. Assessor calls, one per requirement group, using the same provider
   infrastructure as the finding path (retries, circuit breaker, structured
   output). Evidence is then checked for provenance against the stored chunks;
   a quote that does not appear in its cited chunk is dropped, and a verdict
   whose evidence all fails provenance is downgraded to UNCLEAR.
3. Entailment verification for VIOLATED verdicts: a second model answers
   whether the surviving quotes actually justify the claim. "none" downgrades
   to UNCLEAR. This replaces the lexical claim-support check, which marked
   98-100% of findings unsupported on every measured corpus and therefore
   distinguished nothing.

Verification only ever demotes -- a verdict is never upgraded by a checker.
Failure is fail-secure: a failed assessor call yields server-authored UNCLEAR
verdicts for its whole group, which in a QA process means human review.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.agents.providers import (
    AnthropicProvider,
    BaseModelProvider,
    MistralProvider,
    MockProvider,
    OpenAIProvider,
    ProviderRuntimeOptions,
)
from app.audit.events import InMemoryAuditLog
from app.core.config import Settings, get_settings
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import DocumentChunk, DocumentSet, Requirement, Severity
from app.schemas.requirement_review import (
    EntailmentCheck,
    EntailmentSupport,
    EvidenceSufficiency,
    FulfilledChallenge,
    RequirementCoverageReport,
    RequirementGroupOutput,
    RequirementReviewEvidence,
    RequirementReviewModelCall,
    RequirementVerdict,
    RequirementVerdictStatus,
    VerifiedRequirementVerdict,
)

ENGINE_VERSION = "requirement-review-v0.1"

#: Requirements per assessor call. Small enough that each verdict gets real
#: attention and the output fits comfortably in the token budget, large enough
#: that a typical case needs three to five calls instead of twenty-eight.
REQUIREMENT_GROUP_SIZE = 6

#: Characters of chunk text passed to the assessor per chunk.
MAX_CHUNK_CHARS = 6000

ASSESSOR_PROMPT = (
    "Du bist ein pharmazeutischer QA-Reviewer. Du erhältst Dokumentauszüge "
    "(chunks) eines GMP-Vorgangs und eine Liste von Anforderungen "
    "(requirements). Beurteile jede Anforderung einzeln.\n\n"
    "Mögliche Status je Anforderung:\n"
    "- fulfilled: Die Unterlagen belegen die Erfüllung. Zitiere den Beleg.\n"
    "- violated: Die Unterlagen belegen einen Verstoß ODER sie belegen den "
    "auslösenden Vorgang, während der geforderte Nachweis fehlt. Bei einem "
    "fehlenden Nachweis zitiere den Auslöser (die Stelle, die die Pflicht "
    "begründet) -- eine Lücke ist nur dann ein Verstoß, wenn ihr Auslöser "
    "belegt ist.\n"
    "- unclear: Die Unterlagen reichen für keine der beiden Aussagen.\n"
    "- not_applicable: Die Anforderung betrifft diesen Vorgang erkennbar "
    "nicht.\n\n"
    "Harte Regeln:\n"
    "- Verwende ausschließlich die übergebenen Chunks. Kein externes Wissen.\n"
    "- Jedes Zitat muss wortwörtlich und zusammenhängend aus dem genannten "
    "Chunk stammen, mit document_id, chunk_id und page aus den Eingaben.\n"
    "- Für fulfilled und violated ist mindestens ein Zitat Pflicht.\n"
    "- Setze severity nur bei violated oder unclear (critical, high, medium, "
    "low, informational).\n"
    "- Formuliere rationale auf Deutsch mit den korrekten Umlauten ä, ö, ü "
    "und ß; schreibe niemals ae, oe, ue oder ss als Ersatz.\n"
    "- Gib für jede übergebene Anforderung genau ein Verdict zurück.\n"
    "- Denke konservativ: Ein möglicher schwerer Verstoß, der nicht widerlegt "
    "ist, gehört als violated oder unclear zur menschlichen Prüfung, nicht "
    "stillschweigend als fulfilled abgehakt.\n\n"
    "Evidenzskepsis für fulfilled:\n"
    "- Verlangt die Anforderung die DURCHFÜHRUNG einer Tätigkeit (Review, "
    "Prüfung, Training, Bewertung), dann genügt die nachträgliche Behauptung "
    "'durchgeführt, keine Auffälligkeiten' nicht. Es braucht Primärevidenz: "
    "einen Audit-Trail-Auszug, eine Checkliste, Rohdaten, signierte zeitnahe "
    "Dokumentation oder konkrete referenzierbare Ergebnisse.\n"
    "- Verlangt die Anforderung lediglich, dass eine bestimmte ERKLÄRUNG oder "
    "FREIGABE dokumentiert ist, kann die signierte Erklärung selbst die "
    "Evidenz sein.\n"
    "- Prüfe Pflichtfelder einzeln: Ein vorhandener Signaturblock heißt nicht, "
    "dass jede geforderte Unterschrift geleistet ist. Ein leeres Pflichtfeld "
    "ist ein Befund.\n"
    "- Vergleiche Messwerte einzeln mit ihren deklarierten Grenzen, bevor du "
    "einen Bereich als eingehalten wertest.\n\n"
    "Zusatzfelder für jedes fulfilled-Verdict (sonst null):\n"
    "- evidence_type: Art des tragenden Nachweises (z. B. 'Audit-Trail-Auszug', "
    "'signierte Freigabeerklärung', 'Rohdaten').\n"
    "- evidence_reference: wo der Nachweis steht (Dokument/Abschnitt).\n"
    "- evidence_sufficiency: sufficient, partial oder insufficient.\n"
    "- independent_support: true nur, wenn der Nachweis über die bloße "
    "Selbstauskunft des geprüften Dokuments hinausgeht.\n"
    "- Ein fulfilled mit evidence_sufficiency=insufficient ist keins: dann "
    "unclear."
)

CHALLENGE_PROMPT = (
    "Du bist ein skeptischer QA-Zweitprüfer. Ein Erstprüfer hat eine "
    "Anforderung als erfüllt bewertet. Du erhältst die Anforderung, seine "
    "Begründung und die Belegzitate.\n\n"
    "Beantworte genau eine Frage: Welche geforderte Evidenz könnte trotz der "
    "positiven Formulierung fehlen, unvollständig oder nur behauptet sein?\n\n"
    "- challenge_sustained=true, wenn ein konkreter geforderter Nachweis "
    "fehlt, nur behauptet statt belegt ist oder ein Pflichtbestandteil "
    "erkennbar unvollständig ist. Nenne die Lücken in "
    "missing_or_asserted_evidence.\n"
    "- challenge_sustained=false, wenn die Belege die Erfüllung tatsächlich "
    "tragen. Eine Erklärung oder Freigabe, deren Dokumentation selbst die "
    "Anforderung ist, gilt mit Signatur als belegt -- konstruiere dann keine "
    "künstlichen Zweifel.\n"
    "- Antworte auf Deutsch mit korrekten Umlauten ä, ö, ü, ß."
)

ENTAILMENT_PROMPT = (
    "Du prüfst einen einzelnen QA-Befund. Gegeben sind eine Behauptung "
    "(rationale) und die wörtlichen Belegzitate aus den Quelldokumenten.\n\n"
    "Beantworte ausschließlich: Rechtfertigen die Zitate die Behauptung?\n"
    "- supports: Die Zitate tragen die Behauptung. Bei einer behaupteten "
    "Lücke genügt es, wenn die Zitate den auslösenden Vorgang belegen und "
    "keines den geforderten Nachweis zeigt.\n"
    "- partial: Die Zitate tragen einen wesentlichen Teil, aber nicht die "
    "gesamte Behauptung.\n"
    "- none: Die Zitate tragen die Behauptung nicht.\n\n"
    "Beurteile nur den Zusammenhang zwischen Zitaten und Behauptung. Erfinde "
    "keine zusätzlichen Fakten. Antworte auf Deutsch mit korrekten Umlauten."
)


class RequirementReviewDocumentSetNotFoundError(Exception):
    pass


class RequirementReviewEngine:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
        assessor_provider: BaseModelProvider,
        entailment_provider: BaseModelProvider,
        group_size: int = REQUIREMENT_GROUP_SIZE,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.assessor_provider = assessor_provider
        self.entailment_provider = entailment_provider
        self.group_size = max(1, group_size)

    def run(self, document_set_id: str) -> RequirementCoverageReport:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise RequirementReviewDocumentSetNotFoundError(
                f"DocumentSet {document_set_id} not found"
            )
        chunks = self.repository.list_chunks_for_document_set(document_set_id)
        requirement_set = self.repository.get_requirement_set(
            document_set.requirement_set_id
        )
        requirements = list(requirement_set.requirements) if requirement_set else []

        applicable, inapplicable = _split_by_applicability(requirements, document_set)
        verdicts: list[VerifiedRequirementVerdict] = [
            _server_verdict(
                requirement,
                status=RequirementVerdictStatus.NOT_APPLICABLE,
                rationale=(
                    "Vom Server als nicht anwendbar eingestuft: Dokumenttyp "
                    f"'{document_set.declared_document_type}' oder Prozessbereich "
                    f"'{document_set.declared_process_area}' liegt außerhalb des "
                    "Geltungsbereichs dieser Anforderung."
                ),
            )
            for requirement in inapplicable
        ]
        model_calls: list[RequirementReviewModelCall] = []

        chunk_payload = _chunk_payload(chunks, self.repository)
        for group in _grouped(applicable, self.group_size):
            group_verdicts, call = self._assess_group(
                group=group, chunk_payload=chunk_payload, chunks=chunks
            )
            verdicts.extend(group_verdicts)
            model_calls.append(call)

        criticality_by_id = {
            requirement.requirement_id: requirement.criticality.value
            for requirement in requirements
        }
        verdicts = [self._verify_entailment(verdict, model_calls) for verdict in verdicts]
        verdicts = [
            self._challenge_fulfilled(
                verdict,
                model_calls,
                criticality=criticality_by_id.get(verdict.requirement_id, "medium"),
            )
            for verdict in verdicts
        ]

        verdicts.sort(key=lambda v: v.requirement_id)
        status_counts: dict[str, int] = {}
        for verdict in verdicts:
            status_counts[verdict.published_status.value] = (
                status_counts.get(verdict.published_status.value, 0) + 1
            )
        report = RequirementCoverageReport(
            document_set_id=document_set_id,
            engine_version=ENGINE_VERSION,
            created_at=datetime.now(UTC),
            verdicts=verdicts,
            status_counts=status_counts,
            model_calls=model_calls,
            failed_model_call_count=sum(
                1 for call in model_calls if call.status != "succeeded"
            ),
        )
        self.audit_log.append(
            event_type="requirement_review_completed",
            actor_id="service_requirement_review",
            actor_type="service",
            entity_type="DocumentSet",
            entity_id=document_set_id,
            payload=report.summary(),
        )
        return report

    def _assess_group(
        self,
        *,
        group: list[Requirement],
        chunk_payload: list[dict[str, Any]],
        chunks: list[DocumentChunk],
    ) -> tuple[list[VerifiedRequirementVerdict], RequirementReviewModelCall]:
        requirement_ids = [requirement.requirement_id for requirement in group]
        input_schema = {
            "requirements": [
                {
                    "requirement_id": requirement.requirement_id,
                    "title": requirement.title,
                    "requirement_text": requirement.requirement_text,
                    "required_evidence": requirement.required_evidence,
                    "criticality": requirement.criticality.value,
                }
                for requirement in group
            ],
            "chunks": chunk_payload,
        }
        try:
            raw = self.assessor_provider.run_structured(
                ASSESSOR_PROMPT, input_schema, RequirementGroupOutput
            )
        except Exception as exc:  # noqa: BLE001 - fail-secure per group
            call = _model_call(
                self.assessor_provider,
                purpose="assess",
                requirement_ids=requirement_ids,
                status="failed",
                error=exc,
            )
            return [
                _server_verdict(
                    requirement,
                    status=RequirementVerdictStatus.UNCLEAR,
                    rationale=(
                        "Modelllauf für diese Anforderungsgruppe fehlgeschlagen; "
                        "die Anforderung bleibt unbeurteilt und gehört zur "
                        "menschlichen Prüfung."
                    ),
                )
                for requirement in group
            ], call

        output = RequirementGroupOutput.model_validate(
            {"verdicts": raw.get("verdicts", [])}
        )
        by_id = {verdict.requirement_id: verdict for verdict in output.verdicts}
        verified = []
        for requirement in group:
            verdict = by_id.get(requirement.requirement_id)
            if verdict is None:
                verified.append(
                    _server_verdict(
                        requirement,
                        status=RequirementVerdictStatus.UNCLEAR,
                        rationale=(
                            "Das Modell hat für diese Anforderung kein Verdict "
                            "geliefert; sie bleibt unbeurteilt."
                        ),
                    )
                )
                continue
            verified.append(_check_provenance(requirement, verdict, chunks))
        call = _model_call(
            self.assessor_provider,
            purpose="assess",
            requirement_ids=requirement_ids,
            status="succeeded",
        )
        return verified, call

    def _verify_entailment(
        self,
        verdict: VerifiedRequirementVerdict,
        model_calls: list[RequirementReviewModelCall],
    ) -> VerifiedRequirementVerdict:
        """Ask a second model whether the evidence carries the claim.

        Only VIOLATED verdicts are checked: they are the rows a customer acts
        on, and the expensive failure mode is a violation whose quotes do not
        say what the rationale claims. FULFILLED verdicts keep entailment=None
        for now -- extending the check there doubles the calls and the risk it
        guards against (a false all-clear) is already covered by conservative
        prompting plus human review of everything not fulfilled.
        """
        if verdict.published_status != RequirementVerdictStatus.VIOLATED:
            return verdict
        if not verdict.evidence:
            return verdict
        input_schema = {
            "rationale": verdict.rationale,
            "quotes": [item.quote for item in verdict.evidence],
        }
        try:
            raw = self.entailment_provider.run_structured(
                ENTAILMENT_PROMPT, input_schema, EntailmentCheck
            )
            check = EntailmentCheck.model_validate(raw)
        except Exception as exc:  # noqa: BLE001 - fail-secure per verdict
            model_calls.append(
                _model_call(
                    self.entailment_provider,
                    purpose="entailment",
                    requirement_ids=[verdict.requirement_id],
                    status="failed",
                    error=exc,
                )
            )
            return verdict.model_copy(
                update={
                    "published_status": RequirementVerdictStatus.UNCLEAR,
                    "entailment": None,
                    "entailment_reason": (
                        "Entailment-Prüfung fehlgeschlagen; Verdict vorsorglich "
                        "auf unclear gestuft."
                    ),
                }
            )
        model_calls.append(
            _model_call(
                self.entailment_provider,
                purpose="entailment",
                requirement_ids=[verdict.requirement_id],
                status="succeeded",
            )
        )
        update: dict[str, Any] = {
            "entailment": check.support,
            "entailment_reason": check.reason,
        }
        if check.support == EntailmentSupport.NONE:
            update["published_status"] = RequirementVerdictStatus.UNCLEAR
        return verdict.model_copy(update=update)

    def _challenge_fulfilled(
        self,
        verdict: VerifiedRequirementVerdict,
        model_calls: list[RequirementReviewModelCall],
        *,
        criticality: str,
    ) -> VerifiedRequirementVerdict:
        """Adversarial second look at FULFILLED verdicts of critical scope.

        All five misses of the 2026-07-27 held-out run were fulfilled verdicts
        earned by self-attestation -- the QA note asserting its own audit-trail
        review was taken as proof of that review. A different provider than the
        assessor asks one question: which required evidence could be missing,
        incomplete or merely asserted despite the positive wording. Sustained
        challenge demotes to UNCLEAR; nothing is ever upgraded. Limited to
        critical and high requirements to keep the extra calls proportionate to
        what a wrong all-clear would cost.
        """
        if verdict.published_status != RequirementVerdictStatus.FULFILLED:
            return verdict
        if criticality not in {"critical", "high"}:
            return verdict
        if verdict.server_authored:
            return verdict
        input_schema = {
            "requirement_text": verdict.requirement_text,
            "rationale": verdict.rationale,
            "quotes": [item.quote for item in verdict.evidence],
            "evidence_type": verdict.evidence_type,
            "independent_support": verdict.independent_support,
        }
        try:
            raw = self.entailment_provider.run_structured(
                CHALLENGE_PROMPT, input_schema, FulfilledChallenge
            )
            challenge = FulfilledChallenge.model_validate(raw)
        except Exception as exc:  # noqa: BLE001 - fail-secure per verdict
            model_calls.append(
                _model_call(
                    self.entailment_provider,
                    purpose="challenge",
                    requirement_ids=[verdict.requirement_id],
                    status="failed",
                    error=exc,
                )
            )
            return verdict.model_copy(
                update={
                    "published_status": RequirementVerdictStatus.UNCLEAR,
                    "challenge_sustained": None,
                    "challenge_reason": (
                        "Zweitprüfung fehlgeschlagen; fulfilled vorsorglich auf "
                        "unclear gestuft."
                    ),
                }
            )
        model_calls.append(
            _model_call(
                self.entailment_provider,
                purpose="challenge",
                requirement_ids=[verdict.requirement_id],
                status="succeeded",
            )
        )
        update: dict[str, Any] = {
            "challenge_sustained": challenge.challenge_sustained,
            "challenge_reason": challenge.reason,
        }
        if challenge.challenge_sustained:
            update["published_status"] = RequirementVerdictStatus.UNCLEAR
            if challenge.missing_or_asserted_evidence:
                update["challenge_reason"] = (
                    f"{challenge.reason} Fehlend oder nur behauptet: "
                    + "; ".join(challenge.missing_or_asserted_evidence)
                )
        return verdict.model_copy(update=update)


def _split_by_applicability(
    requirements: list[Requirement], document_set: DocumentSet
) -> tuple[list[Requirement], list[Requirement]]:
    applicable: list[Requirement] = []
    inapplicable: list[Requirement] = []
    for requirement in sorted(requirements, key=lambda r: r.requirement_id):
        matches = (
            document_set.declared_document_type in requirement.applies_to_document_types
            and document_set.declared_process_area in requirement.applies_to_process_areas
        )
        (applicable if matches else inapplicable).append(requirement)
    return applicable, inapplicable


def _grouped(requirements: list[Requirement], size: int) -> list[list[Requirement]]:
    return [requirements[i : i + size] for i in range(0, len(requirements), size)]


def _chunk_payload(
    chunks: list[DocumentChunk], repository: InMemoryDocumentRepository
) -> list[dict[str, Any]]:
    payload = []
    for chunk in chunks:
        document = repository.get_document(chunk.document_id)
        payload.append(
            {
                "document_id": chunk.document_id,
                "document_name": document.filename if document else "",
                "chunk_id": chunk.chunk_id,
                "page": chunk.page_start,
                "text": chunk.text[:MAX_CHUNK_CHARS],
            }
        )
    return payload


def _check_provenance(
    requirement: Requirement,
    verdict: RequirementVerdict,
    chunks: list[DocumentChunk],
) -> VerifiedRequirementVerdict:
    """Keep only quotes that verifiably appear in their cited chunk.

    A VIOLATED or FULFILLED verdict that loses all its evidence is published
    as UNCLEAR: the model's conclusion may be right, but a verdict the pack
    cannot ground in a checkable quote must not read as settled.
    """
    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}
    surviving: list[RequirementReviewEvidence] = []
    dropped = 0
    for item in verdict.evidence:
        chunk = chunks_by_id.get(item.chunk_id)
        if chunk is None or chunk.document_id != item.document_id:
            dropped += 1
            continue
        if _normalize(item.quote) not in _normalize(chunk.text):
            dropped += 1
            continue
        if not chunk.page_start <= item.page <= chunk.page_end:
            dropped += 1
            continue
        surviving.append(item)

    needs_evidence = verdict.status in {
        RequirementVerdictStatus.VIOLATED,
        RequirementVerdictStatus.FULFILLED,
    }
    provenance_ok = dropped == 0 and (bool(surviving) or not needs_evidence)
    published_status = verdict.status
    if needs_evidence and not surviving:
        published_status = RequirementVerdictStatus.UNCLEAR
    if (
        verdict.status == RequirementVerdictStatus.FULFILLED
        and verdict.evidence_sufficiency == EvidenceSufficiency.INSUFFICIENT
    ):
        # The prompt says an insufficient fulfilled is no fulfilled; enforce it
        # server-side too, so a model that fills the field honestly but keeps
        # the status cannot publish a clean row on evidence it itself rates
        # inadequate.
        published_status = RequirementVerdictStatus.UNCLEAR
    return VerifiedRequirementVerdict(
        requirement_id=requirement.requirement_id,
        requirement_title=requirement.title,
        requirement_text=requirement.requirement_text,
        source_name=requirement.source_name,
        section=requirement.section,
        model_status=verdict.status,
        published_status=published_status,
        severity=verdict.severity,
        rationale=verdict.rationale,
        evidence=surviving,
        dropped_evidence_count=dropped,
        provenance_ok=provenance_ok,
        evidence_type=verdict.evidence_type,
        evidence_reference=verdict.evidence_reference,
        evidence_sufficiency=verdict.evidence_sufficiency,
        independent_support=verdict.independent_support,
    )


def _server_verdict(
    requirement: Requirement,
    *,
    status: RequirementVerdictStatus,
    rationale: str,
) -> VerifiedRequirementVerdict:
    severity = None
    if status == RequirementVerdictStatus.UNCLEAR:
        severity = (
            Severity.HIGH
            if requirement.criticality.value in {"critical", "high"}
            else Severity.MEDIUM
        )
    return VerifiedRequirementVerdict(
        requirement_id=requirement.requirement_id,
        requirement_title=requirement.title,
        requirement_text=requirement.requirement_text,
        source_name=requirement.source_name,
        section=requirement.section,
        model_status=status,
        published_status=status,
        severity=severity,
        rationale=rationale,
        evidence=[],
        dropped_evidence_count=0,
        provenance_ok=status == RequirementVerdictStatus.NOT_APPLICABLE,
        server_authored=True,
    )


def _model_call(
    provider: BaseModelProvider,
    *,
    purpose: str,
    requirement_ids: list[str],
    status: str,
    error: Exception | None = None,
) -> RequirementReviewModelCall:
    metadata = provider.last_run_metadata if status == "succeeded" else None
    token_usage = metadata.token_usage if metadata else None
    return RequirementReviewModelCall(
        purpose=purpose,
        provider=provider.provider_name,
        model_id=provider.configured_model_id,
        requirement_ids=requirement_ids,
        status=status,
        error_type=type(error).__name__ if error else None,
        error_summary=_safe_error_summary(error) if error else None,
        input_tokens=token_usage.input_tokens if token_usage else 0,
        output_tokens=token_usage.output_tokens if token_usage else 0,
    )


def _safe_error_summary(error: Exception) -> str:
    """Class-name-first summary; provider payloads never belong in reports."""
    text = str(error)
    return text[:200] if text else type(error).__name__


def _normalize(value: str) -> str:
    return " ".join(
        value.replace("**", "").replace("__", "").replace("`", "").lower().split()
    )


def default_requirement_review_engine(
    *,
    repository: InMemoryDocumentRepository,
    audit_log: InMemoryAuditLog,
) -> RequirementReviewEngine:
    settings = get_settings()
    if not settings.external_model_calls_enabled:
        mock = MockProvider(output_factory=_mock_assessor_output)
        return RequirementReviewEngine(
            repository=repository,
            audit_log=audit_log,
            assessor_provider=mock,
            entailment_provider=MockProvider(output_factory=_mock_entailment_output),
        )
    runtime_options = _runtime_options(settings)
    return RequirementReviewEngine(
        repository=repository,
        audit_log=audit_log,
        assessor_provider=_provider(
            settings.requirement_review_assessor_provider, settings, runtime_options
        ),
        entailment_provider=_provider(
            settings.requirement_review_entailment_provider, settings, runtime_options
        ),
    )


def _provider(
    name: str, settings: Settings, runtime_options: ProviderRuntimeOptions
) -> BaseModelProvider:
    if name == "anthropic":
        return AnthropicProvider(
            configured_model_id=settings.anthropic_model_id,
            runtime_options=runtime_options,
        )
    if name == "openai":
        return OpenAIProvider(
            configured_model_id=settings.openai_model_id,
            runtime_options=runtime_options,
        )
    if name == "mistral":
        return MistralProvider(
            configured_model_id=settings.mistral_model_id,
            runtime_options=runtime_options,
        )
    return MockProvider(output_factory=_mock_assessor_output)


def _runtime_options(settings: Settings) -> ProviderRuntimeOptions:
    # Same knobs as the finding path, via the same settings, so operational
    # tuning (retries, breaker, timeouts) applies to both engines at once.
    from app.services.review_orchestrator import _runtime_options_from_settings

    return _runtime_options_from_settings(settings)


def _mock_assessor_output(
    prompt: str, input_schema: dict[str, Any], output_schema: type
) -> dict[str, Any]:
    """Deterministic offline assessor: violated iff a red-flag term appears.

    Exercises the full plumbing (evidence provenance included, because the
    quote is a real chunk line) without any network call.
    """
    verdicts = []
    chunks = input_schema.get("chunks", [])
    for requirement in input_schema.get("requirements", []):
        flags = [
            flag.lower()
            for flag in requirement.get("required_evidence", [])
            if isinstance(flag, str)
        ]
        hit = None
        for chunk in chunks:
            text = str(chunk.get("text", ""))
            for line in text.splitlines():
                if any(flag and flag in line.lower() for flag in flags):
                    hit = (chunk, line.strip())
                    break
            if hit:
                break
        if hit is None:
            verdicts.append(
                {
                    "requirement_id": requirement["requirement_id"],
                    "status": "unclear",
                    "severity": "medium",
                    "rationale": (
                        "Mock-Assessor: kein geforderter Nachweis in den "
                        "Auszügen gefunden."
                    ),
                    "evidence": [],
                }
            )
            continue
        chunk, line = hit
        verdicts.append(
            {
                "requirement_id": requirement["requirement_id"],
                "status": "fulfilled",
                "severity": None,
                "rationale": "Mock-Assessor: geforderter Nachweis gefunden.",
                "evidence": [
                    {
                        "document_id": chunk["document_id"],
                        "chunk_id": chunk["chunk_id"],
                        "page": chunk["page"],
                        "quote": line,
                    }
                ],
                "evidence_type": "Dokumentauszug",
                "evidence_reference": chunk["chunk_id"],
                "evidence_sufficiency": "sufficient",
                "independent_support": False,
            }
        )
    return {"verdicts": verdicts}


def _mock_entailment_output(
    prompt: str, input_schema: dict[str, Any], output_schema: type
) -> dict[str, Any]:
    if getattr(output_schema, "__name__", "") == "FulfilledChallenge":
        return {
            "challenge_sustained": False,
            "missing_or_asserted_evidence": [],
            "reason": "Mock-Zweitprüfung: keine Lücke konstruiert.",
        }
    return {"support": "supports", "reason": "Mock-Entailment: akzeptiert."}
