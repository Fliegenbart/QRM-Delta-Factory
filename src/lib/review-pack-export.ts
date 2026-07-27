import {
  displayReviewReason,
  displayReviewReasons,
  displayReviewValue,
  displayRiskStatement,
  reviewPackRiskPresentation,
  type ReviewPack
} from "@/src/lib/review-ui";

type ExportFormat = "pdf" | "csv";
export type ReviewPackPublicationState = "canonical" | "qa_hint_partial";

const csvHeaders = [
  "Prüfpunkt-ID",
  "Risikobeschreibung",
  "Dokument",
  "Seite",
  "Chunk",
  "Zitat",
  "Anforderungen",
  "Verifikationsstatus",
  "Publikationsstatus"
];

export function deriveReviewPackPublication(verifierStatus: string | null | undefined): {
  state: ReviewPackPublicationState;
  label: string;
} {
  return ["strong", "verified"].includes(verifierStatus?.trim().toLowerCase() ?? "")
    ? { state: "canonical", label: "Kanonischer Risikobefund" }
    : { state: "qa_hint_partial", label: "QA-Hinweis" };
}

export function reviewPackExportFileName(pack: ReviewPack, format: ExportFormat): string {
  const caseId = safeFilePart(pack.document_set_id);
  return format === "pdf"
    ? `pruefmappe-${caseId}.pdf`
    : `pruefmappe-${caseId}-evidenz.csv`;
}

export function buildReviewPackCsv(pack: ReviewPack): string {
  const rows = pack.evidence_table.map((row) => [
    row.finding_id,
    row.risk_statement,
    sourceName(row),
    String(row.page),
    row.chunk_id,
    row.quote,
    row.requirement_references.join(", "),
    row.verifier_status,
    deriveReviewPackPublication(row.verifier_status).state
  ]);
  const findingsWithEvidence = new Set(pack.evidence_table.map((row) => row.finding_id));
  for (const risk of pack.top_risks) {
    if (findingsWithEvidence.has(risk.finding_id)) continue;
    rows.push([
      risk.finding_id,
      risk.risk_statement,
      "",
      "",
      "",
      "",
      risk.requirement_references.join(", "),
      risk.verifier_status,
      deriveReviewPackPublication(risk.verifier_status).state
    ]);
  }

  return `\ufeff${[csvHeaders, ...rows].map((row) => row.map(csvCell).join(";")).join("\r\n")}\r\n`;
}

