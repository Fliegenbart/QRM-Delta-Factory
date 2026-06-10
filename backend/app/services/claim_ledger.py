from __future__ import annotations

import re
from collections.abc import Sequence
from hashlib import sha256
from typing import Protocol

from pydantic import BaseModel, Field, ValidationError

from app.agents.providers import (
    AnthropicProvider,
    BaseModelProvider,
    MistralProvider,
    ProviderRuntimeOptions,
)
from app.audit.events import InMemoryAuditLog
from app.core.config import get_settings
from app.db.in_memory import InMemoryDocumentRepository
from app.schemas.domain import Claim, ClaimType, DocumentChunk, Requirement


class ClaimLedgerValidationError(Exception):
    pass


class ClaimLedgerDocumentSetNotFoundError(Exception):
    pass


class ClaimExtractor(Protocol):
    extractor_version: str
    prompt_version: str

    def extract_claims(
        self,
        document_set_id: str,
        chunks: Sequence[DocumentChunk],
        requirements_context: Sequence[Requirement],
    ) -> list[Claim]:
        ...


class MockClaimExtractor:
    extractor_version = "mock-claim-extractor-v0.1"
    prompt_version = "mock-claim-ledger-v0.1"

    def extract_claims(
        self,
        document_set_id: str,
        chunks: Sequence[DocumentChunk],
        requirements_context: Sequence[Requirement],
    ) -> list[Claim]:
        claims: list[Claim] = []
        for chunk in chunks:
            claims.extend(self._extract_from_chunk(chunk))
        return claims

    def _extract_from_chunk(self, chunk: DocumentChunk) -> list[Claim]:
        text = chunk.text
        claims: list[Claim] = []

        for match in re.finditer(r"\b(?:Batch|Charge|Lot)\s+([A-Z0-9][A-Z0-9-]+)\b", text):
            claims.append(
                _claim(
                    chunk=chunk,
                    claim_type=ClaimType.BATCH_IDENTIFIER,
                    normalized_subject="batch_identifier",
                    normalized_predicate="identifies",
                    normalized_object=match.group(1),
                    quote=match.group(0),
                    confidence=0.95,
                    extractor_version=self.extractor_version,
                    prompt_version=self.prompt_version,
                )
            )

        for match in re.finditer(r"\b(DEV-[A-Z0-9-]+)\b", text):
            quote = _sentence_containing(text=text, start=match.start(), end=match.end())
            claims.append(
                _claim(
                    chunk=chunk,
                    claim_type=ClaimType.DEVIATION_DESCRIPTION,
                    normalized_subject="deviation_id",
                    normalized_predicate="describes",
                    normalized_object=match.group(1),
                    quote=quote,
                    confidence=0.9,
                    extractor_version=self.extractor_version,
                    prompt_version=self.prompt_version,
                )
            )

        for match in re.finditer(r"\b(CAPA-[A-Z0-9-]+)\b", text):
            quote = _sentence_containing(text=text, start=match.start(), end=match.end())
            claims.append(
                _claim(
                    chunk=chunk,
                    claim_type=ClaimType.CAPA_ACTION,
                    normalized_subject="capa_id",
                    normalized_predicate="references",
                    normalized_object=match.group(1),
                    quote=quote,
                    confidence=0.9,
                    extractor_version=self.extractor_version,
                    prompt_version=self.prompt_version,
                )
            )

        claims.extend(self._extract_labeled_claims(chunk))
        claims.extend(self._extract_dates(chunk))
        claims.extend(self._extract_unclear_claims(chunk))
        return claims

    def _extract_labeled_claims(self, chunk: DocumentChunk) -> list[Claim]:
        patterns = [
            (ClaimType.ROOT_CAUSE, "root_cause", r"Root cause:\s*([^.]+)\."),
            (
                ClaimType.IMPACT_ASSESSMENT,
                "impact_assessment",
                r"Impact assessment:\s*([^.]+)\.",
            ),
            (ClaimType.QA_APPROVAL, "qa_approval", r"QA approval:\s*([^.]+)\."),
            (
                ClaimType.EFFECTIVENESS_CHECK,
                "effectiveness_check",
                r"Effectiveness check[^.]*\.",
            ),
            (
                ClaimType.ACCEPTANCE_CRITERION,
                "acceptance_criterion",
                r"Acceptance criterion:\s*([^.]+)\.",
            ),
            (ClaimType.TEST_RESULT, "test_result", r"Test result:\s*([^.]+)\."),
            (ClaimType.RESPONSIBLE_PARTY, "responsible_party", r"assigned to\s+([^.]+)\."),
        ]
        claims: list[Claim] = []
        for claim_type, subject, pattern in patterns:
            for match in re.finditer(pattern, chunk.text, flags=re.IGNORECASE):
                quote = match.group(0)
                normalized_object = match.group(1).strip() if match.lastindex else quote
                claims.append(
                    _claim(
                        chunk=chunk,
                        claim_type=claim_type,
                        normalized_subject=subject,
                        normalized_predicate="states",
                        normalized_object=normalized_object,
                        quote=quote,
                        confidence=0.85,
                        extractor_version=self.extractor_version,
                        prompt_version=self.prompt_version,
                    )
                )
        return claims

    def _extract_dates(self, chunk: DocumentChunk) -> list[Claim]:
        claims: list[Claim] = []
        for match in re.finditer(r"\b(20\d{2}-\d{2}-\d{2})\b", chunk.text):
            quote = _sentence_containing(text=chunk.text, start=match.start(), end=match.end())
            claims.append(
                _claim(
                    chunk=chunk,
                    claim_type=ClaimType.DATE_OR_DEADLINE,
                    normalized_subject="date_or_deadline",
                    normalized_predicate="states_date",
                    normalized_object=match.group(1),
                    quote=quote,
                    confidence=0.9,
                    extractor_version=self.extractor_version,
                    prompt_version=self.prompt_version,
                )
            )
        return claims

    def _extract_unclear_claims(self, chunk: DocumentChunk) -> list[Claim]:
        claims: list[Claim] = []
        for match in re.finditer(
            r"\b(missing|unclear|not documented|not available)\b",
            chunk.text,
            re.I,
        ):
            quote = _sentence_containing(text=chunk.text, start=match.start(), end=match.end())
            claims.append(
                _claim(
                    chunk=chunk,
                    claim_type=ClaimType.MISSING_OR_UNCLEAR,
                    normalized_subject="missing_or_unclear",
                    normalized_predicate="flags",
                    normalized_object=match.group(1).lower(),
                    quote=quote,
                    confidence=0.55,
                    extractor_version=self.extractor_version,
                    prompt_version=self.prompt_version,
                )
            )
        return claims


