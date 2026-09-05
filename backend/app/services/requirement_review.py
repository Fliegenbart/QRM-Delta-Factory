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

import copy
import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from typing import Any

from app.agents.providers import (
    AnthropicProvider,
    BaseModelProvider,
    HetznerProvider,
    MockProvider,
    OpenAIProvider,
    ProviderRuntimeOptions,
    ProviderStructuredOutputError,
)
from app.agents.providers.hetzner_provider import hetzner_runtime_options
from app.audit.events import InMemoryAuditLog
from app.core.config import Settings, get_settings
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import DocumentChunk, DocumentSet, Requirement, Severity
from app.schemas.structured_evidence import ValidatorFinding
from app.schemas.requirement_review import (
    EntailmentCheck,
    EntailmentSupport,
    EvidenceLocation,
    EvidenceSufficiency,
    FulfilledChallenge,
    NarrowVerdict,
    RequirementApplicability,
    RequirementCoverageReport,
    RequirementGroupOutput,
    RequirementReviewEvidence,
    RequirementReviewModelCall,
    RequirementVerdict,
    RequirementVerdictStatus,
    VerifiedRequirementVerdict,
)

# The quote-reconciliation machinery is deliberately shared with the finding
# path rather than reimplemented: both engines must resolve model quotes to
# exact source spans by the same rules, or their evidence trails drift apart.
from app.services.review_orchestrator import _matching_source_quote

ENGINE_VERSION = "requirement-review-v0.2"  # v0.2: quote second chance (2026-08-23)

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

#: The narrow assessor's prompts. Written for a model that follows short,
#: concrete instructions and loses the thread in long rule lists: one
#: requirement, one question, one flat answer. Status semantics are spelled
#: out because an undefined enum produced a not_applicable under a rationale
#: that said "violated" in the first live probe.
LOCATE_PROMPT = (
    "Du bist ein pharmazeutischer QA-Reviewer. Du erhältst GENAU EINE "
    "Anforderung und die Dokumentauszüge (chunks) eines GMP-Vorgangs.\n\n"
    "Aufgabe: Finde jede Stelle, die für diese Anforderung relevant ist -- "
    "sowohl Stellen, die ihre Erfüllung belegen, als auch Stellen, die einen "
    "Verstoß belegen oder den Vorgang zeigen, der die Pflicht auslöst.\n\n"
    "Regeln:\n"
    "- quote muss WÖRTLICH und zusammenhängend aus dem genannten Chunk "
    "kopiert sein, unverändert, ohne Auslassungen. Lieber ein kurzes exaktes "
    "Zitat als ein langes ungenaues.\n"
    "- chunk_id exakt aus den Eingaben übernehmen.\n"
    "- Höchstens fünf Zitate; die aussagekräftigsten zuerst.\n"
    "- applicability: applies, wenn der Vorgang diese Pflicht auslöst; "
    "does_not_apply, wenn die Anforderung diesen Vorgang erkennbar nicht "
    "betrifft; cannot_tell, wenn die Auszüge das nicht hergeben.\n"
    "- reason: ein Satz auf Deutsch mit korrekten Umlauten ä, ö, ü, ß."
)

JUDGE_PROMPT = (
    "Du bist ein pharmazeutischer QA-Reviewer. Du erhältst GENAU EINE "
    "Anforderung, die dafür gefundenen wörtlichen Zitate (quotes, nummeriert "
    "ab 0) und den vollständigen Text der Chunks, aus denen sie stammen.\n\n"
    "Beurteile die Anforderung:\n"
    "- fulfilled: Die Zitate belegen die Erfüllung.\n"
    "- violated: Die Zitate belegen einen Verstoß, ODER sie belegen den "
    "auslösenden Vorgang, während der geforderte Nachweis in den Auszügen "
    "fehlt.\n"
    "- unclear: Die Auszüge reichen für keine der beiden Aussagen.\n"
    "- not_applicable: Die Anforderung betrifft diesen Vorgang erkennbar "
    "nicht.\n\n"
    "Regeln:\n"
    "- supporting_quote_indices: die Nummern der Zitate, die dein Urteil "
    "tragen. Für fulfilled und violated ist mindestens eine Nummer Pflicht; "
    "bei einem fehlenden Nachweis nenne das Zitat, das den Auslöser belegt.\n"
    "- severity nur bei violated oder unclear: critical, high, medium, low "
    "oder informational.\n"
    "- rationale auf Deutsch mit korrekten Umlauten ä, ö, ü, ß; niemals ae, "
    "oe, ue, ss.\n"
    "- Sei konservativ: Ein möglicher schwerer Verstoß, der nicht widerlegt "
    "ist, ist violated oder unclear, nie stillschweigend fulfilled.\n"
    "- Eine nachträgliche Behauptung 'durchgeführt, keine Auffälligkeiten' "
    "belegt keine Durchführung. Dafür braucht es Primärevidenz: Auszug, "
    "Checkliste, Rohdaten, signierte zeitnahe Dokumentation.\n"
    "- Ein leeres Pflichtfeld ist ein Befund. Vergleiche Messwerte einzeln "
    "mit ihren Grenzen.\n\n"
    "Nur bei fulfilled (sonst null): evidence_type (Art des Nachweises), "
    "evidence_reference (wo er steht), evidence_sufficiency (sufficient, "
    "partial, insufficient), independent_support (true nur, wenn der Nachweis "
    "über die Selbstauskunft des geprüften Dokuments hinausgeht). Ein "
    "fulfilled mit insufficient ist keins: dann unclear."
)

LOCATE_REASK_NOTE = (
    "\n\nHINWEIS ZUR WIEDERHOLUNG: Die vorige Antwort hat eine relevante Stelle "
    "beschrieben, aber nicht zitiert. Beschreibungen zählen nicht. Kopiere die "
    "Stelle(n), die du meinst, WÖRTLICH in quotes, jede mit ihrer chunk_id. "
    "Gibt es wirklich keine relevante Stelle, lass quotes leer und setze "
    "applicability auf does_not_apply oder cannot_tell."
)

