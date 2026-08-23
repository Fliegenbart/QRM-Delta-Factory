import {
  REQUIREMENT_STATUS_LABELS,
  REQUIREMENT_STATUS_ORDER,
  evidenceLocationLabel,
  requirementConfidenceNotes,
  requirementCoverageProgress,
  type RequirementCoverageReport,
  type RequirementVerdictRow
} from "@/src/lib/review-ui";
import {
  buildPdfDocument,
  cleanExportSnippet,
  csvDocument,
  PdfPageBuilder,
  safeFilePart
} from "@/src/lib/review-pack-export";

/**
 * Export of the coverage report -- the artifact that goes into the file.
 *
 * Deliberately the same shape as the on-screen report: one row per obligation,
 * grouped by what the reviewer must do about it, each row carrying its source
 * in the rulebook and either its verified quote or the gap that remains. An
 * auditor reading the PDF alone can tell which obligations were checked, which
 * are settled, and on what evidence -- that completeness is the point.
 */

export function requirementReportFileName(
  report: RequirementCoverageReport,
  format: "pdf" | "csv"
): string {
  const caseId = safeFilePart(report.document_set_id);
  return format === "pdf"
    ? `anforderungsabdeckung-${caseId}.pdf`
    : `anforderungsabdeckung-${caseId}.csv`;
}

const CSV_HEADERS = [
  "Anforderung",
  "Titel",
  "Quelle",
  "Abschnitt",
  "Status",
  "Schweregrad",
  "Bewertung",
  "Dokument",
  "Seite",
  "Zitat",
  "Sicherheitsvermerke"
];

export function buildRequirementReportCsv(report: RequirementCoverageReport): string {
  const rows: string[][] = [];
  for (const row of orderedRows(report)) {
    const notes = requirementConfidenceNotes(row).join(" | ");
    if (row.evidence.length === 0) {
      rows.push([
        row.requirement_id,
        row.requirement_title ?? "",
        row.source_name,
        row.section,
        REQUIREMENT_STATUS_LABELS[row.published_status],
        row.severity ?? "",
        cleanExportSnippet(row.rationale),
        "",
        "",
        "",
        notes
      ]);
      continue;
    }
    // One line per quote, so a spreadsheet filter over evidence works the way
    // it does for the finding pack's evidence table.
    for (const item of row.evidence) {
      rows.push([
        row.requirement_id,
        row.requirement_title ?? "",
        row.source_name,
        row.section,
        REQUIREMENT_STATUS_LABELS[row.published_status],
        row.severity ?? "",
        cleanExportSnippet(row.rationale),
        item.document_name || item.document_id,
        String(item.page),
        cleanExportSnippet(item.quote),
        notes
      ]);
    }
  }
  return csvDocument(CSV_HEADERS, rows);
}

export function createRequirementReportPdf(report: RequirementCoverageReport): Blob {
  const progress = requirementCoverageProgress(report);
  const builder = new PdfPageBuilder();

  builder.kicker("PHARMA QRM · ANFORDERUNGSABDECKUNG");
  builder.heading("Anforderungsabdeckung");
  builder.labelValue("Vorgang", report.document_set_id);
  builder.labelValue("Erstellt", formatTimestamp(report.created_at));
  builder.labelValue("Prüfstand", report.engine_version);
  builder.rule();

  builder.paragraph(
    "Jede Anforderung des hinterlegten Regelwerks ist genau einmal beantwortet. " +
      "Die Vollständigkeit dieses Berichts ist damit nicht behauptet, sondern " +
      "seine Struktur. Jede Zeile nennt ihre Quelle im Regelwerk und trägt " +
      "entweder ihren geprüften Beleg oder die Lücke, die offen bleibt."
  );
  builder.labelValue("Anforderungen insgesamt", String(progress.total));
  builder.labelValue("Prüfung erforderlich", String(progress.needsAttention));
  builder.labelValue("Ohne Befund", String(progress.answered));
  if (report.failed_model_call_count > 0) {
    builder.labelValue(
      "Fehlgeschlagene Prüfschritte",
      `${report.failed_model_call_count} — betroffene Anforderungen stehen als unklar`
    );
  }
  builder.rule();

  for (const status of REQUIREMENT_STATUS_ORDER) {
    const rows = report.verdicts.filter((row) => row.published_status === status);
    if (rows.length === 0) continue;
    builder.sectionHeading(`${REQUIREMENT_STATUS_LABELS[status]} (${rows.length})`);
    for (const row of rows) {
      writeRow(builder, row);
    }
    builder.spacer(6);
  }

  return buildPdfDocument(builder.finish());
}

function writeRow(builder: PdfPageBuilder, row: RequirementVerdictRow) {
  builder.findingTitle(row.requirement_title ?? row.requirement_id);
  builder.labelValue("Quelle", `${row.source_name}, Abschnitt ${row.section}`);
  if (row.severity) {
    builder.labelValue("Schweregrad", row.severity);
  }
  builder.paragraph(cleanExportSnippet(row.requirement_text), 9);
  builder.paragraph(cleanExportSnippet(row.rationale));

  for (const item of row.evidence) {
    builder.paragraph(`„${cleanExportSnippet(item.quote)}"`, 9, 12);
    builder.text(evidenceLocationLabel(item), 8, 12);
  }
  if (
    row.evidence.length === 0 &&
    (row.published_status === "violated" || row.published_status === "unclear")
  ) {
    builder.text("Kein prüfbares Zitat verblieben.", 9, 12);
  }

  for (const note of requirementConfidenceNotes(row)) {
    builder.text(`· ${cleanExportSnippet(note)}`, 8, 12);
  }
  builder.spacer(4);
}

function orderedRows(report: RequirementCoverageReport): RequirementVerdictRow[] {
  return REQUIREMENT_STATUS_ORDER.flatMap((status) =>
    report.verdicts.filter((row) => row.published_status === status)
  );
}

function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString("de-DE");
}