class ExtractedClaimDraft(BaseModel):
    claim_type: str = Field(min_length=1)
    normalized_subject: str = Field(min_length=1)
    normalized_predicate: str = Field(min_length=1)
    normalized_object: str = Field(min_length=1)
    exact_quote: str = Field(min_length=1)
    confidence: float = Field(default=0.8, ge=0, le=1)


class ClaimExtractionOutput(BaseModel):
    claims: list[ExtractedClaimDraft] = Field(default_factory=list)
    coverage_summary: str = Field(default="no summary provided")


_CLAIM_EXTRACTION_PROMPT = """\
You are a conservative GMP claim extraction model for pharmaceutical quality documents.
Extract every atomic, checkable claim from the supplied document chunk. The documents may
be written in German or English; keep quotes in the original language.

Extract claims for, at minimum:
- identifiers (deviation/CAPA/change IDs, batch/lot numbers, equipment IDs, SOP references)
- all dates in any format (ISO, German 14.12.2026, written out), including signature dates
- signatures, approvals, reviewer names and roles
- classifications and severity ratings (e.g. Minor/Major/Critical Einstufung)
- process parameters, specification limits, measured values and their stated acceptance ranges
- impact assessments and no-impact statements (including 'kein Einfluss', 'nicht betroffen')
- root cause statements, CAPA actions, effectiveness checks
- test results, release decisions, batch dispositions
- statements that information is missing, unclear, pending or not documented

Rules:
- exact_quote MUST be a verbatim, character-exact substring of the chunk text. Never paraphrase.
- Keep quotes short: the single sentence or line that carries the claim.
- One claim per atomic statement; prefer many small claims over few broad ones.
- claim_type MUST be one of: batch_identifier, deviation_description, root_cause,
  impact_assessment, capa_action, qa_approval, effectiveness_check, date_or_deadline,
  responsible_party, acceptance_criterion, test_result, missing_or_unclear.
- normalized_subject/predicate/object: short English snake_case normalization of the claim.
- Do not invent claims that are not present in the chunk text.
"""