JUDGE_REASK_NOTE = (
    "\n\nHINWEIS ZUR WIEDERHOLUNG: Die vorige Antwort war fulfilled oder "
    "violated ohne eine einzige Zitatnummer in supporting_quote_indices. "
    "Nenne die Nummern der tragenden Zitate. Trägt kein Zitat das Urteil, "
    "ist der Status unclear."
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


class RequirementReviewReportNotFoundError(Exception):
    pass


class RequirementReviewEngine:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
        assessor_provider: BaseModelProvider,
        entailment_provider: BaseModelProvider,
        extraction_provider: BaseModelProvider | None = None,
        group_size: int = REQUIREMENT_GROUP_SIZE,
        assessor_samples: int = 2,
        assessor_mode: str = "grouped",
        locate_chunk_limit: int = 12,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.assessor_provider = assessor_provider
        self.entailment_provider = entailment_provider
        #: None disables the structured-evidence/validator layer entirely.
        self.extraction_provider = extraction_provider
        self.group_size = max(1, group_size)
        #: Independent assessor samples per group, merged by alarm-side
        #: precedence. Two by default; one restores single-sample behaviour.
        self.assessor_samples = max(1, assessor_samples)
        #: "grouped": six requirements per call with all chunks and the whole
        #: rulebook -- the shape a frontier model handles. "narrow": per
        #: requirement, locate the evidence first, then judge over those quotes
        #: alone -- the shape a local 27B model handles. See _assess_narrow.
        self.assessor_mode = assessor_mode
        #: How many chunks the locator sees per requirement. Every requirement
        #: used to get every chunk -- 26 copies of the whole case per case,
        #: 1.67M tokens for ten small cases. Fine on a rented endpoint, the
        #: bottleneck on a customer's own GPU. See _candidate_chunks.
        self.locate_chunk_limit = max(1, locate_chunk_limit)

    def run(
        self,
        document_set_id: str,
        *,
        progress: Callable[[str], None] | None = None,
    ) -> RequirementCoverageReport:
        # A run on a local model takes 20-30 minutes; the reviewer waiting on
        # it gets told where it is. Reporting never affects the result.
        tell = progress or (lambda _detail: None)
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
        assessed, assess_calls = self._assess(applicable, chunk_payload, chunks, tell)
        verdicts.extend(assessed)
        model_calls.extend(assess_calls)

        verdicts, check_calls = self._verify_all(verdicts, requirements, tell)
        model_calls.extend(check_calls)

        validator_findings: list[dict[str, Any]] = []
        extracted_evidence: dict[str, Any] | None = None
        tell("Fakten werden erfasst und Regeln geprüft")
        if self.extraction_provider is not None:
            verdicts, validator_findings, extracted_evidence = self._apply_validators(
                verdicts=verdicts,
                applicable=applicable,
                chunk_payload=chunk_payload,
                chunks=chunks,
                model_calls=model_calls,
                document_set=document_set,
            )
        # Arithmetic runs on chunk text and needs no extraction, so it must not
        # sit behind the extraction provider: surviving a truncated extraction
        # is the reason it reads raw text in the first place.
        verdicts, arithmetic_findings = _apply_arithmetic_validators(
            verdicts=verdicts,
            applicable=applicable,
            chunks=chunks,
        )
        validator_findings = [*validator_findings, *arithmetic_findings]

        verdicts.sort(key=lambda v: v.requirement_id)
        _name_cited_documents(verdicts, self.repository)
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
            validator_findings=validator_findings,
            extracted_evidence=extracted_evidence,
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

    def _verify_all(
        self,
        verdicts: list[VerifiedRequirementVerdict],
        requirements: list[Requirement],
        tell: Callable[[str], None],
    ) -> tuple[list[VerifiedRequirementVerdict], list[RequirementReviewModelCall]]:
        """Entailment-check every verdict and challenge the fulfilled ones.

        The checks are per verdict and independent; same pool discipline as
        the narrow assessor, with a provider copy per task.
        """
        criticality_by_id = {
            requirement.requirement_id: requirement.criticality.value
            for requirement in requirements
        }
        workers = max(1, self.entailment_provider.runtime_options.max_concurrent_calls)

        def _check(
            verdict: VerifiedRequirementVerdict,
        ) -> tuple[VerifiedRequirementVerdict, list[RequirementReviewModelCall]]:
            provider = copy.copy(self.entailment_provider)
            local_calls: list[RequirementReviewModelCall] = []
            checked = self._verify_entailment(verdict, local_calls, provider=provider)
            checked = self._challenge_fulfilled(
                checked,
                local_calls,
                criticality=criticality_by_id.get(verdict.requirement_id, "medium"),
                provider=provider,
            )
            return checked, local_calls

        tell(f"Urteile werden nachgeprüft (0 von {len(verdicts)})")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            check_futures = [pool.submit(_check, verdict) for verdict in verdicts]
            for done, _future in enumerate(as_completed(check_futures), start=1):
                tell(f"Urteile werden nachgeprüft ({done} von {len(verdicts)})")
            checked_results = [future.result() for future in check_futures]
        model_calls: list[RequirementReviewModelCall] = []
        for _, local_calls in checked_results:
            model_calls.extend(local_calls)
        return [checked for checked, _ in checked_results], model_calls

    def _assess(
        self,
        applicable: list[Requirement],
        chunk_payload: list[dict[str, Any]],
        chunks: list[DocumentChunk],
        tell: Callable[[str], None],
        *,
        phrase: str = "Anforderung {done} von {total} beurteilt",
    ) -> tuple[list[VerifiedRequirementVerdict], list[RequirementReviewModelCall]]:
        """Judge the given requirements in the configured assessor shape."""
        total = len(applicable)
        verdicts: list[VerifiedRequirementVerdict] = []
        model_calls: list[RequirementReviewModelCall] = []
        if self.assessor_mode == "narrow":
            # Requirements are independent of one another, so they run on a
            # small pool. Each worker gets its own shallow copy of the provider:
            # breaker state and the per-provider semaphore are class-level and
            # locked, but last_run_metadata -- which the call record reads --
            # is per instance, and two workers sharing one instance would book
            # each other's tokens. The semaphore still bounds real concurrent
            # HTTP calls at max_concurrent_calls, so this is ordering, not load.
            workers = max(1, self.assessor_provider.runtime_options.max_concurrent_calls)
            tell(phrase.format(done=0, total=total))
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [
                    pool.submit(
                        self._assess_narrow,
                        requirement=requirement,
                        chunk_payload=chunk_payload,
                        chunks=chunks,
                        provider=copy.copy(self.assessor_provider),
                    )
                    for requirement in applicable
                ]
                for done, _future in enumerate(as_completed(futures), start=1):
                    tell(phrase.format(done=done, total=total))
                # Collected in submission order: the report's call list stays
                # deterministic regardless of which worker finished first.
                results = [future.result() for future in futures]
            for verdict, calls in results:
                verdicts.append(verdict)
                model_calls.extend(calls)
        else:
            done = 0
            for group in _grouped(applicable, self.group_size):
                group_verdicts, group_calls = self._assess_group(
                    group=group, chunk_payload=chunk_payload, chunks=chunks
                )
                verdicts.extend(group_verdicts)
                model_calls.extend(group_calls)
                done += len(group)
                tell(phrase.format(done=done, total=total))
        return verdicts, model_calls

    def rerun_failed(
        self,
        document_set_id: str,
        *,
        progress: Callable[[str], None] | None = None,
    ) -> RequirementCoverageReport:
        """Re-judge only the rows a failed model call left as placeholders.

        The report's other rows, its extracted facts and its rule findings are
        untouched: the facts did not change, and a rule that fired still
        fires. The fresh verdicts go through the same verification and the
        same rule escalation as in a full run, so a retried row is held to
        exactly the standard of a first-run row.
        """
        tell = progress or (lambda _detail: None)
        report = self.repository.get_requirement_report(document_set_id)
        if report is None:
            raise RequirementReviewReportNotFoundError(
                f"No requirement report for DocumentSet {document_set_id}"
            )
        failed_ids = [v.requirement_id for v in report.verdicts if v.needs_retry]
        if not failed_ids:
            return report
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise RequirementReviewDocumentSetNotFoundError(
                f"DocumentSet {document_set_id} not found"
            )
        chunks = self.repository.list_chunks_for_document_set(document_set_id)
        requirement_set = self.repository.get_requirement_set(
            document_set.requirement_set_id
        )
        requirements = [
            requirement
            for requirement in (requirement_set.requirements if requirement_set else [])
            if requirement.requirement_id in set(failed_ids)
        ]
        applicable, _inapplicable = _split_by_applicability(requirements, document_set)
        chunk_payload = _chunk_payload(chunks, self.repository)

        fresh, model_calls = self._assess(
            applicable,
            chunk_payload,
            chunks,
            tell,
            phrase="Erneute Prüfung: Anforderung {done} von {total} beurteilt",
        )
        fresh, check_calls = self._verify_all(fresh, applicable, tell)
        model_calls.extend(check_calls)

        stored_findings = [
            ValidatorFinding.model_validate(finding) for finding in report.validator_findings
        ]
        applicable_ids = {requirement.requirement_id for requirement in applicable}
        fresh = _escalate_with_findings(fresh, stored_findings, applicable_ids)
        fresh, _arithmetic = _apply_arithmetic_validators(
            verdicts=fresh, applicable=applicable, chunks=chunks
        )
        _name_cited_documents(fresh, self.repository)

        fresh_by_id = {verdict.requirement_id: verdict for verdict in fresh}
        verdicts = [fresh_by_id.get(v.requirement_id, v) for v in report.verdicts]
        all_calls = [*report.model_calls, *model_calls]
        status_counts: dict[str, int] = {}
        for verdict in verdicts:
            status_counts[verdict.published_status.value] = (
                status_counts.get(verdict.published_status.value, 0) + 1
            )
        updated = report.model_copy(
            update={
                "created_at": datetime.now(UTC),
                "verdicts": verdicts,
                "status_counts": status_counts,
                "model_calls": all_calls,
                "failed_model_call_count": sum(
                    1 for call in all_calls if call.status != "succeeded"
                ),
            }
        )
        self.repository.replace_requirement_report(
            document_set_id=document_set_id, report=updated
        )
        self.audit_log.append(
            event_type="requirement_review_retried",
            actor_id="service_requirement_review",
            actor_type="service",
            entity_type="DocumentSet",
            entity_id=document_set_id,
            payload={
                "retried_requirement_ids": sorted(applicable_ids),
                "still_failed": sorted(
                    v.requirement_id for v in fresh if v.needs_retry
                ),
                **updated.summary(),
            },
        )
        return updated

    def _apply_validators(
        self,
        *,
        verdicts: list[VerifiedRequirementVerdict],
        applicable: list[Requirement],
        chunk_payload: list[dict[str, Any]],
        chunks: list[DocumentChunk],
        model_calls: list[RequirementReviewModelCall],
        document_set: DocumentSet,
    ) -> tuple[list[VerifiedRequirementVerdict], list[dict[str, Any]], dict[str, Any]]:
        """Run structured extraction plus deterministic checks, then merge.

        Deterministic evidence of a breach overrides a model all-clear: this is
        the one path that raises a verdict instead of lowering it, and it is
        reserved for arithmetic over rows whose quotes were grounded against
        the stored chunks. Extraction failure is recorded and skipped -- the
        validators are additive, and a dead extraction call must not take the
        assessed verdicts down with it.
        """
        from app.services.deterministic_validators import ValidationContext, run_validators
        from app.services.evidence_extraction import EvidenceExtractor

        requirement_index = [
            {
                "requirement_id": requirement.requirement_id,
                "title": requirement.title or "",
                "requirement_text": requirement.requirement_text,
            }
            for requirement in applicable
        ]
        assert self.extraction_provider is not None
        outcome = EvidenceExtractor(provider=self.extraction_provider).extract(
            chunk_payload=chunk_payload,
            requirement_index=requirement_index,
            chunks=chunks,
        )
        for document_id in outcome.succeeded_document_ids:
            model_calls.append(
                _model_call(
                    self.extraction_provider,
                    purpose=f"extract[{document_id}]",
                    requirement_ids=[r.requirement_id for r in applicable],
                    status="succeeded",
                )
            )
        for document_id, error in outcome.failures:
            model_calls.append(
                _model_call(
                    self.extraction_provider,
                    purpose=f"extract[{document_id}]",
                    requirement_ids=[r.requirement_id for r in applicable],
                    status="failed",
                    error=error,
                )
            )

        findings = run_validators(
            outcome.evidence,
            ValidationContext(
                declared_document_type=document_set.declared_document_type,
                chunk_texts=tuple(chunk.text for chunk in chunks),
            ),
        )
        applicable_ids = {requirement.requirement_id for requirement in applicable}
        merged = _escalate_with_findings(verdicts, findings, applicable_ids)
        return (
            merged,
            [finding.model_dump(mode="json") for finding in findings],
            outcome.report_payload(),
        )

    def _insist_on_quotes(
        self,
        output: RequirementGroupOutput,
        input_schema: dict[str, Any],
        *,
        discarded_usage: list[Any],
    ) -> RequirementGroupOutput:
        """Give a sample that decided without quoting one explicit second chance.

        A fulfilled or violated verdict with no evidence is schema-valid, and
        downstream it is demoted to UNCLEAR because there is nothing to check.
        The 2026-08-22 Hetzner ablation lost 154 of 280 verdicts that way --
        136 of them VIOLATED with a sound rationale and no quote -- without a
        single re-ask, because the prompt's quote obligation was never enforced.

        Enforcing it in the schema was tried and was worse: a model that still
        refused on the re-ask failed the whole group, discarding the verdicts
        that did quote. So the obligation lives here. One more ask, naming the
        breach; then keep whichever answer left fewer decided verdicts without
        a quote, and let the usual provenance demotion handle the rest, verdict
        by verdict. A group is never lost to this rule.
        """
        missing = _decided_without_quote(output)
        if not missing:
            return output
        # Both answers were paid for; the call record carries the kept one via
        # the provider's last_run_metadata and the other via discarded_usage.
        first_metadata = self.assessor_provider.last_run_metadata
        first_usage = first_metadata.token_usage if first_metadata else None
        try:
            raw = self.assessor_provider.run_structured(
                ASSESSOR_PROMPT + REASK_CONTRACT_NOTE, input_schema, RequirementGroupOutput
            )
            second = RequirementGroupOutput.model_validate(
                {"verdicts": raw.get("verdicts", [])}
            )
        except ProviderStructuredOutputError:
            return self._keep_first(output, first_metadata, discarded_usage)
        if len(_decided_without_quote(second)) < len(missing):
            if first_usage:
                discarded_usage.append(first_usage)
            return second
        return self._keep_first(output, first_metadata, discarded_usage)

    def _keep_first(
        self,
        output: RequirementGroupOutput,
        first_metadata: Any,
        discarded_usage: list[Any],
    ) -> RequirementGroupOutput:
        # The call record reads the kept call's spend from last_run_metadata,
        # which the second ask has just overwritten. Put the first call's
        # metadata back and book the second as discarded, so neither is lost
        # nor counted twice.
        second_metadata = self.assessor_provider.last_run_metadata
        if second_metadata and second_metadata.token_usage:
            discarded_usage.append(second_metadata.token_usage)
        self.assessor_provider.last_run_metadata = first_metadata
        return output

    def _assess_group(
        self,
        *,
        group: list[Requirement],
        chunk_payload: list[dict[str, Any]],
        chunks: list[DocumentChunk],
    ) -> tuple[list[VerifiedRequirementVerdict], list[RequirementReviewModelCall]]:
        """Sample the assessor N times and merge by conservative precedence.

        Nine of thirty-four errors flipped between two runs on identical
        inputs -- the assessor's judgment is broader than any single sample of
        it (the union of two runs stood at 30 of 34 against 25 and 26 alone).
        Sampling twice and taking the alarm-side union buys that breadth: a
        violation seen by either sample becomes a candidate, and the existing
        provenance, entailment and challenge gates keep the standard of proof
        exactly where it was. The second sample sees the same content with
        requirements and chunks in reverse order, because providers pinned to
        temperature 0 tend to repeat themselves verbatim on identical input.
        """
        requirement_ids = [requirement.requirement_id for requirement in group]
        requirement_payload = [
            {
                "requirement_id": requirement.requirement_id,
                "title": requirement.title,
                "requirement_text": requirement.requirement_text,
                "required_evidence": requirement.required_evidence,
                "criticality": requirement.criticality.value,
            }
            for requirement in group
        ]
        samples: list[dict[str, RequirementVerdict]] = []
        calls: list[RequirementReviewModelCall] = []
        for sample_index in range(max(1, self.assessor_samples)):
            reverse = sample_index % 2 == 1
            input_schema = {
                "requirements": list(reversed(requirement_payload))
                if reverse
                else requirement_payload,
                "chunks": list(reversed(chunk_payload)) if reverse else chunk_payload,
            }
            discarded_usage: list[Any] = []
            try:
                raw = _run_with_one_reask(
                    self.assessor_provider,
                    ASSESSOR_PROMPT,
                    input_schema,
                    RequirementGroupOutput,
                    discarded_usage=discarded_usage,
                )
                output = RequirementGroupOutput.model_validate(
                    {"verdicts": raw.get("verdicts", [])}
                )
                output = self._insist_on_quotes(
                    output, input_schema, discarded_usage=discarded_usage
                )
            except Exception as exc:  # noqa: BLE001 - fail-secure per sample
                calls.append(
                    _model_call(
                        self.assessor_provider,
                        purpose="assess",
                        requirement_ids=requirement_ids,
                        status="failed",
                        error=exc,
                        discarded_usage=discarded_usage,
                    )
                )
                continue
            samples.append(
                {verdict.requirement_id: verdict for verdict in output.verdicts}
            )
            calls.append(
                _model_call(
                    self.assessor_provider,
                    purpose="assess",
                    requirement_ids=requirement_ids,
                    status="succeeded",
                    discarded_usage=discarded_usage,
                )
            )

        if not samples:
            return [
                _server_verdict(
                    requirement,
                    status=RequirementVerdictStatus.UNCLEAR,
                    rationale=(
                        "Modelllauf für diese Anforderungsgruppe fehlgeschlagen; "
                        "die Anforderung bleibt unbeurteilt und gehört zur "
                        "menschlichen Prüfung."
                    ),
                    needs_retry=True,
                )
                for requirement in group
            ], calls

        verified = []
        for requirement in group:
            candidates = [
                sample[requirement.requirement_id]
                for sample in samples
                if requirement.requirement_id in sample
            ]
            if not candidates:
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
            merged, disagreement = _merge_sample_verdicts(candidates)
            checked = _check_provenance(requirement, merged, chunks)
            if disagreement:
                checked = checked.model_copy(update={"sample_disagreement": True})
            verified.append(checked)
        return verified, calls

    def _assess_narrow(
        self,
        *,
        requirement: Requirement,
        chunk_payload: list[dict[str, Any]],
        chunks: list[DocumentChunk],
        provider: BaseModelProvider | None = None,
    ) -> tuple[VerifiedRequirementVerdict, list[RequirementReviewModelCall]]:
        """Two small calls per requirement: locate the evidence, then judge it.

        Built for a model that cannot carry the grouped call. On the same
        corpus Qwen3.8-27B scored 12/25 grouped -- it judged acceptably but
        left the evidence list empty in two thirds of its decided verdicts --
        while answering one flat question with a verbatim quote four times out
        of four. So the shape is the probe's: one requirement, all chunks,
        "where is the evidence?" with a flat answer; then the judgment over
        those quotes alone, pointing at them by index. A decided verdict
        cannot exist without a quote because the judge never sees anything
        else, and the model never copies a document id or page number.

        The judge is sampled assessor_samples times over the same quotes
        (reversed on odd samples) and merged by the same alarm-side precedence
        as the grouped path, so the gates downstream see the same shape.
        """
        requirement_payload = {
            "requirement_id": requirement.requirement_id,
            "title": requirement.title,
            "requirement_text": requirement.requirement_text,
            "required_evidence": requirement.required_evidence,
            "criticality": requirement.criticality.value,
        }
        calls: list[RequirementReviewModelCall] = []
        rid = [requirement.requirement_id]
        provider = provider or self.assessor_provider

        # --- call 1: locate -------------------------------------------------
        candidate_chunks = _candidate_chunks(requirement, chunk_payload, self.locate_chunk_limit)
        discarded: list[Any] = []
        try:
            raw = _run_with_one_reask(
                provider,
                LOCATE_PROMPT,
                {"requirement": requirement_payload, "chunks": candidate_chunks},
                EvidenceLocation,
                discarded_usage=discarded,
            )
            location = EvidenceLocation.model_validate(raw)
        except Exception as exc:  # noqa: BLE001 - fail-secure per requirement
            calls.append(
                _model_call(
                    provider,
                    purpose="locate",
                    requirement_ids=rid,
                    status="failed",
                    error=exc,
                    discarded_usage=discarded,
                )
            )
            return (
                _server_verdict(
                    requirement,
                    status=RequirementVerdictStatus.UNCLEAR,
                    rationale=(
                        "Belegsuche für diese Anforderung fehlgeschlagen; sie "
                        "bleibt unbeurteilt und gehört zur menschlichen Prüfung."
                    ),
                    needs_retry=True,
                ),
                calls,
            )
        calls.append(
            _model_call(
                provider,
                purpose="locate",
                requirement_ids=rid,
                status="succeeded",
                discarded_usage=discarded,
            )
        )

        chunk_by_id = {chunk["chunk_id"]: chunk for chunk in chunk_payload}
        located = [q for q in location.quotes if q.chunk_id in chunk_by_id]
        if not located and location.applicability != RequirementApplicability.DOES_NOT_APPLY:
            # The locator described the passage instead of quoting it -- "Die
            # QS-Notiz dokumentiert, dass ..." with an empty list -- on three of
            # the rows behind the two judgment misses of the 2026-08-23 run. It
            # knows where the evidence is; it is told once that descriptions
            # do not count. A second empty answer stands.
            location, located = self._locate_again(
                provider, requirement_payload, candidate_chunks, chunk_by_id, location, calls, rid
            )
        if not located:
            if location.applicability == RequirementApplicability.DOES_NOT_APPLY:
                return (
                    _server_verdict(
                        requirement,
                        status=RequirementVerdictStatus.NOT_APPLICABLE,
                        rationale=f"Laut Belegsuche nicht einschlägig: {location.reason}",
                    ),
                    calls,
                )
            return (
                _server_verdict(
                    requirement,
                    status=RequirementVerdictStatus.UNCLEAR,
                    rationale=(
                        "Keine einschlägige Stelle in den Auszügen gefunden: "
                        f"{location.reason}"
                    ),
                ),
                calls,
            )

        # --- call 2: judge, sampled ----------------------------------------
        context_chunks = [
            chunk_by_id[chunk_id]
            for chunk_id in dict.fromkeys(q.chunk_id for q in located)
        ]
        samples: list[RequirementVerdict] = []
        for sample_index in range(max(1, self.assessor_samples)):
            reverse = sample_index % 2 == 1
            ordered = list(reversed(located)) if reverse else located
            input_schema = {
                "requirement": requirement_payload,
                "quotes": [
                    {"index": i, "chunk_id": q.chunk_id, "quote": q.quote}
                    for i, q in enumerate(ordered)
                ],
                "chunks": list(reversed(context_chunks)) if reverse else context_chunks,
            }
            discarded = []
            try:
                judged = self._judge_once(input_schema, discarded_usage=discarded, provider=provider)
            except Exception as exc:  # noqa: BLE001 - fail-secure per sample
                calls.append(
                    _model_call(
                        provider,
                        purpose="judge",
                        requirement_ids=rid,
                        status="failed",
                        error=exc,
                        discarded_usage=discarded,
                    )
                )
                continue
            calls.append(
                _model_call(
                    provider,
                    purpose="judge",
                    requirement_ids=rid,
                    status="succeeded",
                    discarded_usage=discarded,
                )
            )
            samples.append(_narrow_to_verdict(requirement, judged, ordered, chunk_by_id))

        if not samples:
            return (
                _server_verdict(
                    requirement,
                    status=RequirementVerdictStatus.UNCLEAR,
                    rationale=(
                        "Beurteilung für diese Anforderung fehlgeschlagen; sie "
                        "bleibt unbeurteilt und gehört zur menschlichen Prüfung."
                    ),
                    needs_retry=True,
                ),
                calls,
            )
        merged, disagreement = _merge_sample_verdicts(samples)
        checked = _check_provenance(requirement, merged, chunks)
        if disagreement:
            checked = checked.model_copy(update={"sample_disagreement": True})
        return checked, calls

    def _locate_again(
        self,
        provider: BaseModelProvider,
        requirement_payload: dict[str, Any],
        chunk_payload: list[dict[str, Any]],
        chunk_by_id: dict[str, dict[str, Any]],
        first: EvidenceLocation,
        calls: list[RequirementReviewModelCall],
        rid: list[str],
    ) -> tuple[EvidenceLocation, list[Any]]:
        try:
            raw = provider.run_structured(
                LOCATE_PROMPT + LOCATE_REASK_NOTE,
                {"requirement": requirement_payload, "chunks": chunk_payload},
                EvidenceLocation,
            )
            second = EvidenceLocation.model_validate(raw)
        except Exception as exc:  # noqa: BLE001 - the first answer stands
            calls.append(
                _model_call(provider, purpose="locate", requirement_ids=rid, status="failed", error=exc)
            )
            return first, []
        calls.append(
            _model_call(provider, purpose="locate", requirement_ids=rid, status="succeeded")
        )
        located = [q for q in second.quotes if q.chunk_id in chunk_by_id]
        return (second, located) if located else (first, [])

    def _judge_once(
        self,
        input_schema: dict[str, Any],
        *,
        discarded_usage: list[Any],
        provider: BaseModelProvider | None = None,
    ) -> NarrowVerdict:
        """One judge sample, with one explicit second chance to point at a quote."""
        provider = provider or self.assessor_provider
        raw = _run_with_one_reask(
            provider,
            JUDGE_PROMPT,
            input_schema,
            NarrowVerdict,
            discarded_usage=discarded_usage,
        )
        judged = NarrowVerdict.model_validate(raw)
        if not _decided_without_indices(judged):
            return judged
        first_metadata = provider.last_run_metadata
        try:
            raw = provider.run_structured(
                JUDGE_PROMPT + JUDGE_REASK_NOTE, input_schema, NarrowVerdict
            )
            second = NarrowVerdict.model_validate(raw)
        except ProviderStructuredOutputError:
            second = None
        if second is not None and not _decided_without_indices(second):
            if first_metadata and first_metadata.token_usage:
                discarded_usage.append(first_metadata.token_usage)
            return second
        second_metadata = provider.last_run_metadata
        if second_metadata and second_metadata.token_usage:
            discarded_usage.append(second_metadata.token_usage)
        provider.last_run_metadata = first_metadata
        return judged

    def _verify_entailment(
        self,
        verdict: VerifiedRequirementVerdict,
        model_calls: list[RequirementReviewModelCall],
        provider: BaseModelProvider | None = None,
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
        provider = provider or self.entailment_provider
        input_schema = {
            "rationale": verdict.rationale,
            "quotes": [item.quote for item in verdict.evidence],
        }
        try:
            raw = _run_with_one_reask(
                provider, ENTAILMENT_PROMPT, input_schema, EntailmentCheck
            )
            check = EntailmentCheck.model_validate(raw)
        except Exception as exc:  # noqa: BLE001 - fail-secure per verdict
            model_calls.append(
                _model_call(
                    provider,
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
                    "needs_retry": True,
                }
            )
        model_calls.append(
            _model_call(
                provider,
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
        provider: BaseModelProvider | None = None,
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
        provider = provider or self.entailment_provider
        if verdict.independent_support is True:
            # The challenge exists to catch fulfilled-by-self-attestation. Where
            # the assessor already names support beyond the document's own
            # say-so, a second look sustained 17 of 19 objections on the
            # regression corpus -- a rubber stamp in the sceptical direction
            # that would flood a mostly-clean package with precautionary
            # unclear rows. The assessor's independent_support claim is itself
            # checkable later against the named evidence_reference.
            return verdict
        input_schema = {
            "requirement_text": verdict.requirement_text,
            "rationale": verdict.rationale,
            "quotes": [item.quote for item in verdict.evidence],
            "evidence_type": verdict.evidence_type,
            "independent_support": verdict.independent_support,
        }
        try:
            raw = _run_with_one_reask(
                provider, CHALLENGE_PROMPT, input_schema, FulfilledChallenge
            )
            challenge = FulfilledChallenge.model_validate(raw)
        except Exception as exc:  # noqa: BLE001 - fail-secure per verdict
            model_calls.append(
                _model_call(
                    provider,
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
                    "needs_retry": True,
                }
            )
        model_calls.append(
            _model_call(
                provider,
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


#: Alarm-side precedence for merging assessor samples: the merged verdict is
#: the most cautious status any sample produced. A violation seen once is a
#: candidate (the gates still have to sustain it); a fulfilled requires every
#: sample to agree, because an all-clear is the verdict a wrong version of
#: costs the most.
_MERGE_PRECEDENCE = {
    RequirementVerdictStatus.VIOLATED: 0,
    RequirementVerdictStatus.UNCLEAR: 1,
    RequirementVerdictStatus.FULFILLED: 2,
    RequirementVerdictStatus.NOT_APPLICABLE: 3,
}


def _merge_sample_verdicts(
    candidates: list[RequirementVerdict],
) -> tuple[RequirementVerdict, bool]:
    """Pick one verdict from N samples; report whether they disagreed.

    Ties on status prefer the sample with more evidence, so the chosen verdict
    enters provenance checking with the most material to ground.
    """
    chosen = min(
        candidates,
        key=lambda v: (_MERGE_PRECEDENCE.get(v.status, 1), -len(v.evidence)),
    )
    disagreement = len({candidate.status for candidate in candidates}) > 1
    return chosen, disagreement


REASK_CONTRACT_NOTE = (
    "\n\nHINWEIS ZUR WIEDERHOLUNG: Die vorige Antwort hat den Ausgabevertrag "
    "verletzt. Häufigste Ursache: ein Verdict mit status fulfilled oder "
    "violated ohne Zitat. Jedes solche Verdict braucht mindestens einen "
    "evidence-Eintrag mit document_id, chunk_id, page und einem wörtlichen, "
    "zusammenhängenden quote aus genau diesem Chunk. Kannst du keinen Beleg "
    "zitieren, ist der Status unclear."
)


_TERM_RE = re.compile(r"[a-zäöüß0-9][a-zäöüß0-9\-]{2,}")
_STOP_TERMS = frozenset(
    "und oder der die das den dem des ein eine einer eines für mit von zur zum bei auf "
    "aus nach vor über unter durch ist sind wird werden muss müssen soll sollen kann "
    "nicht sein haben hat als auch wie wenn dass nur alle jede jeder jedes sich "
    "the and for with from that this are not".split()
)


def _terms(text: str) -> set[str]:
    """Lower-cased content words, cut to a crude stem so 'Freigabe' meets
    'freigegeben' and 'Validierung' meets 'Validierungsnachweis'."""
    return {
        term[:6]
        for term in _TERM_RE.findall(text.casefold().replace("**", " "))
        if term not in _STOP_TERMS
    }


def _candidate_chunks(
    requirement: Requirement, chunk_payload: list[dict[str, Any]], limit: int
) -> list[dict[str, Any]]:
    """The chunks worth showing the locator for one requirement.

    Lexical overlap between the requirement (title, text, required evidence)
    and each chunk, top ``limit`` in document order. A small case passes
    through untouched -- on the ten-case goldstandard corpus no case has more
    than five chunks, so this changes nothing there and everything on a real
    thirty-page deviation package. Ties and all-zero scores fall back to
    document order, so a requirement whose vocabulary matches nothing still
    sees the first ``limit`` chunks rather than none.
    """
    if len(chunk_payload) <= limit:
        return chunk_payload
    wanted = _terms(
        " ".join([requirement.title or "", requirement.requirement_text, *requirement.required_evidence])
    )
    scored = []
    for index, chunk in enumerate(chunk_payload):
        overlap = len(wanted & _terms(str(chunk.get("text", ""))))
        scored.append((-overlap, index))
    keep = sorted(index for _, index in sorted(scored)[:limit])
    return [chunk_payload[index] for index in keep]


def _decided_without_indices(judged: NarrowVerdict) -> bool:
    return judged.status in (
        RequirementVerdictStatus.FULFILLED,
        RequirementVerdictStatus.VIOLATED,
    ) and not judged.supporting_quote_indices


def _narrow_to_verdict(
    requirement: Requirement,
    judged: NarrowVerdict,
    quotes: list[Any],
    chunk_by_id: dict[str, dict[str, Any]],
) -> RequirementVerdict:
    """Resolve the judge's quote indices back to chunk-addressed evidence.

    Out-of-range indices are ignored rather than failing the verdict; a
    decided verdict that ends up with no evidence is then demoted by the
    provenance check exactly like a grouped verdict would be.
    """
    evidence = []
    seen: set[int] = set()
    for index in judged.supporting_quote_indices:
        if index in seen or not 0 <= index < len(quotes):
            continue
        seen.add(index)
        quote = quotes[index]
        chunk = chunk_by_id[quote.chunk_id]
        evidence.append(
            {
                "document_id": chunk["document_id"],
                "chunk_id": quote.chunk_id,
                "page": chunk["page"],
                "quote": quote.quote,
            }
        )
    return RequirementVerdict(
        requirement_id=requirement.requirement_id,
        status=judged.status,
        severity=judged.severity,
        rationale=judged.rationale,
        evidence=evidence,
        evidence_type=judged.evidence_type,
        evidence_reference=judged.evidence_reference,
        evidence_sufficiency=judged.evidence_sufficiency,
        independent_support=judged.independent_support,
    )


def _decided_without_quote(output: RequirementGroupOutput) -> list[str]:
    """Requirement ids of fulfilled/violated verdicts that cite nothing."""
    return [
        verdict.requirement_id
        for verdict in output.verdicts
        if verdict.status
        in (RequirementVerdictStatus.FULFILLED, RequirementVerdictStatus.VIOLATED)
        and not verdict.evidence
    ]


def _run_with_one_reask(
    provider: BaseModelProvider,
    prompt: str,
    input_schema: dict[str, Any],
    output_schema: type,
    *,
    discarded_usage: list[Any] | None = None,
) -> dict[str, Any]:
    """Re-ask once when a response fails the schema after normalization.

    Transport retries live in the provider; schema failures are explicitly the
    caller's to bound (see base.py). A malformed sample is usually a one-off --
    the blind runs lost two assessor groups and one challenge to single
    responses that were never re-asked. One fresh sample, then fail-secure.

    The discarded first sample was still paid for; its token usage (recorded
    by the provider even on schema failure) is appended to ``discarded_usage``
    so the call record can carry the real spend instead of half of it.
    """
    try:
        return provider.run_structured(prompt, input_schema, output_schema)
    except ProviderStructuredOutputError:
        metadata = provider.last_run_metadata
        if discarded_usage is not None and metadata and metadata.token_usage:
            discarded_usage.append(metadata.token_usage)
        # The second ask is told that the first answer broke the contract.
        # Re-sending an identical prompt mostly reproduces an identical
        # mistake; naming the most common breach gives the model something
        # to correct. The error text itself is deliberately not echoed -- it
        # can carry fragments of the rejected payload.
        return provider.run_structured(
            prompt + REASK_CONTRACT_NOTE, input_schema, output_schema
        )


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


def _name_cited_documents(
    verdicts: list[VerifiedRequirementVerdict], repository: InMemoryDocumentRepository
) -> None:
    """Put the file name next to every surviving quote.

    A citation that reads "Seite 1" is not checkable in a four-document case;
    "document_03_capa_plan.md, Seite 1" is. The id stays for the machines.
    """
    names: dict[str, str] = {}
    for verdict in verdicts:
        for item in verdict.evidence:
            if item.document_id not in names:
                document = repository.get_document(item.document_id)
                names[item.document_id] = document.filename if document else ""
            item.document_name = names[item.document_id]


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


#: Ellipsis markers a model uses when it stitches two passages into one quote.
#: Bracketed forms first: splitting on "..." before "[...]" would leave the
#: brackets behind as unfindable fragment debris.
_ELLIPSIS_MARKERS = ("[...]", "(...)", "[…]", "(…)", "...", "…")


def _check_provenance(
    requirement: Requirement,
    verdict: RequirementVerdict,
    chunks: list[DocumentChunk],
) -> VerifiedRequirementVerdict:
    """Ground every quote in its cited chunk, repairing before rejecting.

    Strict substring matching alone taxed the engine about one evidence-bearing
    verdict in ten: near-miss quotes -- markdown drift, typographic quote
    variants, umlaut transliteration, stitched fragments -- were dropped
    outright, and in the 2026-07-27 regression run five previously-found errors
    demoted to UNCLEAR solely because their quotes lost that lottery. The
    finding path repairs such variants deterministically with its
    quote-reconciliation layer; this uses the same machinery. An ellipsis
    quote is split and each fragment must ground individually, becoming its
    own evidence item -- honest exact spans instead of one unverifiable
    stitch. Repair never invents text: a quote that cannot be resolved to an
    exact source span is still dropped, now with a recorded reason.

    A VIOLATED or FULFILLED verdict that loses all its evidence is published
    as UNCLEAR: the model's conclusion may be right, but a verdict the pack
    cannot ground in a checkable quote must not read as settled.
    """
    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}
    surviving: list[RequirementReviewEvidence] = []
    dropped = 0
    dropped_reasons: list[str] = []
    for item in verdict.evidence:
        chunk = chunks_by_id.get(item.chunk_id)
        if chunk is not None and chunk.document_id != item.document_id:
            # An existing chunk id paired with a different document is the
            # strongest hallucination signal there is -- the model named a real
            # passage and the wrong source for it. Relocating would search the
            # claimed document for the same words and, on boilerplate, find
            # them, publishing a citation into a document the finding was never
            # about. This one keeps failing.
            dropped += 1
            dropped_reasons.append(
                f"Zitat verworfen ({item.chunk_id}): Chunk gehört zu einem "
                f"anderen Dokument als {item.document_id}."
            )
            continue
        if chunk is None:
            # An invented chunk id is bookkeeping drift, not a wrong source: a
            # verdict naming the right document lost both quotes this way and
            # demoted to unclear although it had found its planted error.
            # Relocate within the cited document; the text still has to ground
            # exactly, so provenance is unchanged.
            relocated = _relocate_quote(item, chunks)
            if relocated is None:
                dropped += 1
                dropped_reasons.append(
                    f"Zitat verworfen ({item.chunk_id}): Chunk existiert nicht "
                    f"oder gehört nicht zu {item.document_id}, und der Wortlaut "
                    f"findet sich in keinem Chunk des Dokuments."
                )
                continue
            chunk, grounded_fragments = relocated
            surviving.extend(
                item.model_copy(
                    update={
                        "chunk_id": chunk.chunk_id,
                        "page": chunk.page_start,
                        "quote": fragment,
                    }
                )
                for fragment in grounded_fragments
            )
            continue
        if not chunk.page_start <= item.page <= chunk.page_end:
            dropped += 1
            dropped_reasons.append(
                f"Zitat verworfen ({item.chunk_id}): Seite {item.page} liegt "
                f"außerhalb von {chunk.page_start}-{chunk.page_end}."
            )
            continue
        grounded = _ground_quote(item.quote, chunk.text)
        if grounded is None:
            dropped += 1
            dropped_reasons.append(
                f"Zitat verworfen ({item.chunk_id}): nicht im Chunk auffindbar, "
                f"auch nicht nach Reparatur: „{item.quote[:120]}“"
            )
            continue
        surviving.extend(
            item.model_copy(update={"quote": fragment}) for fragment in grounded
        )

    needs_evidence = verdict.status in {
        RequirementVerdictStatus.VIOLATED,
        RequirementVerdictStatus.FULFILLED,
    }
    provenance_ok = dropped == 0 and (bool(surviving) or not needs_evidence)
    del dropped_reasons[8:]  # cap the report payload; the count stays exact
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
        dropped_evidence_reasons=dropped_reasons,
        provenance_ok=provenance_ok,
        evidence_type=verdict.evidence_type,
        evidence_reference=verdict.evidence_reference,
        evidence_sufficiency=verdict.evidence_sufficiency,
        independent_support=verdict.independent_support,
    )


def _escalate_with_findings(
    verdicts: list[VerifiedRequirementVerdict],
    findings: list[ValidatorFinding],
    applicable_ids: set[str],
) -> list[VerifiedRequirementVerdict]:
    """Let deterministic findings raise the verdicts they are mapped to."""
    verdicts_by_id = {verdict.requirement_id: verdict for verdict in verdicts}
    for finding in findings:
        for requirement_id in finding.requirement_ids:
            verdict = verdicts_by_id.get(requirement_id)
            if verdict is None or requirement_id not in applicable_ids:
                continue
            update: dict[str, Any] = {
                "validator_flags": [*verdict.validator_flags, finding.validator_id],
                "validator_statements": [
                    *verdict.validator_statements,
                    finding.statement,
                ],
                "evidence": _merge_evidence(verdict.evidence, finding.locations),
            }
            if verdict.published_status != RequirementVerdictStatus.VIOLATED:
                update["published_status"] = RequirementVerdictStatus.VIOLATED
                if verdict.severity is None:
                    update["severity"] = Severity(finding.severity)
                # The rule is now the reason the row is violated, so the
                # row must say so. Left alone, a verdict whose model call
                # had failed kept "Beurteilung fehlgeschlagen" as its
                # rationale above a perfectly good rule finding -- the
                # reviewer read a failure, and the eval matcher scored a
                # miss on a breach the system had in fact found.
                update["rationale"] = (
                    finding.statement
                    if verdict.server_authored
                    else f"{finding.statement} {verdict.rationale}"
                )
            verdicts_by_id[requirement_id] = verdict.model_copy(update=update)
    return [verdicts_by_id[v.requirement_id] for v in verdicts]


def _apply_arithmetic_validators(
    *,
    verdicts: list[VerifiedRequirementVerdict],
    applicable: list[Requirement],
    chunks: list[DocumentChunk],
) -> tuple[list[VerifiedRequirementVerdict], list[dict[str, Any]]]:
    """Run the text-level arithmetic checks and annotate co-citing verdicts.

    Deliberately non-escalating. The check knows a document contradicts its own
    arithmetic; it cannot know which obligation that breaches, and a wrong
    escalation would cost the decoy specificity that is the engine's strongest
    measured result. The findings publish as their own rows instead.
    """
    from app.services.arithmetic_validators import run_arithmetic_validators

    findings = run_arithmetic_validators(chunks)
    if not findings:
        return verdicts, []
    applicable_ids = {requirement.requirement_id for requirement in applicable}
    verdicts_by_id = {verdict.requirement_id: verdict for verdict in verdicts}
    for finding in findings:
        finding_chunks = {location.chunk_id for location in finding.locations}
        for verdict in verdicts:
            if verdict.requirement_id not in applicable_ids:
                continue
            current = verdicts_by_id[verdict.requirement_id]
            if not (finding_chunks & {item.chunk_id for item in current.evidence}):
                continue
            verdicts_by_id[verdict.requirement_id] = current.model_copy(
                update={
                    "validator_flags": [*current.validator_flags, finding.validator_id],
                    "validator_statements": [
                        *current.validator_statements,
                        finding.statement,
                    ],
                }
            )
    merged = [verdicts_by_id[verdict.requirement_id] for verdict in verdicts]
    return merged, [finding.model_dump(mode="json") for finding in findings]


def _relocate_quote(
    item: RequirementReviewEvidence, chunks: list[DocumentChunk]
) -> tuple[DocumentChunk, list[str]] | None:
    """Find the cited document's chunk that actually carries the quote.

    Only the chunk id moves; the document the model named stays binding and
    the text must still ground exactly. Two constraints keep this from turning
    a citation into a guess. The page the model gave decides between chunks --
    without it, a sentence appearing twice in a document would relocate to
    whichever copy comes first and the published page would look precise while
    being invented. And a quote that grounds in several chunks with no page to
    choose between them is refused outright rather than resolved arbitrarily.
    """
    matches: list[tuple[DocumentChunk, list[str]]] = []
    for candidate in chunks:
        if candidate.document_id != item.document_id:
            continue
        grounded = _ground_quote(item.quote, candidate.text)
        if grounded is None:
            continue
        if candidate.page_start <= item.page <= candidate.page_end:
            return candidate, grounded
        matches.append((candidate, grounded))
    return matches[0] if len(matches) == 1 else None


#: Latin-1 codepoints this repair is willing to restore. Restricted to German
#: orthography on purpose: the repair must fix an encoding accident, never
#: reconstruct arbitrary characters the model may have meant.
_REPAIRABLE_CODEPOINTS = frozenset("äöüÄÖÜß")

#: Only the two lead bytes actually observed. Accepting every C0 control
#: character would eat the ones documents legitimately contain: U+000C is the
#: page break of PDF-extracted text and U+000D a carriage return, and both have
#: low nibbles that map into the German range -- "\x0c4. Quartal" would become
#: "Ä. Quartal", destroying text that grounds perfectly well on its own.
_MOJIBAKE_LEADS = frozenset("\x0e\x0f")


def _repair_mojibake(value: str) -> str:
    """Undo the control-character umlaut corruption seen in model quotes.

    A quote came back with U+000E followed by "4" where "ä" belonged, and
    U+000F followed by "c" for "ü": the codepoint's high hex nibble had
    become a C0 control character and the low nibble stayed a hex digit.
    The verdict describing that finding lost its only quote at provenance
    and, with it, the blind corpus scored a correct detection as a miss.

    Reversing it is mechanical -- (control & 0x0F) << 4 | int(digit, 16) --
    and safe, because the result still has to match the chunk exactly; the
    chunk text remains the authority for what the evidence says.
    """
    if not any(character in _MOJIBAKE_LEADS for character in value):
        return value
    repaired: list[str] = []
    index = 0
    while index < len(value):
        character = value[index]
        if character in _MOJIBAKE_LEADS and index + 1 < len(value):
            try:
                low = int(value[index + 1], 16)
            except ValueError:
                repaired.append(character)
                index += 1
                continue
            candidate = chr(((ord(character) & 0x0F) << 4) | low)
            if candidate in _REPAIRABLE_CODEPOINTS:
                repaired.append(candidate)
                index += 2
                continue
        repaired.append(character)
        index += 1
    return "".join(repaired)


def _ground_quote(quote: str, chunk_text: str) -> list[str] | None:
    """Resolve a model quote to exact source spans, or refuse.

    Returns the list of exact chunk substrings the quote resolves to: one
    entry for a plain quote, several for an ellipsis-stitched quote whose
    fragments each ground individually. None when any part cannot be found.
    The reconciliation itself is the finding path's: token-sequence matching
    that forgives markdown markers, typographic quote variants, whitespace
    and umlaut transliteration, but never fuzzy-matches content.
    """
    # A quote that is already an exact substring stays as it is.
    if quote in chunk_text:
        return [quote]

    repaired_quote = _repair_mojibake(quote)
    if repaired_quote != quote:
        if repaired_quote in chunk_text:
            return [repaired_quote]
        # The repair is an attempt, not a commitment: if it did not produce a
        # match, the original text goes on to the fragment and reconciliation
        # paths, which treat control characters as separators and may well
        # ground it as it stands.
        repaired = _ground_quote(repaired_quote, chunk_text)
        if repaired is not None:
            return repaired

    fragments = [quote]
    for marker in _ELLIPSIS_MARKERS:
        fragments = [
            piece for fragment in fragments for piece in fragment.split(marker)
        ]
    fragments = [fragment.strip() for fragment in fragments if fragment.strip()]
    if not fragments:
        return None

    grounded: list[str] = []
    for fragment in fragments:
        if fragment in chunk_text:
            grounded.append(fragment)
            continue
        repaired = _matching_source_quote(fragment, chunk_text)
        if repaired is None:
            return None
        # Edge whitespace from span extension is not part of the quote; the
        # stripped text remains an exact chunk substring.
        grounded.append(repaired.strip())
    return grounded


def _merge_evidence(
    existing: list[RequirementReviewEvidence],
    locations: list[Any],
) -> list[RequirementReviewEvidence]:
    merged = list(existing)
    seen = {(item.document_id, item.chunk_id, item.quote) for item in existing}
    for location in locations:
        key = (location.document_id, location.chunk_id, location.quote)
        if key in seen:
            continue
        seen.add(key)
        merged.append(
            RequirementReviewEvidence(
                document_id=location.document_id,
                chunk_id=location.chunk_id,
                page=location.page,
                quote=location.quote,
            )
        )
    return merged


def _server_verdict(
    requirement: Requirement,
    *,
    status: RequirementVerdictStatus,
    rationale: str,
    needs_retry: bool = False,
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
        needs_retry=needs_retry,
    )


def _model_call(
    provider: BaseModelProvider,
    *,
    purpose: str,
    requirement_ids: list[str],
    status: str,
    error: Exception | None = None,
    discarded_usage: list[Any] | None = None,
) -> RequirementReviewModelCall:
    metadata = provider.last_run_metadata if status == "succeeded" else None
    token_usage = metadata.token_usage if metadata else None
    input_tokens = token_usage.input_tokens if token_usage else 0
    output_tokens = token_usage.output_tokens if token_usage else 0
    # Samples discarded by a re-ask were billed all the same; without them the
    # call record understates spend by a full call exactly on the paths that
    # needed a second sample.
    for usage in discarded_usage or []:
        input_tokens += usage.input_tokens
        output_tokens += usage.output_tokens
    return RequirementReviewModelCall(
        purpose=purpose,
        provider=provider.provider_name,
        model_id=provider.configured_model_id,
        requirement_ids=requirement_ids,
        status=status,
        error_type=type(error).__name__ if error else None,
        error_summary=_safe_error_summary(error) if error else None,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
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
            extraction_provider=MockProvider(output_factory=_mock_extraction_output),
            assessor_samples=settings.requirement_review_assessor_samples,
            assessor_mode=settings.requirement_review_assessor_mode,
            locate_chunk_limit=settings.requirement_review_locate_chunk_limit,
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
        # Extraction rides the assessor's provider choice: it is mechanical
        # transcription work, and the cheapest capable model is the right one.
        extraction_provider=_provider(
            settings.requirement_review_assessor_provider, settings, runtime_options
        ),
        assessor_samples=settings.requirement_review_assessor_samples,
        assessor_mode=settings.requirement_review_assessor_mode,
        locate_chunk_limit=settings.requirement_review_locate_chunk_limit,
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
    if name == "hetzner":
        return HetznerProvider(
            configured_model_id=settings.hetzner_model_id,
            endpoint=settings.hetzner_endpoint,
            runtime_options=hetzner_runtime_options(
                runtime_options,
                timeout_seconds=settings.hetzner_model_provider_timeout_seconds,
            ),
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
    quote is a real chunk line) without any network call. Answers the narrow
    path's two schemas with the same heuristic.
    """
    if output_schema is EvidenceLocation:
        requirement = input_schema.get("requirement", {})
        flags = [f.lower() for f in requirement.get("required_evidence", []) if isinstance(f, str)]
        quotes = []
        for chunk in input_schema.get("chunks", []):
            for line in str(chunk.get("text", "")).splitlines():
                if any(flag and flag in line.lower() for flag in flags):
                    quotes.append({"chunk_id": chunk["chunk_id"], "quote": line.strip()})
                    break
        return {
            "applicability": "applies" if quotes else "cannot_tell",
            "reason": "Mock-Belegsuche.",
            "quotes": quotes[:5],
        }
    if output_schema is NarrowVerdict:
        quotes = input_schema.get("quotes", [])
        if not quotes:
            return {"status": "unclear", "severity": "medium", "rationale": "Mock: keine Zitate."}
        return {
            "status": "fulfilled",
            "severity": None,
            "rationale": "Mock-Assessor: geforderter Nachweis gefunden.",
            "supporting_quote_indices": [0],
            "evidence_type": "Dokumentauszug",
            "evidence_reference": quotes[0]["chunk_id"],
            "evidence_sufficiency": "sufficient",
            "independent_support": False,
        }
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


def _mock_extraction_output(
    prompt: str, input_schema: dict[str, Any], output_schema: type
) -> dict[str, Any]:
    """Offline extraction extracts nothing; the validator layer stays a no-op."""
    return {
        "signatures": [],
        "measurements": [],
        "specifications": [],
        "action_items": [],
        "events": [],
    }


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