export function createReviewPackPdf(pack: ReviewPack): Blob {
  const pages = new PdfPageBuilder();
  const presentation = reviewPackRiskPresentation(pack);
  const canonicalRisks = pack.top_risks.filter(
    (risk) => deriveReviewPackPublication(risk.verifier_status).state === "canonical"
  );
  const qaHints = pack.top_risks.filter(
    (risk) => deriveReviewPackPublication(risk.verifier_status).state === "qa_hint_partial"
  );
  const evidenceByFinding = groupEvidenceByFinding(pack.evidence_table);
  const reasons = unique([
    ...(pack.decision.required_human_review_reasons ?? []),
    ...pack.ood_reasons,
    ...pack.coverage_gap_reasons,
    ...pack.missing_information
  ]);

  pages.kicker("QA REVIEW PACK");
  pages.heading("Prüfmappe");
  pages.rule();
  pages.labelValue("Fall", pack.document_set_id);
  pages.labelValue("Erstellt", new Date().toLocaleDateString("de-DE"));
  pages.labelValue("Entscheidung", displayReviewValue(pack.decision.decision));
  pages.labelValue("Höchste Einstufung", displayReviewValue(pack.decision.max_severity ?? "nicht angegeben"));
  pages.spacer();
  pages.sectionHeading("QA-Entscheidung");
  pages.paragraph(presentation.summary || pack.summary || "Keine Zusammenfassung vorhanden.");
  pages.spacer();
  pages.sectionHeading("Prüfumfang");
  pages.labelValue("Kernbefunde", `${canonicalRisks.length}`);
  pages.labelValue("QA-Hinweise", `${qaHints.length}`);
  pages.labelValue("Quellenstellen", `${pack.evidence_table.length}`);
  if (presentation.supportingFindingCount > 0) {
    pages.labelValue("Zusätzliche Signale", `${presentation.supportingFindingCount}`);
  }
  pages.spacer();

  pages.sectionHeading("Kernbefunde");
  if (canonicalRisks.length === 0) pages.text("Keine vollständig verifizierten Kernbefunde vorhanden.");
  for (const [index, risk] of canonicalRisks.entries()) {
    pages.findingTitle(`${index + 1}. ${pdfFindingTitle(risk)}`);
    pages.text(`${displayReviewValue(risk.severity)} · ${displayReviewValue(risk.verifier_status)}`, 9);
    pages.paragraph(displayRiskStatement(risk.risk_statement));
    pages.text(`Verifier-Status: ${risk.verifier_status}`, 9);
    addEvidencePreview(pages, evidenceByFinding.get(risk.finding_id) ?? risk.evidence_quotes);
    addQaStep(pages, risk.human_review_reason);
    pages.spacer(6);
  }

  pages.sectionHeading("Hinweise zur QA-Prüfung");
  pages.paragraph("Quellenbezogene Hinweise mit unvollständiger Evidenz. QA bewertet sie vor einer Freigabe.");
  if (qaHints.length === 0) pages.text("Keine nicht-kanonischen QA-Hinweise vorhanden.");
  for (const [index, risk] of qaHints.entries()) {
    pages.findingTitle(`${index + 1}. ${pdfFindingTitle(risk)}`);
    pages.text(`Hinweis · ${displayReviewValue(risk.severity)} · ${displayReviewValue(risk.verifier_status)}`, 9);
    pages.paragraph(displayRiskStatement(risk.risk_statement));
    pages.text(`Verifier-Status: ${risk.verifier_status}`, 9);
    addEvidencePreview(pages, evidenceByFinding.get(risk.finding_id) ?? risk.evidence_quotes, 1);
    addQaStep(pages, risk.human_review_reason);
    pages.spacer(5);
  }

  if (presentation.operationalWarnings.length > 0 || presentation.modelCoverageStatus) {
    pages.sectionHeading("Technische Hinweise");
    if (presentation.modelCoverageStatus) {
      pages.paragraph(`Technische Abdeckung: ${presentation.modelCoverageStatus}`);
    }
    presentation.operationalWarnings.forEach((warning) => pages.paragraph(`- ${displayOperationalWarning(warning)}`));
  }

  if (reasons.length > 0) {
    pages.sectionHeading("Offene Punkte");
    reasons.forEach((reason) => pages.paragraph(`- ${displayReviewReason(reason)}`));
  }

  pages.sectionHeading("Evidenzanhang");
  if (pack.evidence_table.length === 0) {
    pages.text("Keine Evidenzstellen vorhanden.");
  }
  for (const evidence of pack.evidence_table) {
    pages.paragraph(
      `Quelle ${sourceName(evidence)}, Seite ${evidence.page}: ${cleanPdfSnippet(evidence.quote)}`,
      9,
      0
    );
  }

  return new Blob([new Uint8Array(buildPdf(pages.finish()))], { type: "application/pdf" });
}

type ExportEvidencePreview =
  | ReviewPack["evidence_table"][number]
  | (ReviewPack["top_risks"][number]["evidence_quotes"][number] & { document_name?: string | null });

function groupEvidenceByFinding(rows: ReviewPack["evidence_table"]): Map<string, ReviewPack["evidence_table"]> {
  const grouped = new Map<string, ReviewPack["evidence_table"]>();
  for (const row of rows) {
    grouped.set(row.finding_id, [...(grouped.get(row.finding_id) ?? []), row]);
  }
  return grouped;
}

function addEvidencePreview(pages: PdfPageBuilder, evidenceRows: ExportEvidencePreview[], maxRows = 2) {
  const rows = evidenceRows.slice(0, maxRows);
  if (rows.length === 0) return;
  pages.text("Beleg", 9);
  rows.forEach((row) => {
    pages.paragraph(`Quelle ${sourceName(row)}, Seite ${row.page}: ${cleanPdfSnippet(row.quote)}`, 8, 8);
  });
}

