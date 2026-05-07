import { NextResponse } from "next/server";
import { demoDocuments, demoGaps, demoProject, demoRiskItems, reviewQueue } from "@/src/lib/demo-data";

export async function GET() {
  return NextResponse.json({
    projects: [
      {
        ...demoProject,
        documentCount: demoDocuments.length,
        riskItemCount: demoRiskItems.length,
        openHighGapCount: demoGaps.filter((gap) => gap.status === "OPEN" && (gap.priority === "HIGH" || gap.priority === "CRITICAL")).length,
        reviewQueueCount: reviewQueue.length
      }
    ]
  });
}

export async function POST(request: Request) {
  const body = await request.json();
  return NextResponse.json(
    {
      project: {
        id: `project-${Date.now()}`,
        methodology: "FMEA",
        scoringModel: "Severity, Occurrence, Detectability, RPN",
        ...body
      },
      auditAction: "PROJECT_CREATED"
    },
    { status: 201 }
  );
}
