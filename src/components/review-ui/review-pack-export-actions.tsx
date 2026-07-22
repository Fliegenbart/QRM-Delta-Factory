"use client";

import { Download, FileSpreadsheet } from "lucide-react";
import type { ReviewPack } from "@/src/lib/review-ui";
import {
  buildReviewPackCsv,
  createReviewPackPdf,
  reviewPackExportFileName
} from "@/src/lib/review-pack-export";

export function ReviewPackExportActions({ pack }: { pack: ReviewPack }) {
  return (
    <div className="flex flex-wrap items-center justify-end gap-2">
      <button
        type="button"
        onClick={() => downloadBlob(createReviewPackPdf(pack), reviewPackExportFileName(pack, "pdf"))}
        className="inline-flex h-8 items-center justify-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-2.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--brand)] hover:bg-[var(--brand-soft)]"
      >
        <Download className="h-3.5 w-3.5" aria-hidden />
        Prüfmappe als PDF
      </button>
      <button
        type="button"
        onClick={() =>
          downloadBlob(
            new Blob([buildReviewPackCsv(pack)], { type: "text/csv;charset=utf-8" }),
            reviewPackExportFileName(pack, "csv")
          )
        }
        className="inline-flex h-8 items-center justify-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-2.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--brand)] hover:bg-[var(--brand-soft)]"
      >
        <FileSpreadsheet className="h-3.5 w-3.5" aria-hidden />
        Evidenz als Excel (.csv)
      </button>
    </div>
  );
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}
