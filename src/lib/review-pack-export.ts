import {
  displayReviewReason,
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
    row.document_id,
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
  pages.heading("Prüfmappe");
  pages.text(`Fall: ${pack.document_set_id}`);
  pages.text(`Erstellt: ${new Date().toLocaleDateString("de-DE")}`);
  pages.spacer();
  pages.heading("QA-Entscheidung", 13);
  pages.paragraph(presentation.summary || pack.summary || "Keine Zusammenfassung vorhanden.");

  const canonicalRisks = pack.top_risks.filter(
    (risk) => deriveReviewPackPublication(risk.verifier_status).state === "canonical"
  );
  const qaHints = pack.top_risks.filter(
    (risk) => deriveReviewPackPublication(risk.verifier_status).state === "qa_hint_partial"
  );
  pages.heading("Kernbefunde", 13);
  if (canonicalRisks.length === 0) pages.text("Keine vollständig verifizierten Kernbefunde vorhanden.");
  for (const [index, risk] of canonicalRisks.entries()) {
    pages.subheading(
      `${index + 1}. ${displayReviewValue(risk.severity)} – ${displayReviewValue(risk.risk_category ?? "risk")}`
    );
    pages.paragraph(displayRiskStatement(risk.risk_statement));
    pages.text(`Verifier-Status: ${risk.verifier_status}`);
    pages.text(`QA-Schritt: ${displayHumanReviewReason(risk.human_review_reason)}`);
    pages.spacer(4);
  }

  pages.heading("Hinweise zur QA-Prüfung", 13);
  pages.paragraph("Diese Hinweise sind quellenbezogen, aber noch nicht vollständig verifiziert. QA bewertet sie vor einer Freigabe.");
  if (qaHints.length === 0) pages.text("Keine nicht-kanonischen QA-Hinweise vorhanden.");
  for (const [index, risk] of qaHints.entries()) {
    pages.subheading(`${index + 1}. Hinweis – ${displayReviewValue(risk.severity)}`);
    pages.paragraph(displayRiskStatement(risk.risk_statement));
    pages.text(`Verifier-Status: ${risk.verifier_status}`);
    pages.text(`QA-Schritt: ${displayHumanReviewReason(risk.human_review_reason)}`);
    pages.spacer(4);
  }

  if (presentation.operationalWarnings.length > 0 || presentation.modelCoverageStatus) {
    pages.heading("Technische Hinweise", 13);
    if (presentation.modelCoverageStatus) {
      pages.paragraph(`Technische Abdeckung: ${presentation.modelCoverageStatus}`);
    }
    presentation.operationalWarnings.forEach((warning) => pages.paragraph(`- ${warning}`));
  }

  const reasons = unique([
    ...(pack.decision.required_human_review_reasons ?? []),
    ...pack.ood_reasons,
    ...pack.coverage_gap_reasons,
    ...pack.missing_information
  ]);
  if (reasons.length > 0) {
    pages.heading("Offene Punkte", 13);
    reasons.forEach((reason) => pages.paragraph(`- ${displayReviewReason(reason)}`));
  }

  pages.heading("Evidenzanhang", 13);
  if (pack.evidence_table.length === 0) {
    pages.text("Keine Evidenzstellen vorhanden.");
  }
  for (const evidence of pack.evidence_table) {
    pages.paragraph(
      `Quelle ${evidence.document_id}, Seite ${evidence.page}: ${evidence.quote}`,
      9,
      0
    );
  }

  return new Blob([new Uint8Array(buildPdf(pages.finish()))], { type: "application/pdf" });
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

function displayHumanReviewReason(reason: string | null | undefined): string {
  if (!reason) return "Menschliche Prüfung erforderlich.";
  return displayReviewReason(reason);
}

type PdfLine = { text: string; fontSize: number; indent: number; gapAfter: number };

class PdfPageBuilder {
  private readonly pages: PdfLine[][] = [[]];
  private y = 800;

  heading(text: string, fontSize = 18) {
    this.add(text, fontSize, 0, 8);
  }

  subheading(text: string) {
    this.add(text, 11, 0, 3);
  }

  text(text: string, fontSize = 10, indent = 0) {
    this.add(text, fontSize, indent, 2);
  }

  paragraph(text: string, fontSize = 10, indent = 0) {
    wrapPdfText(text, fontSize, indent).forEach((line, index, lines) => {
      this.add(line, fontSize, indent, index === lines.length - 1 ? 4 : 0);
    });
  }

  spacer(size = 8) {
    this.y -= size;
  }

  finish(): PdfLine[][] {
    return this.pages;
  }

  private add(text: string, fontSize: number, indent: number, gapAfter: number) {
    const lineHeight = fontSize + 4 + gapAfter;
    if (this.y - lineHeight < 44) {
      this.pages.push([]);
      this.y = 800;
    }
    this.pages.at(-1)?.push({ text: pdfText(text), fontSize, indent, gapAfter });
    this.y -= lineHeight;
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

function pdfText(value: string): string {
  return value
    .replace(/[–—]/g, "-")
    .replace(/€/g, "EUR")
    .replace(/[^\x20-\xFF]/g, "?");
}

function buildPdf(pages: PdfLine[][]): Uint8Array {
  const pageCount = Math.max(1, pages.length);
  const pageObjectIds = Array.from({ length: pageCount }, (_, index) => 4 + index * 2);
  const contentObjectIds = pageObjectIds.map((id) => id + 1);
  const objects: string[] = [];
  objects[1] = "<< /Type /Catalog /Pages 2 0 R >>";
  objects[2] = `<< /Type /Pages /Kids [${pageObjectIds.map((id) => `${id} 0 R`).join(" ")}] /Count ${pageCount} >>`;
  objects[3] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>";

  pages.forEach((page, index) => {
    const pageObjectId = pageObjectIds[index];
    const contentObjectId = contentObjectIds[index];
    let y = 800;
    const commands = page.map((line) => {
      const command = `BT /F1 ${line.fontSize} Tf ${54 + line.indent} ${y} Td (${escapePdfText(line.text)}) Tj ET`;
      y -= line.fontSize + 4 + line.gapAfter;
      return command;
    });
    const stream = commands.join("\n");
    objects[pageObjectId] = `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents ${contentObjectId} 0 R >>`;
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
