import { NextResponse } from "next/server";
import { authenticateDemoUser } from "@/src/lib/auth";

export async function POST(request: Request) {
  const body = await request.json();
  const user = authenticateDemoUser(body.email, body.password);
  if (!user) return NextResponse.json({ error: "Invalid demo credentials" }, { status: 401 });
  return NextResponse.json({ user });
}
