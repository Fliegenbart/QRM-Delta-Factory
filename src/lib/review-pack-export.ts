import type { ReviewPack } from "@/src/lib/review-ui";

type ExportFormat = "pdf" | "csv";

const csvHeaders = [
  "Prüfpunkt-ID",
  "Risikobeschreibung",
  "Dokument",
  "Seite",
  "Chunk",
  "Zitat",
  "Anforderungen",
  "Verifikationsstatus"
];

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
    row.verifier_status
  ]);

  return `\ufeff${[csvHeaders, ...rows].map((row) => row.map(csvCell).join(";")).join("\r\n")}\r\n`;
}

export function createReviewPackPdf(pack: ReviewPack): Blob {
  const pages = new PdfPageBuilder();
  pages.heading("Pruefmappe");
  pages.text(`Fall: ${pack.document_set_id}`);
  pages.text(`Entscheidung: ${pack.decision.decision}`);
  pages.text(`Hoechste Einstufung: ${pack.decision.max_severity ?? "nicht angegeben"}`);
  pages.text(`Erstellt: ${new Date().toLocaleDateString("de-DE")}`);
  pages.spacer();
  pages.heading("Zusammenfassung", 13);
  pages.paragraph(pack.summary || "Keine Zusammenfassung vorhanden.");

  pages.heading("Pruefpunkte", 13);
  if (pack.top_risks.length === 0) {
    pages.text("Keine Pruefpunkte vorhanden.");
  }
  for (const [index, risk] of pack.top_risks.entries()) {
    pages.subheading(`${index + 1}. ${risk.severity.toUpperCase()} - ${risk.risk_category ?? "Risiko"}`);
    pages.paragraph(risk.risk_statement);
    pages.text(`Anforderungen: ${risk.requirement_references.join(", ") || "nicht zugeordnet"}`);
    pages.text(`Verifikation: ${risk.verifier_status}`);
    pages.text(`Pruefhinweis: ${risk.human_review_reason || "Menschliche Pruefung erforderlich."}`);
    for (const evidence of risk.evidence_quotes) {
      pages.paragraph(`Quelle ${evidence.document_id}, Seite ${evidence.page}: ${evidence.quote}`, 9, 10);
    }
    pages.spacer(4);
  }

  const reasons = unique([
    ...(pack.decision.required_human_review_reasons ?? []),
    ...pack.ood_reasons,
    ...pack.coverage_gap_reasons,
    ...pack.missing_information
  ]);
  if (reasons.length > 0) {
    pages.heading("Offene Punkte", 13);
    reasons.forEach((reason) => pages.paragraph(`- ${reason}`));
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
  const maxCharacters = Math.max(30, Math.floor((82 - indent / 7) * (10 / fontSize)));
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
  objects[3] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>";

  pages.forEach((page, index) => {
    const pageObjectId = pageObjectIds[index];
    const contentObjectId = contentObjectIds[index];
    let y = 800;
    const commands = page.map((line) => {
      const command = `BT /F1 ${line.fontSize} Tf ${42 + line.indent} ${y} Td (${escapePdfText(line.text)}) Tj ET`;
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
