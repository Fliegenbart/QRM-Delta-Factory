from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from app.audit.events import audit_log
from app.db.in_memory import repository
from app.main import app
from app.schemas.domain import (
    Claim,
    ClaimType,
    Document,
    DocumentChunk,
    DocumentSet,
    RequirementSet,
)
from app.services.claim_ledger import (
    ClaimLedgerService,
    ClaimLedgerValidationError,
    MockClaimExtractor,
)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    repository.reset()
    audit_log.clear()
    repository.create_requirement_set(_active_requirement_set())
    repository.create_document_set(_document_set())
    repository.add_document(document=_document("doc_deviation_record"), chunks=[_chunk_one()])
    repository.add_document(document=_document("doc_capa_record"), chunks=[_chunk_two()])


def test_claim_ledger_endpoint_extracts_expected_claims_from_chunks() -> None:
    client = TestClient(app)

    response = client.get("/document-sets/ds_claim_demo/claims")

    assert response.status_code == 200
    claims = response.json()
    claim_types = {claim["claim_type"] for claim in claims}
    assert {
        "batch_identifier",
        "deviation_description",
        "root_cause",
        "impact_assessment",
        "capa_action",
        "qa_approval",
        "effectiveness_check",
        "date_or_deadline",
    }.issubset(claim_types)
    assert all(claim["raw_text_quote"] for claim in claims)
    assert all(claim["document_id"] and claim["chunk_id"] and claim["page"] for claim in claims)
    assert all(0 <= claim["confidence"] <= 1 for claim in claims)


def test_cross_document_claims_are_linked_by_shared_ids() -> None:
    client = TestClient(app)

    claims = client.get("/document-sets/ds_claim_demo/claims").json()
    batch_claims = [
        claim for claim in claims if claim["normalized_subject"] == "batch_identifier"
    ]
    capa_claims = [claim for claim in claims if claim["normalized_subject"] == "capa_id"]

    assert len(batch_claims) == 2
    assert len(capa_claims) == 2
    assert all(claim["dependencies"] for claim in batch_claims)
    assert all(claim["dependencies"] for claim in capa_claims)


def test_claims_without_quote_are_rejected() -> None:
    class BadExtractor(MockClaimExtractor):
        def extract_claims(self, document_set_id, chunks, requirements_context):  # type: ignore[no-untyped-def]
            return [
                Claim.model_construct(
                    claim_id="claim_bad_empty_quote",
                    document_id="doc_deviation_record",
                    chunk_id="chunk_deviation_record_p1",
                    page=1,
                    claim_type=ClaimType.BATCH_IDENTIFIER,
                    normalized_subject="batch_identifier",
                    normalized_predicate="identifies",
                    normalized_object="BATCH-001",
                    raw_text_quote="",
                    confidence=0.9,
                    dependencies=[],
                    created_by_model="bad-extractor",
                    prompt_version="bad-prompt",
                )
            ]

    service = ClaimLedgerService(
        repository=repository,
        audit_log=audit_log,
        extractor=BadExtractor(),
    )

    with pytest.raises(ClaimLedgerValidationError):
        service.build_claim_ledger("ds_claim_demo")


def test_duplicate_claims_are_deduplicated() -> None:
    class DuplicateExtractor(MockClaimExtractor):
        def extract_claims(self, document_set_id, chunks, requirements_context):  # type: ignore[no-untyped-def]
            claim = Claim.model_validate(
                {
                    "claim_id": "claim_duplicate_a",
                    "document_id": "doc_deviation_record",
                    "chunk_id": "chunk_deviation_record_p1",
                    "page": 1,
                    "claim_type": "batch_identifier",
                    "normalized_subject": "batch_identifier",
                    "normalized_predicate": "identifies",
                    "normalized_object": "BATCH-001",
                    "raw_text_quote": "Batch BATCH-001",
                    "confidence": 0.9,
                    "dependencies": [],
                    "created_by_model": "duplicate-extractor",
                    "prompt_version": "duplicate-prompt",
                }
            )
            return [claim, claim.model_copy(update={"claim_id": "claim_duplicate_b"})]

    service = ClaimLedgerService(
        repository=repository,
        audit_log=audit_log,
        extractor=DuplicateExtractor(),
    )

    claims = service.build_claim_ledger("ds_claim_demo")

    assert len(claims) == 1
    assert claims[0].claim_id == "claim_duplicate_a"


def test_claim_extraction_audit_includes_extractor_and_prompt_versions() -> None:
    client = TestClient(app)

    response = client.get("/document-sets/ds_claim_demo/claims")

    assert response.status_code == 200
    event = audit_log.list_events()[-1]
    assert event.event_type == "claim_extraction_run"
    assert event.payload["extractor_version"] == "mock-claim-extractor-v0.1"
    assert event.payload["prompt_version"] == "mock-claim-ledger-v0.1"
    assert event.payload["claim_count"] == len(response.json())


def _document_set() -> DocumentSet:
    return DocumentSet(
        document_set_id="ds_claim_demo",
        tenant_id="tenant_demo_pharma",
        requirement_set_id="rset_claim_demo_2026",
        upload_timestamp=datetime.now(UTC),
        document_ids=[],
        declared_document_type="deviation",
        declared_process_area="aseptic_filling",
        uploaded_by="user_qrm_author",
        status="ready_for_orchestration",
    )


def _active_requirement_set() -> RequirementSet:
    return RequirementSet(
        requirement_set_id="rset_claim_demo_2026",
        tenant_id="tenant_demo_pharma",
        name="Claim Demo Requirements",
        version="2026.1",
        imported_at=datetime.now(UTC),
        imported_by="user_quality_admin",
        active=True,
        requirements=[
            {
                "requirement_id": "req_claim_demo",
                "source_type": "internal_sop",
                "source_name": "SOP-CLAIM-DEMO",
                "source_version": "1.0",
                "section": "1.0",
                "requirement_text": "Claims must be traceable to source chunks.",
                "applies_to_document_types": ["deviation"],
                "applies_to_process_areas": ["aseptic_filling"],
                "criticality": "medium",
                "required_evidence": ["source chunk quote"],
                "auto_close_allowed": False,
                "effective_from": "2026-01-01T00:00:00Z",
                "effective_to": None,
            }
        ],
    )


def _document(document_id: str) -> Document:
    return Document(
        document_id=document_id,
        document_set_id="ds_claim_demo",
        filename=f"{document_id}.txt",
        file_hash_sha256=sha256(document_id.encode()).hexdigest(),
        mime_type="text/plain",
        page_count=1,
        storage_uri=f"local://claim-demo/{document_id}.txt",
        parser_version="test-parser",
        parsing_status="parsed",
        parsing_quality_score=0.95,
        language="en",
        metadata={},
    )


def _chunk_one() -> DocumentChunk:
    text = (
        "Deviation DEV-2026-014 for Batch BATCH-001. "
        "Root cause: automated visual inspection threshold configuration error. "
        "Impact assessment: possible false accept of defective container. "
        "CAPA CAPA-2026-020 assigned to QA Operations."
    )
    return _chunk("chunk_deviation_record_p1", "doc_deviation_record", text)


def _chunk_two() -> DocumentChunk:
    text = (
        "Batch BATCH-001 reviewed under CAPA CAPA-2026-020. "
        "QA approval: pending. Effectiveness check due 2026-06-01."
    )
    return _chunk("chunk_capa_record_p1", "doc_capa_record", text)


def _chunk(chunk_id: str, document_id: str, text: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        page_start=1,
        page_end=1,
        text=text,
        token_count=len(text.split()),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )
