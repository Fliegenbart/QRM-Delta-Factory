import { ReviewShell } from "@/src/components/review-ui/review-shell";

export default function Loading() {
  return (
    <ReviewShell>
      <div className="animate-pulse space-y-5" aria-label="Wird geladen" role="status">
        <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-5">
          <div className="h-5 w-64 rounded bg-[var(--surface-secondary)]" />
          <div className="mt-4 h-3 w-full max-w-2xl rounded bg-[var(--surface-secondary)]" />
          <div className="mt-2 h-3 w-3/4 max-w-xl rounded bg-[var(--surface-secondary)]" />
        </div>
        <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-5">
          <div className="h-4 w-40 rounded bg-[var(--surface-secondary)]" />
          <div className="mt-4 space-y-3">
            <div className="h-3 w-full rounded bg-[var(--surface-secondary)]" />
            <div className="h-3 w-5/6 rounded bg-[var(--surface-secondary)]" />
            <div className="h-3 w-2/3 rounded bg-[var(--surface-secondary)]" />
          </div>
        </div>
      </div>
    </ReviewShell>
  );
}
