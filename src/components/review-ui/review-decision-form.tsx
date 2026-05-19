"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { consultantReviewCopy, decisionOptions, type ReviewDecisionValue } from "@/src/lib/review-ui";

export function ReviewDecisionForm({ findingId }: { findingId: string }) {
  const router = useRouter();
  const [reviewerId, setReviewerId] = useState("reviewer_qa_1");
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

    const response = await fetch(`/api/review-ui/findings/${findingId}/review-decision`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        reviewerId,
        decision: nextDecision,
        rationale: trimmedRationale
      })
    });

    if (!response.ok) {
      setStatus("error");
      setMessage(await response.text());
      return;
    }

    setStatus("saved");
    setMessage(consultantReviewCopy.decision.savedMessage);
    router.refresh();
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-[220px_1fr]">
        <label className="text-sm font-medium text-slate-700 dark:text-slate-200">
          {consultantReviewCopy.decision.reviewerId}
          <input
            className="mt-1 h-11 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-950 dark:border-white/10 dark:bg-slate-900 dark:text-white"
            value={reviewerId}
            onChange={(event) => setReviewerId(event.target.value)}
          />
        </label>
        <label className="text-sm font-medium text-slate-700 dark:text-slate-200">
          {consultantReviewCopy.decision.rationale}
          <textarea
            className="mt-1 min-h-24 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm leading-6 text-slate-950 dark:border-white/10 dark:bg-slate-900 dark:text-white"
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
            className={`rounded-xl border px-4 py-2 text-sm font-semibold transition ${
              decision === option.value
                ? "border-teal-600 bg-teal-600 text-white"
                : "border-slate-200 bg-white text-slate-800 hover:border-teal-300 dark:border-white/10 dark:bg-slate-900 dark:text-slate-100 dark:hover:border-teal-400"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      {message ? (
        <div
          className={`rounded-xl border px-4 py-3 text-sm ${
            status === "error"
              ? "border-red-200 bg-red-50 text-red-800"
              : "border-emerald-200 bg-emerald-50 text-emerald-800"
          }`}
        >
          {message}
        </div>
      ) : null}
    </div>
  );
}
