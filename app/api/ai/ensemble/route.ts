/**
 * Ensemble Analysis API
 *
 * Endpoint: POST /api/ai/ensemble
 *
 * Runs all 3 AI models in parallel:
 * - GPT-4o (OpenAI)
 * - Claude (Anthropic)
 * - Gemini 1.5 Pro (Google)
 *
 * Returns agreement scores and canary test results.
 */

import { NextResponse } from "next/server";
import { createEnsembleOrchestrator, type EnsembleResult } from "@/src/lib/agents/ensemble-orchestrator";
import { getRealisticSourceSnippets } from "@/src/lib/mock-documents";
import type { SourceSnippet } from "@/src/lib/agents/types";

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));

    const projectId = body.projectId || "demo-project";
    const changeControlId = body.changeControlId || "CC-2026-014";

    // Load source documents
    const realisticSnippets = getRealisticSourceSnippets();
    const sourceDocuments: SourceSnippet[] = body.sourceDocuments || realisticSnippets;

    // Create ensemble orchestrator
    const orchestrator = createEnsembleOrchestrator();

    // Run ensemble analysis
    const result: EnsembleResult = await orchestrator.runEnsembleAnalysis(
      projectId,
      changeControlId,
      sourceDocuments,
      body.existingRiskItems || []
    );

    // Calculate model performance summary
    const modelSummary = result.modelResults.map(r => ({
      provider: r.provider,
      model: r.model,
      risksFound: r.riskItems.length,
      gapsFound: r.gaps.length,
      processingTimeMs: r.processingTimeMs,
      error: r.error,
    }));

    // Canary test summary
    const canaryPassed = result.canaryResults?.filter(c => c.passed).length || 0;
    const canaryTotal = result.canaryResults?.length || 0;

    return NextResponse.json({
      success: true,
      result: {
        // Agreement analysis
        overallAgreementScore: result.overallAgreementScore,
        riskAgreements: result.riskAgreements,
        highConfidenceItems: result.highConfidenceItems,
        needsReviewItems: result.needsReviewItems,

        // Combined results
        combinedRiskItems: result.combinedRiskItems,
        combinedGaps: result.combinedGaps,

        // Per-model results
        modelResults: result.modelResults,
        modelSummary,

        // Canary tests
        canaryResults: result.canaryResults,
        canaryPassRate: canaryTotal > 0 ? canaryPassed / canaryTotal : 0,

        // Metrics
        totalTokenUsage: result.totalTokenUsage,
        totalProcessingTimeMs: result.totalProcessingTimeMs,
      },
      meta: {
        projectId,
        changeControlId,
        timestamp: new Date().toISOString(),
        modelsUsed: result.modelResults.map(r => r.provider),
      },
    });
  } catch (error) {
    console.error("Ensemble analysis failed:", error);

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
 * GET: Return API info and health check
 */
export async function GET() {
  const hasOpenAI = !!process.env.OPENAI_API_KEY;
  const hasAnthropic = !!process.env.ANTHROPIC_API_KEY;
  const hasGemini = !!process.env.GEMINI_API_KEY;

  const availableModels = [
    hasOpenAI && "GPT-4o",
    hasAnthropic && "Claude",
    hasGemini && "Gemini 1.5 Pro",
  ].filter(Boolean);

  return NextResponse.json({
    endpoint: "/api/ai/ensemble",
    method: "POST",
    description: "Ensemble analysis with GPT-4o, Claude, and Gemini running in parallel",
    health: {
      openai: hasOpenAI ? "configured" : "missing",
      anthropic: hasAnthropic ? "configured" : "missing",
      gemini: hasGemini ? "configured" : "missing",
      ready: availableModels.length >= 2,
    },
    models: availableModels,
    features: [
      "Parallel execution of all available models",
      "Agreement scoring between models",
      "Canary tests for model reliability",
      "Smart routing: high agreement = auto-OK, disagreement = human review",
    ],
    canaryTests: [
      "Missing validation for new threshold",
      "Training gap for operators",
      "Audit trail scope gaps",
      "Batch reconciliation ambiguity",
      "Engineering assessment limitations",
    ],
  });
}
