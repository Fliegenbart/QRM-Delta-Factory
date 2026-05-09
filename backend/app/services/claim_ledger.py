from __future__ import annotations

import re
from collections.abc import Sequence
from hashlib import sha256
from typing import Protocol

from pydantic import ValidationError

from app.audit.events import InMemoryAuditLog
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


class LLMClaimExtractor:
    extractor_version = "llm-claim-extractor-stub-v0.1"
    prompt_version = "llm-claim-ledger-stub-v0.1"

    def extract_claims(
        self,
        document_set_id: str,
        chunks: Sequence[DocumentChunk],
        requirements_context: Sequence[Requirement],
    ) -> list[Claim]:
        raise NotImplementedError("LLMClaimExtractor is a stub and must not call external APIs.")


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