function pdfFindingTitle(risk: ReviewPack["top_risks"][number]): string {
  const source = `${risk.risk_category ?? ""} ${risk.risk_statement}`.toLowerCase();
  if (source.includes("qa") && (source.includes("approval") || source.includes("freigabe") || source.includes("genehmigung"))) {
    return "QA-Freigabe vor GMP-Anwendung";
  }
  if (source.includes("affected batch") || source.includes("chargenumfang") || source.includes("retest") || source.includes("a17-26044")) {
    return "Chargenumfang und Retest";
  }
  if (source.includes("comparator") || source.includes("bridge") || source.includes("gerätebrücke") || source.includes("equipment")) {
    return "Übertragbarkeit der Vergleichsdaten";
  }
  if (source.includes("limit") || source.includes("grenzwert") || source.includes("methodenfitness") || source.includes("validierung")) {
    return "Methodenfitness am neuen Grenzwert";
  }
  if (source.includes("training") || source.includes("schulung") || source.includes("sop")) {
    return "SOP-Schulung vor Anwendung";
  }
  return displayReviewValue(risk.risk_category ?? "Risikobefund");
}

function displayOperationalWarning(warning: string): string {
  if (warning === "failed model run affects review coverage") {
    return "Ein Modelllauf konnte nicht vollständig ausgewertet werden; die übrigen Prüfschritte bleiben sichtbar.";
  }
  return displayReviewReason(warning);
}

function sourceName(evidence: { document_name?: string | null; document_id: string }): string {
  return evidence.document_name?.trim() || evidence.document_id;
}

function csvCell(value: string): string {
  const safeValue = value.replace(/^([=+\-@])/, "'$1").replace(/"/g, '""');
  return /[;"\r\n]/.test(safeValue) || /\s/.test(safeValue) ? `"${safeValue}"` : safeValue;
}

function safeFilePart(value: string): string {
  return value.replace(/[^a-zA-Z0-9_-]+/g, "-").replace(/^-+|-+$/g, "") || "case";
}

function unique(values: string[]): string[] {
  return [...new Set(values.map((value) => value.trim()).filter(Boolean))];
}

function addQaStep(pages: PdfPageBuilder, reason: string | null | undefined) {
  const reasons = displayHumanReviewReasons(reason);
  const [firstReason, ...additionalReasons] = reasons;
  pages.paragraph(`QA-Schritt: ${firstReason}`, 10, 0);
  additionalReasons.forEach((additionalReason) => pages.paragraph(`- ${additionalReason}`, 10, 8));
}

function displayHumanReviewReasons(reason: string | null | undefined): string[] {
  if (!reason) return ["Menschliche Prüfung erforderlich."];
  return displayReviewReasons(reason);
}

function cleanPdfSnippet(value: string): string {
  return value
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\?+\s*(Datum|Dokumenttyp|Prozessbereich|Seiten-\/Abschnittsplatzhalter|Status):/g, "$1:")
    .replace(/\s+/g, " ")
    .trim();
}

type PdfLine =
  | { kind: "text"; text: string; fontSize: number; indent: number; gapAfter: number; font: "regular" | "bold" }
  | { kind: "rule"; gapAfter: number };

class PdfPageBuilder {
  private readonly pages: PdfLine[][] = [[]];
  private y = 800;

  kicker(text: string) {
    this.add(text, 8, 0, 4, "bold");
  }

  heading(text: string, fontSize = 18) {
    this.add(text, fontSize, 0, 8, "bold");
  }

  sectionHeading(text: string) {
    this.ensureSpace(50);
    this.add(text, 13, 0, 6, "bold");
  }

  subheading(text: string) {
    this.add(text, 11, 0, 3, "bold");
  }

  findingTitle(text: string) {
    this.ensureSpace(64);
    this.add(text, 11, 0, 3, "bold");
  }

  labelValue(label: string, value: string) {
    this.add(`${label}: ${value}`, 10, 0, 2, "regular");
  }

  rule() {
    this.addRule(9);
  }

  text(text: string, fontSize = 10, indent = 0) {
    this.add(text, fontSize, indent, 2, "regular");
  }

  paragraph(text: string, fontSize = 10, indent = 0) {
    wrapPdfText(text, fontSize, indent).forEach((line, index, lines) => {
      this.add(line, fontSize, indent, index === lines.length - 1 ? 4 : 0, "regular");
    });
  }

  spacer(size = 8) {
    this.y -= size;
  }

  finish(): PdfLine[][] {
    return this.pages;
  }

  private add(text: string, fontSize: number, indent: number, gapAfter: number, font: "regular" | "bold") {
    const lineHeight = fontSize + 4 + gapAfter;
    this.ensureSpace(lineHeight);
    this.pages.at(-1)?.push({ kind: "text", text: pdfText(text), fontSize, indent, gapAfter, font });
    this.y -= lineHeight;
  }

  private addRule(gapAfter: number) {
    this.ensureSpace(14 + gapAfter);
    this.pages.at(-1)?.push({ kind: "rule", gapAfter });
    this.y -= 14 + gapAfter;
  }

  private ensureSpace(requiredHeight: number) {
    if (this.y - requiredHeight < 44) {
      this.pages.push([]);
      this.y = 800;
    }
  }
}

function wrapPdfText(text: string, fontSize: number, indent: number): string[] {
  const maxCharacters = Math.max(28, Math.floor((68 - indent / 8) * (10 / fontSize)));
  const words = pdfText(text).split(/\s+/).filter(Boolean);
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxCharacters && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
  }
  if (current) lines.push(current);
  return lines.length > 0 ? lines : [""];
}

