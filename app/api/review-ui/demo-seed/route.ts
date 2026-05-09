import { NextResponse } from "next/server";
import { seedDemoData } from "@/src/lib/review-api";

export async function POST() {
  try {
    const result = await seedDemoData();
    return NextResponse.json(result, { status: result.created ? 201 : 200 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Demo seed failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
