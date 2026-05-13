"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Trash2 } from "lucide-react";

type DeleteDocumentSetButtonProps = {
  documentSetId: string;
};

export function DeleteDocumentSetButton({ documentSetId }: DeleteDocumentSetButtonProps) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function deleteDocumentSet() {
    const confirmed = window.confirm(
      "Diesen Prüffall wirklich löschen? Die hochgeladenen Dokumente und die erzeugte Prüfmappe werden entfernt."
    );
    if (!confirmed) return;

    setIsDeleting(true);
    setError(null);

    try {
      const response = await fetch(`/api/review-ui/document-sets/${encodeURIComponent(documentSetId)}`, {
        method: "DELETE"
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(
          typeof payload.error === "string"
            ? payload.error
            : "Prüffall konnte nicht gelöscht werden."
        );
      }
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Prüffall konnte nicht gelöscht werden.");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <div className="inline-flex flex-col items-end gap-1">
      <button
        type="button"
        onClick={deleteDocumentSet}
        disabled={isDeleting}
        className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-red-200 bg-white text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-red-400/30 dark:bg-slate-900 dark:text-red-300 dark:hover:bg-red-950/30"
        aria-label={`Prüffall ${documentSetId} löschen`}
        title="Prüffall löschen"
      >
        <Trash2 className="h-4 w-4" />
      </button>
      {error ? <span className="max-w-44 text-right text-xs leading-5 text-red-600">{error}</span> : null}
    </div>
  );
}
