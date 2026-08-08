"""Arithmetic self-consistency checks over raw chunk text.

Three of the second blind corpus's seven judgment misses were sums the
assessor read, quoted, and never recomputed: a factor-ten unit conversion, a
total line contradicting its own items, and "14 von 320 (2,8 %)" where the
fraction is 4,4 %. In each case both numbers sat verbatim in the evidence of
a verdict published as fulfilled. Reading is not arithmetic, and no amount of
prompting makes a language model reliably multiply.

These checks run on chunk text rather than extracted rows, for two reasons:
the patterns are self-contained in one line, and the extraction pass is
exactly what truncates on the dense, table-heavy documents where numbers
live. They are also deliberately non-escalating -- they publish their own
rows and annotate verdicts citing the same chunk, but never flip someone
else's verdict to VIOLATED. A contradiction in a document's arithmetic is a
fact about the document, not a ruling about which obligation it breaches.

Scope is narrower than the misses alone would justify. An adversarial review
of the first draft confirmed fourteen ways it could fire on correct
documents: percentages bound to unrelated fractions across a table row, "/"
read as a fraction bar in dates and dilutions, "Gesamtkeimzahl" read as a
total row, subtotals summed against every item, negative correction rows
added instead of subtracted. Each of those is a false violation in a report
whose decoy specificity -- 41 of 42 -- is the strongest result this engine
has. So the table-total check is gone until real table semantics exist to
support it, and what remains fires only on a syntactically explicit
restatement: a parenthesised or connector-introduced percentage, and a
conversion between two genuinely different units.

Ambiguity acquits throughout. German and English decimal conventions collide
("113.190" is one hundred thousand here and a hundred there), so an ambiguous
literal is read both ways and flagged only when every reading disagrees.
"""

from __future__ import annotations

import re

from app.schemas.domain import DocumentChunk
from app.schemas.structured_evidence import EvidenceLocation, ValidatorFinding

ARITHMETIC_VALIDATOR_VERSION = "arithmetic-validators-v0.2"

#: Relative tolerance for a restated quantity, generous enough to absorb the
#: rounding a document legitimately does and far below the errors caught here
#: (the blind corpus's were 36% and 900% off).
_RELATIVE_TOLERANCE = 0.02

#: Percentage points a stated share may differ from its own fraction before it
#: counts as contradicted; paired with the relative tolerance so neither small
#: nor large shares trip on rounding alone.
_PERCENTAGE_POINT_TOLERANCE = 0.15

#: Longest quote a finding will carry, so a chunk that is one long paragraph
#: does not produce a several-hundred-character "quote".
_MAX_QUOTE_CHARS = 220

_SCALES: dict[str, tuple[str, float]] = {
    "ng": ("mass", 1e-6),
    "µg": ("mass", 1e-3),
    "μg": ("mass", 1e-3),
    "ug": ("mass", 1e-3),
    "mg": ("mass", 1.0),
    "g": ("mass", 1e3),
    "kg": ("mass", 1e6),
    "µl": ("volume", 1e-3),
    "μl": ("volume", 1e-3),
    "ml": ("volume", 1.0),
    "l": ("volume", 1e3),
}

#: Space characters used as thousands separators in real documents.
_SPACES = (" ", " ", " ", " ")

_NUMBER = r"\d{1,3}(?:[.    ]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?"

#: The share must be tied to its fraction syntactically: either parenthesised
#: with the number directly behind the bracket, or introduced by a connector.
#: The gap carries no digits, no table-cell pipe and no bracket of its own, so
#: "3 von 5 Chargen, Ausbeute 92 %" and a table row pairing column two with
#: column four cannot couple. "/" is deliberately not a fraction bar here: in
#: GMP text it is a date, a revision counter or a dilution far more often than
#: a quotient.
_FRACTION_SHARE = re.compile(
    rf"(?P<part>{_NUMBER})\s*(?:von|aus)\s+(?P<whole>{_NUMBER})"
    rf"[^%\n|(\d]{{0,80}}?"
    rf"(?:\(\s*|(?:das sind|dies entspricht|entspricht|entsprechend|also|=)\s*)"
    rf"(?P<share>{_NUMBER})\s*%",
    re.IGNORECASE,
)

_UNIT_ALTERNATION = "µg|μg|ug|mg|kg|ng|g|µl|μl|ml|l"

_CONVERSION = re.compile(
    rf"(?P<left>{_NUMBER})\s*(?P<left_unit>{_UNIT_ALTERNATION})\b"
    rf"\s*(?:entspricht|entsprechen|=|≙|≈|das sind|also)\s*"
    rf"(?P<right>{_NUMBER})\s*(?P<right_unit>{_UNIT_ALTERNATION})\b",
    re.IGNORECASE,
)


def run_arithmetic_validators(
    chunks: list[DocumentChunk],
) -> list[ValidatorFinding]:
    findings: list[ValidatorFinding] = []
    for chunk in chunks:
        findings.extend(_share_contradictions(chunk))
        findings.extend(_conversion_contradictions(chunk))
    return sorted(findings, key=lambda f: (f.validator_id, f.statement))