class LLMClaimExtractor:
    extractor_version = "llm-claim-extractor-v1.0"
    prompt_version = "llm-claim-ledger-v1.0"

    def __init__(self, *, provider: BaseModelProvider) -> None:
        self.provider = provider
        self.token_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        self.call_count = 0

    def _record_token_usage(self) -> None:
        metadata = self.provider.last_run_metadata
        if metadata is not None and metadata.token_usage is not None:
            self.token_usage["input_tokens"] += metadata.token_usage.input_tokens
            self.token_usage["output_tokens"] += metadata.token_usage.output_tokens
            self.token_usage["total_tokens"] += metadata.token_usage.total_tokens
        self.call_count += 1

    def extract_claims(
        self,
        document_set_id: str,
        chunks: Sequence[DocumentChunk],
        requirements_context: Sequence[Requirement],
    ) -> list[Claim]:
        claims: list[Claim] = []
        errors: list[str] = []
        for chunk in chunks:
            try:
                output = self.provider.run_structured(
                    prompt=_CLAIM_EXTRACTION_PROMPT,
                    input_schema={
                        "document_set_id": document_set_id,
                        "document_id": chunk.document_id,
                        "chunk_id": chunk.chunk_id,
                        "page": chunk.page_start,
                        "chunk_text": chunk.text,
                    },
                    output_schema=ClaimExtractionOutput,
                )
            except Exception as exc:  # noqa: BLE001 - keep per-chunk failures isolated
                errors.append(f"{chunk.chunk_id}: {exc}")
                self._record_token_usage()
                continue
            self._record_token_usage()
            parsed = ClaimExtractionOutput.model_validate(output)
            for draft in parsed.claims:
                quote = _locate_verbatim_quote(draft.exact_quote, chunk.text)
                if quote is None:
                    continue
                claims.append(
                    _claim(
                        chunk=chunk,
                        claim_type=_safe_claim_type(draft.claim_type),
                        normalized_subject=draft.normalized_subject,
                        normalized_predicate=draft.normalized_predicate,
                        normalized_object=draft.normalized_object,
                        quote=quote,
                        confidence=min(max(draft.confidence, 0.0), 1.0),
                        extractor_version=self.extractor_version,
                        prompt_version=self.prompt_version,
                    )
                )
        if not claims and errors:
            raise ClaimLedgerValidationError(
                "LLM claim extraction produced no claims; chunk errors: " + "; ".join(errors)
            )
        return claims


def _locate_verbatim_quote(quote: str, chunk_text: str) -> str | None:
    candidate = quote.strip()
    if not candidate:
        return None
    if candidate in chunk_text:
        return candidate
    tokens = candidate.split()
    if not tokens:
        return None
    pattern = r"\s+".join(re.escape(token) for token in tokens)
    match = re.search(pattern, chunk_text)
    if match is None:
        match = re.search(pattern, chunk_text, flags=re.IGNORECASE)
    if match is None:
        return None
    return chunk_text[match.start() : match.end()]


