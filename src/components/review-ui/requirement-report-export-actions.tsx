"use client";

import { Download, FileSpreadsheet } from "lucide-react";
import type { RequirementCoverageReport } from "@/src/lib/review-ui";
import {
  buildRequirementReportCsv,
  createRequirementReportPdf,
  requirementReportFileName
} from "@/src/lib/requirement-report-export";

export function RequirementReportExportActions({
  report
}: {
  report: RequirementCoverageReport;
}) {
  return (
    <div className="flex flex-wrap items-center justify-end gap-2">
      <button
        type="button"
        onClick={() =>
          downloadBlob(
            createRequirementReportPdf(report),
            requirementReportFileName(report, "pdf")
          )
        }
        className="inline-flex h-8 items-center justify-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-2.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--brand)] hover:bg-[var(--brand-soft)]"
      >
        <Download className="h-3.5 w-3.5" aria-hidden />
        Abdeckung als PDF
      </button>
      <button
        type="button"
        onClick={() =>
          downloadBlob(
            new Blob([buildRequirementReportCsv(report)], {
              type: "text/csv;charset=utf-8"
            }),
            requirementReportFileName(report, "csv")
          )
        }
        className="inline-flex h-8 items-center justify-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-2.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--brand)] hover:bg-[var(--brand-soft)]"
      >
        <FileSpreadsheet className="h-3.5 w-3.5" aria-hidden />
        Abdeckung als Excel (.csv)
      </button>
    </div>
  );
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
