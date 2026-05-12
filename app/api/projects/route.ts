import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    projects: []
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