def _safe_claim_type(value: str) -> ClaimType:
    normalized = value.strip().lower()
    try:
        return ClaimType(normalized)
    except ValueError:
        return ClaimType.DEVIATION_DESCRIPTION


def default_claim_extractor() -> ClaimExtractor:
    settings = get_settings()
    if not settings.external_model_calls_enabled:
        return MockClaimExtractor()
    runtime_options = ProviderRuntimeOptions(
        timeout_seconds=settings.model_provider_timeout_seconds,
        max_retries=settings.model_provider_max_retries,
        circuit_breaker_failure_threshold=settings.model_provider_circuit_breaker_threshold,
    )
    allowed = settings.allowed_model_provider_set()
    if settings.reviewer_provider_override == "mistral" and "mistral" in allowed:
        return LLMClaimExtractor(
            provider=MistralProvider(
                configured_model_id=settings.mistral_model_id,
                runtime_options=runtime_options,
            )
        )
    if "anthropic" in allowed:
        return LLMClaimExtractor(
            provider=AnthropicProvider(
                configured_model_id=settings.anthropic_model_id,
                runtime_options=runtime_options,
            )
        )
    return MockClaimExtractor()


class ClaimLedgerService:
    def __init__(
        self,
        *,
        repository: InMemoryDocumentRepository,
        audit_log: InMemoryAuditLog,
        extractor: ClaimExtractor,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.extractor = extractor

    def get_or_build_claim_ledger(self, document_set_id: str) -> list[Claim]:
        existing_claims = self.repository.list_claims(document_set_id)
        if existing_claims:
            return existing_claims
        return self.build_claim_ledger(document_set_id)

    def build_claim_ledger(self, document_set_id: str) -> list[Claim]:
        document_set = self.repository.get_document_set(document_set_id)
        if document_set is None:
            raise ClaimLedgerDocumentSetNotFoundError(f"DocumentSet {document_set_id} not found")

        chunks = self.repository.list_chunks_for_document_set(document_set_id)
        requirement_set = self.repository.get_requirement_set(document_set.requirement_set_id)
        requirements_context = requirement_set.requirements if requirement_set else []
        extracted_claims = self.extractor.extract_claims(
            document_set_id,
            chunks,
            requirements_context,
        )
        validated_claims = _validate_claims_against_chunks(extracted_claims, chunks)
        deduplicated_claims = _deduplicate_claims(validated_claims)
        linked_claims = _link_related_claims(deduplicated_claims)
        self.repository.replace_claim_ledger(document_set_id=document_set_id, claims=linked_claims)
        payload = {
            "extractor_version": self.extractor.extractor_version,
            "prompt_version": self.extractor.prompt_version,
            "claim_count": len(linked_claims),
            "chunk_count": len(chunks),
        }
        token_usage = getattr(self.extractor, "token_usage", None)
        if token_usage:
            # Key names avoid the substring "token": the audit redaction layer
            # blanks any key containing it (it protects credentials, not counts).
            payload["llm_usage"] = {
                "input": token_usage.get("input_tokens", 0),
                "output": token_usage.get("output_tokens", 0),
                "total": token_usage.get("total_tokens", 0),
            }
            provider = getattr(self.extractor, "provider", None)
            payload["extractor_provider"] = getattr(provider, "provider_name", "unknown")
        self.audit_log.append(
            event_type="claims_extracted",
            actor_id=document_set.uploaded_by,
            entity_type="DocumentSet",
            entity_id=document_set_id,
            tenant_id=document_set.tenant_id,
            payload=payload,
        )
        self.audit_log.append(
            event_type="claim_extraction_run",
            actor_id=document_set.uploaded_by,
            entity_type="DocumentSet",
            entity_id=document_set_id,
            tenant_id=document_set.tenant_id,
            payload=payload,
        )
        return linked_claims


def _claim(
    *,
    chunk: DocumentChunk,
    claim_type: ClaimType,
    normalized_subject: str,
    normalized_predicate: str,
    normalized_object: str,
    quote: str,
    confidence: float,
    extractor_version: str,
    prompt_version: str,
) -> Claim:
    cleaned_quote = quote.strip()
    claim_key = "|".join(
        [
            chunk.document_id,
            chunk.chunk_id,
            claim_type.value,
            normalized_subject,
            normalized_predicate,
            normalized_object.strip().upper(),
            cleaned_quote,
        ]
    )
    return Claim(
        claim_id=f"claim_{sha256(claim_key.encode()).hexdigest()[:20]}",
        document_id=chunk.document_id,
        chunk_id=chunk.chunk_id,
        page=chunk.page_start,
        claim_type=claim_type,
        normalized_subject=normalized_subject,
        normalized_predicate=normalized_predicate,
        normalized_object=normalized_object.strip(),
        raw_text_quote=cleaned_quote,
        confidence=confidence,
        dependencies=[],
        created_by_model=extractor_version,
        prompt_version=prompt_version,
    )


def _sentence_containing(*, text: str, start: int, end: int) -> str:
    sentence_start = text.rfind(".", 0, start) + 1
    sentence_end = text.find(".", end)
    if sentence_end == -1:
        sentence_end = len(text)
    else:
        sentence_end += 1
    return text[sentence_start:sentence_end].strip()


def _validate_claims_against_chunks(
    claims: Sequence[Claim],
    chunks: Sequence[DocumentChunk],
) -> list[Claim]:
    chunk_lookup = {(chunk.document_id, chunk.chunk_id): chunk for chunk in chunks}
    validated_claims: list[Claim] = []
    for claim in claims:
        try:
            validated = Claim.model_validate(claim.model_dump())
        except ValidationError as exc:
            raise ClaimLedgerValidationError(str(exc)) from exc
        source_chunk = chunk_lookup.get((validated.document_id, validated.chunk_id))
        if source_chunk is None:
            raise ClaimLedgerValidationError(
                f"Claim {validated.claim_id} references an unknown source chunk"
            )
        if validated.raw_text_quote not in source_chunk.text:
            raise ClaimLedgerValidationError(
                f"Claim {validated.claim_id} quote is not present in its source chunk"
            )
        validated_claims.append(validated)
    return validated_claims


def _deduplicate_claims(claims: Sequence[Claim]) -> list[Claim]:
    unique_claims: dict[tuple[str, str, int, ClaimType, str, str, str], Claim] = {}
    for claim in claims:
        key = (
            claim.document_id,
            claim.chunk_id,
            claim.page,
            claim.claim_type,
            claim.normalized_subject,
            claim.normalized_object.upper(),
            claim.raw_text_quote,
        )
        unique_claims.setdefault(key, claim)
    return list(unique_claims.values())


def _link_related_claims(claims: Sequence[Claim]) -> list[Claim]:
    grouped_claim_ids: dict[tuple[str, str], list[str]] = {}
    for claim in claims:
        key = _link_key(claim)
        if key is None:
            continue
        grouped_claim_ids.setdefault(key, []).append(claim.claim_id)

    linked_claims: list[Claim] = []
    for claim in claims:
        key = _link_key(claim)
        dependencies = (
            [
                claim_id
                for claim_id in grouped_claim_ids.get(key, [])
                if claim_id != claim.claim_id
            ]
            if key
            else []
        )
        linked_claims.append(claim.model_copy(update={"dependencies": dependencies}))
    return linked_claims


def _link_key(claim: Claim) -> tuple[str, str] | None:
    linkable_subjects = {
        "batch_identifier",
        "capa_id",
        "deviation_id",
        "product_material_id",
    }
    if claim.normalized_subject not in linkable_subjects:
        return None
    return (claim.normalized_subject, claim.normalized_object.upper())