// The page fonts declare /WinAnsiEncoding, and WinAnsi has glyphs for the
// typographic punctuation German QA text actually uses -- they just live in
// 0x80-0x9F, above Latin-1's printable range. These were previously discarded
// by the catch-all below, which printed »laut Antrag ?unverändert?« in a
// customer-facing document. Mapping them to their WinAnsi bytes lets the
// existing fonts render them; the catch-all stays for genuinely unmappable
// characters.
const WINANSI_BYTES: Record<string, string> = {
  "€": "\x80", // €
  "‚": "\x82", // ‚
  "„": "\x84", // „
  "…": "\x85", // …
  "‘": "\x91", // '
  "’": "\x92", // '
  "“": "\x93", // "
  "”": "\x94", // "
  "•": "\x95", // •
  "–": "\x96", // –
  "—": "\x97", // —
  "™": "\x99", // ™
};

function pdfText(value: string): string {
  return value
    .replace(/[€‚„…‘’“”•–—™]/g, (character) => WINANSI_BYTES[character])
    .replace(/[^\x20-\xFF]/g, "?");
}

function buildPdf(pages: PdfLine[][]): Uint8Array {
  const pageCount = Math.max(1, pages.length);
  const pageObjectIds = Array.from({ length: pageCount }, (_, index) => 5 + index * 2);
  const contentObjectIds = pageObjectIds.map((id) => id + 1);
  const objects: string[] = [];
  objects[1] = "<< /Type /Catalog /Pages 2 0 R >>";
  objects[2] = `<< /Type /Pages /Kids [${pageObjectIds.map((id) => `${id} 0 R`).join(" ")}] /Count ${pageCount} >>`;
  objects[3] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>";
  objects[4] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>";

  pages.forEach((page, index) => {
    const pageObjectId = pageObjectIds[index];
    const contentObjectId = contentObjectIds[index];
    let y = 800;
    const commands = page.map((line) => {
      if (line.kind === "rule") {
        const command = `0.78 G 54 ${y - 3} m 541 ${y - 3} l S`;
        y -= 14 + line.gapAfter;
        return command;
      }
      const font = line.font === "bold" ? "F2" : "F1";
      const command = `BT /${font} ${line.fontSize} Tf ${54 + line.indent} ${y} Td (${escapePdfText(line.text)}) Tj ET`;
      y -= line.fontSize + 4 + line.gapAfter;
      return command;
    });
    const stream = commands.join("\n");
    objects[pageObjectId] = `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents ${contentObjectId} 0 R >>`;
    objects[contentObjectId] = `<< /Length ${byteLength(stream)} >>\nstream\n${stream}\nendstream`;
  });

  let pdf = "%PDF-1.4\n";
  const offsets = [0];
  for (let id = 1; id < objects.length; id += 1) {
    offsets[id] = byteLength(pdf);
    pdf += `${id} 0 obj\n${objects[id]}\nendobj\n`;
  }
  const xrefOffset = byteLength(pdf);
  pdf += `xref\n0 ${objects.length}\n0000000000 65535 f \n`;
  for (let id = 1; id < objects.length; id += 1) {
    pdf += `${String(offsets[id]).padStart(10, "0")} 00000 n \n`;
  }
  pdf += `trailer\n<< /Size ${objects.length} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
  return latin1Bytes(pdf);
}

function escapePdfText(value: string): string {
  return value.replace(/([\\()])/g, "\\$1");
}

function byteLength(value: string): number {
  return value.length;
}

function latin1Bytes(value: string): Uint8Array {
  return Uint8Array.from(value, (character) => character.charCodeAt(0));
}
