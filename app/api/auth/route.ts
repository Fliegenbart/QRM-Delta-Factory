import { NextResponse } from "next/server";
import { authenticateLocalUser } from "@/src/lib/auth";

export async function POST(request: Request) {
  const body = await request.json();
  const user = authenticateLocalUser(body.email, body.password);
  if (!user) return NextResponse.json({ error: "Local password login is disabled. Use the backend API-key protected review flow." }, { status: 401 });
  return NextResponse.json({ user });
}
