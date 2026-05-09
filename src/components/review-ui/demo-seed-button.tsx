"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { consultantReviewCopy } from "@/src/lib/review-ui";

export function DemoSeedButton() {
  const router = useRouter();
  const [status, setStatus] = useState<"idle" | "seeding" | "seeded" | "error">("idle");
  const [message, setMessage] = useState("");

  async function seedDemo() {
    setStatus("seeding");
    setMessage("");
    const response = await fetch("/api/review-ui/demo-seed", { method: "POST" });
    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
      setStatus("error");
      setMessage(payload.error ?? consultantReviewCopy.seed.error);
      return;
    }

    setStatus("seeded");
    setMessage(
      payload.created
        ? consultantReviewCopy.seed.created
        : consultantReviewCopy.seed.refreshed
    );
    router.refresh();
  }

  return (
    <div className="flex flex-col items-start gap-2 md:items-end">
      <button
        type="button"
        onClick={seedDemo}
        disabled={status === "seeding"}
        className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {status === "seeding" ? consultantReviewCopy.seed.seeding : consultantReviewCopy.seed.idle}
      </button>
      {message ? (
        <p
          className={`max-w-sm text-xs ${
            status === "error" ? "text-red-700" : "text-emerald-700"
          }`}
        >
          {message}
        </p>
      ) : null}
    </div>
  );
}
