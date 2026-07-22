"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle2 } from "lucide-react";
import { demoDecisionStorageKey, type DemoReviewCase } from "@/src/lib/review-ui";

export function DemoDecisionDesk({ demoCase }: { demoCase: DemoReviewCase }) {
  const [selectedAction, setSelectedAction] = useState(demoCase.decisionActions[0] ?? "");
  const [savedAction, setSavedAction] = useState("");
  const storageKey = demoDecisionStorageKey(demoCase.id);

  useEffect(() => {
    const storedAction = window.localStorage.getItem(storageKey);
    if (storedAction && demoCase.decisionActions.includes(storedAction)) {
      setSelectedAction(storedAction);
      setSavedAction(storedAction);
    }
  }, [demoCase.decisionActions, storageKey]);

  function saveDemoDecision() {
    if (!selectedAction) return;
    window.localStorage.setItem(storageKey, selectedAction);
    setSavedAction(selectedAction);
  }

  return (
    <aside className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)]">
      <div className="border-b border-[var(--border-default)] px-4 py-3">
        <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
          Decision Desk
        </div>
        <div className="mt-1 text-[14px] font-medium text-[var(--text-primary)]">QA muss entscheiden</div>
      </div>
      <div className="divide-y divide-[var(--border-muted)] px-4">
        {demoCase.decisionActions.map((action) => {
          const selected = action === selectedAction;
          return (
            <button
              key={action}
              type="button"
              aria-pressed={selected}
              onClick={() => setSelectedAction(action)}
              className={`flex w-full items-center justify-between gap-3 py-3 text-left text-[13px] font-medium transition-colors ${
                selected
                  ? "text-[var(--brand)]"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              }`}
            >
              <span>{action}</span>
              <span
                className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border ${
                  selected
                    ? "border-[var(--brand)] bg-[var(--brand-soft)] text-[var(--brand)]"
                    : "border-[var(--border-strong)] text-transparent"
                }`}
              >
                <CheckCircle2 className="h-3.5 w-3.5" aria-hidden />
              </span>
            </button>
          );
        })}
      </div>
      <div className="border-t border-[var(--border-default)] px-4 py-3">
        <button
          type="button"
          onClick={saveDemoDecision}
          disabled={!selectedAction}
          className="w-full rounded-md bg-[var(--brand)] px-3 py-2 text-[13px] font-semibold text-white transition hover:bg-[var(--brand-strong)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          Demo-Entscheidung speichern
        </button>
        {savedAction ? (
          <p role="status" className="mt-2 text-[12px] font-medium text-[var(--brand-strong)]">
            Demo-Auswahl gespeichert: {savedAction}
          </p>
        ) : null}
      </div>
      <div className="border-t border-[var(--border-default)] px-4 py-3 text-[12px] leading-5 text-[var(--text-secondary)]">
        <span className="font-semibold text-[var(--text-primary)]">Demo-Auswahl:</span>{" "}
        {selectedAction || "Noch keine Aktion ausgewählt"}. Nur Demo: Die Auswahl wird in diesem Browser
        gespeichert, aber nicht als Auditprotokoll oder echte QA-Freigabe verbucht.
      </div>
    </aside>
  );
}
