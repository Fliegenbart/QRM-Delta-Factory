import { NextResponse } from "next/server";
import { generateValidationPack } from "@/src/lib/validation-pack";

export async function GET() {
  return NextResponse.json({
    disclosure: "Draft templates only. Production use requires formal validation under the regulated company's quality system.",
    artifacts: generateValidationPack("Pharma AI Risk Orchestration Backend")
  });
}
