from __future__ import annotations

from app.services.document_parser import ParsedDocument


def score_parsing_quality(parsed: ParsedDocument, *, parser_error: str | None = None) -> float:
    if parser_error:
        return 0.0
    if not parsed.pages:
        return 0.0

    page_count = len(parsed.pages)
    extracted_lengths = [len(page.text.strip()) for page in parsed.pages]
    non_empty_pages = sum(1 for length in extracted_lengths if length > 0)
    empty_pages = page_count - non_empty_pages
    total_text = "\n".join(page.text for page in parsed.pages)
    replacement_count = total_text.count("\ufffd")

    text_presence_score = non_empty_pages / page_count
    empty_page_penalty = empty_pages / page_count * 0.35
    replacement_penalty = min(0.3, replacement_count / max(1, len(total_text)) * 12)
    shortness_penalty = 0.35 if len(total_text.strip()) < 30 else 0.0
    confidence_score = sum(page.extraction_confidence for page in parsed.pages) / page_count

    score = (
        0.45 * text_presence_score
        + 0.45 * confidence_score
        + 0.10 * min(1.0, len(total_text.strip()) / 500)
        - empty_page_penalty
        - replacement_penalty
        - shortness_penalty
    )
    return round(max(0.0, min(1.0, score)), 4)