def _share_contradictions(chunk: DocumentChunk) -> list[ValidatorFinding]:
    """Check a stated percentage against the fraction printed beside it."""
    findings = []
    for match in _FRACTION_SHARE.finditer(chunk.text):
        parts = _readings(match.group("part"))
        wholes = _readings(match.group("whole"))
        shares = _readings(match.group("share"))
        if not (parts and wholes and shares):
            continue
        pairs = [
            (part, whole)
            for part in parts
            for whole in wholes
            if whole > 0 and part <= whole
        ]
        # A part exceeding its whole under every reading is a different defect
        # and not this validator's business.
        if not pairs:
            continue
        contradicted = all(
            not _share_agrees(part / whole * 100.0, share)
            for part, whole in pairs
            for share in shares
        )
        if not contradicted:
            continue
        computed = pairs[0][0] / pairs[0][1] * 100.0
        findings.append(
            ValidatorFinding(
                validator_id="share_contradicts_fraction",
                requirement_ids=[],
                severity="high",
                statement=(
                    f"Angegebener Anteil {match.group('share')} % widerspricht "
                    f"der genannten Grundlage {match.group('part')} von "
                    f"{match.group('whole')} (rechnerisch "
                    f"{_format(round(computed, 1))} %)."
                ),
                locations=[_location(chunk, match)],
            )
        )
    return findings


def _conversion_contradictions(chunk: DocumentChunk) -> list[ValidatorFinding]:
    """Check a restated quantity against its own unit conversion.

    Only across genuinely different units. With the same unit on both sides
    the equation is not a conversion but an identification of two different
    quantities -- fill volume against nominal volume, salt form against free
    base, gross against net -- and calling those arithmetic errors would
    report correct documents as broken.
    """
    findings = []
    for match in _CONVERSION.finditer(chunk.text):
        left_unit = _SCALES.get(match.group("left_unit").lower())
        right_unit = _SCALES.get(match.group("right_unit").lower())
        if not left_unit or not right_unit:
            continue
        if left_unit[0] != right_unit[0] or left_unit[1] == right_unit[1]:
            continue
        lefts = _readings(match.group("left"))
        rights = _readings(match.group("right"))
        if not (lefts and rights):
            continue
        contradicted = all(
            not _within_tolerance(left * left_unit[1], right * right_unit[1])
            for left in lefts
            for right in rights
        )
        if not contradicted:
            continue
        expected = lefts[0] * left_unit[1] / right_unit[1]
        findings.append(
            ValidatorFinding(
                validator_id="conversion_contradicts_value",
                requirement_ids=[],
                severity="high",
                statement=(
                    f"Umrechnung widersprüchlich: {match.group('left')} "
                    f"{match.group('left_unit')} entspricht "
                    f"{_format(expected)} {match.group('right_unit')}, "
                    f"angegeben ist {match.group('right')} "
                    f"{match.group('right_unit')}."
                ),
                locations=[_location(chunk, match)],
            )
        )
    return findings


def _readings(value: str) -> list[float]:
    """Every plausible numeric reading of a literal, plain reading first.

    A single three-digit group is genuinely ambiguous in isolation: 62,244 is
    German decimal or English thousands, 113.190 the reverse. Both readings
    are returned so a contradiction has to hold either way. Two or more groups
    (1.000.000) can only be thousands.
    """
    if value is None:
        return []
    literal = re.search(_NUMBER, value)
    if literal is None:
        return []
    text = literal.group(0)
    for space in _SPACES:
        text = text.replace(space, "")
    if "," in text and "." in text:
        # The rightmost separator is the decimal point in both conventions.
        if text.rfind(",") > text.rfind("."):
            return [float(text.replace(".", "").replace(",", "."))]
        return [float(text.replace(",", ""))]
    if "," in text:
        if re.fullmatch(r"\d{1,3},\d{3}", text):
            return [float(text.replace(",", ".")), float(text.replace(",", ""))]
        if re.fullmatch(r"\d{1,3}(?:,\d{3})+", text):
            return [float(text.replace(",", ""))]
        return [float(text.replace(",", "."))]
    if "." in text:
        if re.fullmatch(r"\d{1,3}\.\d{3}", text):
            return [float(text.replace(".", "")), float(text)]
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", text):
            return [float(text.replace(".", ""))]
        return [float(text)]
    try:
        return [float(text)]
    except ValueError:
        return []


def _share_agrees(computed: float, stated: float) -> bool:
    if abs(computed - stated) <= _PERCENTAGE_POINT_TOLERANCE:
        return True
    return _within_tolerance(computed, stated)


def _within_tolerance(expected: float, actual: float) -> bool:
    if expected == 0:
        return abs(actual) <= 1e-9
    return abs(expected - actual) / abs(expected) <= _RELATIVE_TOLERANCE


def _format(value: float) -> str:
    text = f"{value:,.4f}".rstrip("0").rstrip(".")
    return text.replace(",", "@").replace(".", ",").replace("@", ".")


def _location(chunk: DocumentChunk, match: re.Match[str]) -> EvidenceLocation:
    """Quote the matched passage, widened to its line but never unbounded.

    PDF extractions routinely deliver a whole paragraph as one line, so
    quoting to the newline can produce hundreds of characters around the two
    numbers that matter. The quote stays an exact chunk substring either way.
    """
    text = chunk.text
    line_start = text.rfind("\n", 0, match.start()) + 1
    line_end = text.find("\n", match.end())
    line_end = len(text) if line_end == -1 else line_end
    if line_end - line_start <= _MAX_QUOTE_CHARS:
        quote = text[line_start:line_end]
    else:
        slack = max((_MAX_QUOTE_CHARS - (match.end() - match.start())) // 2, 0)
        start = max(line_start, match.start() - slack)
        end = min(line_end, match.end() + slack)
        quote = text[start:end]
    return EvidenceLocation(
        document_id=chunk.document_id,
        chunk_id=chunk.chunk_id,
        page=chunk.page_start,
        quote=quote.strip() or text[match.start() : match.end()],
    )
