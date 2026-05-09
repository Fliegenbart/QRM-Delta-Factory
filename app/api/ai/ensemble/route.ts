import { NextResponse } from "next/server";

const message =
  "Legacy ensemble analysis is retired. The project is moving to the backend-first evidence orchestration process with claim ledger, verifier gates, conservative aggregation, and human review packs.";

export async function GET() {
  return NextResponse.json({ retired: true, message }, { status: 410 });
}

export async function POST() {
  return NextResponse.json({ retired: true, message }, { status: 410 });
}
