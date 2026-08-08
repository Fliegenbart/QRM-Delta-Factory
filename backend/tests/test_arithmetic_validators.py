"""The arithmetic misses of blind corpus two, and what must stay quiet.

The positives reproduce defects the assessor read, quoted into a fulfilled
verdict's evidence, and never recomputed. The negatives carry more weight:
this validator publishes rows, and the engine's strongest measured result is
its decoy specificity. Most of them come from an adversarial review of the
first draft, which confirmed fourteen ways it fired on correct documents.
"""

from __future__ import annotations

from hashlib import sha256

from app.schemas.domain import DocumentChunk
from app.services.arithmetic_validators import _readings, run_arithmetic_validators


def _chunk(text: str, *, name: str = "test") -> DocumentChunk:
    return DocumentChunk(
        chunk_id=f"chunk_{name}",
        document_id="doc_arithmetic",
        page_start=1,
        page_end=1,
        text=text,
        token_count=max(1, len(text.split())),
        extraction_confidence=0.95,
        bbox=None,
        source_hash=sha256(text.encode()).hexdigest(),
    )


def test_stated_share_contradicting_its_own_fraction_is_flagged() -> None:
    """14 of 320 is 4,4 %, not 2,8 % -- both numbers sat in the same sentence."""
    findings = run_arithmetic_validators(
        [
            _chunk(
                "Bei der Dichtheitsprüfung wurden an 14 von 320 geprüften "
                "Ampullen Farbstoffeintritte festgestellt (2,8 %)."
            )
        ]
    )

    assert [f.validator_id for f in findings] == ["share_contradicts_fraction"]
    assert "4,4 %" in findings[0].statement
    assert findings[0].requirement_ids == []


def test_connector_introduced_share_is_also_checked() -> None:
    findings = run_arithmetic_validators(
        [_chunk("An 14 von 320 Ampullen traten Eintritte auf, das sind 2,8 %.")]
    )

    assert [f.validator_id for f in findings] == ["share_contradicts_fraction"]


def test_unit_conversion_off_by_a_factor_is_flagged() -> None:
    """113.190 µg is 113,19 mg; the document wrote 11,32 mg."""
    findings = run_arithmetic_validators(
        [_chunk("Rechnerisch: 113.190 µg entspricht 11,32 mg Wirkstoffübertrag.")]
    )

    assert [f.validator_id for f in findings] == ["conversion_contradicts_value"]
    assert "113,19 mg" in findings[0].statement


def test_correct_arithmetic_stays_silent() -> None:
    quiet = [
        "An 14 von 320 Ampullen (4,4 %) wurden Eintritte festgestellt.",
        "An 7 von 300 Ampullen (2,3 %) Auffälligkeiten.",  # rounding
        "Die Menge von 2.500 mg entspricht 2,5 g Wirkstoff.",
        "Es wurden 1.500 g entnommen, das sind 1,5 kg Material.",
    ]
    for text in quiet:
        assert run_arithmetic_validators([_chunk(text)]) == [], text


def test_percentage_is_only_bound_to_a_fraction_it_is_written_with() -> None:
    """The share must be parenthesised or introduced, never merely nearby.

    A free 120-character window coupled any count to any later percentage on
    the same line -- including across the cells of one table row.
    """
    unbound = [
        "3 von 5 Chargen freigegeben, Ausbeute 92 %.",
        "| 14 | 320 | Sichtprüfung | 92 % |",
        "2 von 3 Prüfungen abgeschlossen (Ergebnis 88 % Wiederfindung).",
        "Revision 3 von 5, Feuchte 12,0 %.",
    ]
    for text in unbound:
        assert run_arithmetic_validators([_chunk(text)]) == [], text


def test_slash_is_not_read_as_a_fraction_bar() -> None:
    """In GMP text "/" is a date, a revision or a dilution far more often."""
    quiet = [
        "Charge 03/2026 zeigte einen Gehalt von 98,5 %.",
        "Verdünnung 1/10 ergab eine Wiederfindung von 95,0 %.",
    ]
    for text in quiet:
        assert run_arithmetic_validators([_chunk(text)]) == [], text


def test_same_unit_restatements_are_not_conversions() -> None:
    """Fill against nominal volume is two quantities, not a failed conversion."""
    quiet = [
        "Das Füllvolumen von 10,5 ml entspricht 10,0 ml Nennvolumen.",
        "Die Einwaage 52,3 mg entspricht 50,0 mg freier Base.",
    ]
    for text in quiet:
        assert run_arithmetic_validators([_chunk(text)]) == [], text


def test_table_totals_are_no_longer_checked() -> None:
    """The total check is withdrawn until table semantics can support it.

    The review confirmed six ways it fired on correct documents:
    "Gesamtkeimzahl" read as a total row, the first of several subtotals
    compared against every item, a continuation chunk losing its first item to
    the header assumption, negative correction rows added instead of
    subtracted, a non-additive column summed, and a tolerance that forgave
    half a unit per cell. One recovered miss does not pay for that surface.
    """
    findings = run_arithmetic_validators(
        [
            _chunk(
                "| Position | Einwaage |\n"
                "|---|---|\n"
                "| Wirkstoff A | 12,044 kg |\n"
                "| Hilfsstoff B | 50,100 kg |\n"
                "| **Gesamteinwaage** | 62,244 kg |"
            )
        ]
    )

    assert findings == []


def test_ambiguous_separators_are_read_both_ways() -> None:
    """German decimals and English thousands collide; both readings survive."""
    assert _readings("113.190") == [113190.0, 113.19]
    assert _readings("62,244 kg") == [62.244, 62244.0]
    assert _readings("1.000.000") == [1000000.0]
    assert _readings("11,32") == [11.32]
    assert _readings("2,8") == [2.8]


def test_quote_stays_bounded_in_a_single_line_paragraph() -> None:
    """PDF extractions deliver whole paragraphs as one line."""
    filler = "Weiterer Fließtext ohne Zahlen. " * 30
    text = f"{filler}An 14 von 320 Ampullen (2,8 %) Eintritte. {filler}"
    findings = run_arithmetic_validators([_chunk(text)])

    assert len(findings) == 1
    quote = findings[0].locations[0].quote
    assert len(quote) <= 220
    assert quote in text
    assert "14 von 320" in quote
