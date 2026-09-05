import { getRequirementReport } from "@/src/lib/review-api";
import { EmptyState, ReviewShell } from "@/src/components/review-ui/review-shell";
import { RequirementReportView } from "@/src/components/review-ui/requirement-report-view";
import { isHiddenDemoDocumentSetId, userFacingReviewLoadError } from "@/src/lib/review-ui";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function RequirementCoveragePage({ params }: PageProps) {
  const { id } = await params;

  if (isHiddenDemoDocumentSetId(id)) {
    return (
      <ReviewShell>
        <EmptyState message="Für diesen Vorgang liegt keine Anforderungsabdeckung vor." />
      </ReviewShell>
    );
  }

  try {
    const report = await getRequirementReport(id);
    return (
      <ReviewShell>
        <RequirementReportView
          report={report}
          reviewPackHref={`/review-ui/document-sets/${encodeURIComponent(id)}/review-pack`}
          retryDocumentSetId={id}
        />
      </ReviewShell>
    );
  } catch (error) {
    return (
      <ReviewShell>
        <EmptyState
          message={
            userFacingReviewLoadError(error instanceof Error ? error.message : "").message
          }
        />
      </ReviewShell>
    );
  }
}
