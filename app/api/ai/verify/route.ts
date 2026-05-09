/**
 * Document Verification API
 *
 * Endpoint: POST /api/ai/verify
 *
 * Verifies a claim against a source document using:
 * 1. Local keyword matching
 * 2. Claude AI verification (for uncertain cases)
 */

import { NextResponse } from "next/server";
import { createOrchestrator, getDocumentVerifier } from "@/src/lib/agents";

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));

    const { claim, snippetId, useAI = true } = body;

    if (!claim || !snippetId) {
      return NextResponse.json(
        {
          success: false,
          error: "Missing required fields: claim, snippetId",
        },
        { status: 400 }
      );
    }

    const verifier = getDocumentVerifier();
    const localResult = verifier.verifyClaim(claim, snippetId);

    let aiResult = null;

    // Use AI verification for uncertain cases
    if (useAI && (localResult.confidence === "UNVERIFIED" || localResult.confidence === "INFERRED")) {
      try {
        const orchestrator = createOrchestrator();
        const fullResult = await orchestrator.verifyClaimWithAI(claim, snippetId);
        aiResult = fullResult.aiVerification;
      } catch (aiError) {
        console.warn("AI verification failed, using local result only:", aiError);
      }
    }

    return NextResponse.json({
      success: true,
      verification: {
        claim,
        snippetId,
        localResult: {
          confidence: localResult.confidence,
          sourceText: localResult.sourceText,
          note: localResult.verificationNote,
        },
        aiResult: aiResult
          ? {
              confidence: aiResult.confidence,
              sourceText: aiResult.sourceText,
              note: aiResult.verificationNote,
            }
          : null,
        finalConfidence: aiResult?.confidence || localResult.confidence,
      },
    });
  } catch (error) {
    console.error("Verification failed:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

/**
 * GET: Search for documents
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get("q");
  const limit = parseInt(searchParams.get("limit") || "5");

  if (!query) {
    return NextResponse.json({
      endpoint: "/api/ai/verify",
      methods: {
        POST: "Verify a claim against a source snippet",
        GET: "Search for relevant documents (use ?q=query&limit=5)",
      },
    });
  }

  const verifier = getDocumentVerifier();
  const results = verifier.searchDocuments(query, limit);

  return NextResponse.json({
    success: true,
    query,
    results,
  });
}
