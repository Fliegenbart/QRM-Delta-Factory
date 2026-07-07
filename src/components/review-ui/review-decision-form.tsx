"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { consultantReviewCopy, decisionOptions, type ReviewDecisionValue } from "@/src/lib/review-ui";

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    const detail = body?.error ?? body?.detail;
    if (typeof detail === "string" && detail && detail !== "Not Found") {
      return detail;
    }
  } catch {
    // Non-JSON body — fall through to the generic message.
  }
  if (response.status >= 500 || response.status === 404) {
    return "Die Entscheidung konnte nicht gespeichert werden — der Prüfdienst ist gerade nicht erreichbar. Bitte versuchen Sie es erneut.";
  }
  return "Die Entscheidung konnte nicht gespeichert werden. Bitte prüfen Sie die Eingaben und versuchen Sie es erneut.";
}

export function ReviewDecisionForm({ findingId }: { findingId: string }) {
  const router = useRouter();
  const [reviewerId, setReviewerId] = useState("");
  const [decision, setDecision] = useState<ReviewDecisionValue>("confirm");
  const [rationale, setRationale] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [message, setMessage] = useState("");

  async function submitDecision(nextDecision: ReviewDecisionValue) {
    setDecision(nextDecision);
    const trimmedRationale = rationale.trim();
    if (!trimmedRationale) {
      setStatus("error");
      setMessage(consultantReviewCopy.decision.rationaleRequired);
      return;
    }

    setStatus("saving");
    setMessage("");

    try {
      const response = await fetch(`/api/review-ui/findings/${findingId}/review-decision`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          ...(reviewerId.trim() ? { reviewerId: reviewerId.trim() } : {}),
          decision: nextDecision,
          rationale: trimmedRationale
        })
      });

      if (!response.ok) {
        setStatus("error");
        setMessage(await readErrorMessage(response));
        return;
      }

      setStatus("saved");
      setMessage(consultantReviewCopy.decision.savedMessage);
      router.refresh();
    } catch {
      setStatus("error");
      setMessage(
        "Keine Verbindung zum Server — die Entscheidung wurde nicht gespeichert. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut."
      );
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-[220px_1fr]">
        <label className="text-sm font-medium text-[var(--text-secondary)]">
          {consultantReviewCopy.decision.reviewerId}
          <input
            className="mt-1 h-10 w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 text-sm text-[var(--text-primary)] outline-none focus:ring-4 focus:ring-[var(--brand-ring)]"
            value={reviewerId}
            onChange={(event) => setReviewerId(event.target.value)}
            placeholder="Name oder Kürzel"
          />
        </label>
        <label className="text-sm font-medium text-[var(--text-secondary)]">
          {consultantReviewCopy.decision.rationale}
          <textarea
            className="mt-1 min-h-28 w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-3 py-2 text-sm leading-6 text-[var(--text-primary)] outline-none focus:ring-4 focus:ring-[var(--brand-ring)]"
            value={rationale}
            onChange={(event) => setRationale(event.target.value)}
            placeholder={consultantReviewCopy.decision.placeholder}
          />
        </label>
      </div>

      <div className="flex flex-wrap gap-2">
        {decisionOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => submitDecision(option.value)}
            disabled={status === "saving"}
            className={`rounded-md border px-4 py-2 text-sm font-semibold transition ${
              decision === option.value
                ? "border-[var(--brand)] bg-[var(--brand)] text-white"
                : "border-[var(--border-default)] bg-[var(--surface-primary)] text-[var(--text-primary)] hover:border-[var(--brand)] hover:bg-[var(--brand-soft)]"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      {message ? (
        <div
          role="status"
          aria-live="polite"
          className={`rounded-md border px-4 py-3 text-sm ${
            status === "error"
              ? "border-[var(--severity-critical)] bg-[var(--severity-critical-soft)] text-[var(--severity-critical)]"
              : "border-[var(--brand)] bg-[var(--brand-soft)] text-[var(--text-primary)]"
          }`}
        >
          {message}
        </div>
      ) : null}
    </div>
  );
}
