from app.schemas.domain import Claim, ClaimType
from app.services.review_orchestrator import (
    MockModelProvider,
    ReviewerAgent,
    _claims_for_agent,
)


def test_reviewer_context_is_bounded_and_keeps_document_coverage() -> None:
    agent = ReviewerAgent(
        agent_id="agent_deviation",
        role="DeviationReviewer",
        prompt_version="test-v1",
        applicable_risk_categories=["deviation_management"],
        provider=MockModelProvider(),
    )
    claims = [
        _claim(index=index, document_id=f"doc_{index % 3}")
        for index in range(60)
    ]
    claims[5] = _claim(index=5, document_id="doc_2", claim_type=ClaimType.MISSING_OR_UNCLEAR)

    selected = _claims_for_agent(
        agent=agent,
        claims=claims,
        requirements=[],
        max_claims=8,
    )

    assert len(selected) == 8
    assert {claim.document_id for claim in selected} == {"doc_0", "doc_1", "doc_2"}
    assert any(claim.claim_type == ClaimType.MISSING_OR_UNCLEAR for claim in selected)


def _claim(
    *,
    index: int,
    document_id: str,
    claim_type: ClaimType = ClaimType.DEVIATION_DESCRIPTION,
) -> Claim:
    return Claim(
        claim_id=f"claim_{index:020d}",
        document_id=document_id,
        chunk_id=f"chunk_{index}",
        page=1,
        claim_type=claim_type,
        normalized_subject="deviation" if index % 2 else "routine_record",
        normalized_predicate="states",
        normalized_object=f"value-{index}",
        raw_text_quote=f"Deviation DEV-{index:03d}" if index % 2 else f"Routine record {index}",
        confidence=0.9,
        dependencies=[],
        created_by_model="test",
        prompt_version="test-v1",
    )
