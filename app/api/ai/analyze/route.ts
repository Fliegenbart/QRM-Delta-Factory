/**
 * Multi-Agent Risk Analysis API
 *
 * Endpoint: POST /api/ai/analyze
 *
 * Runs the full multi-agent workflow:
 * 1. Author (GPT-4o) creates risk drafts
 * 2. Critic (Claude) reviews and finds issues
 * 3. Resolver (GPT-4o) mediates and revises
 */

import { NextResponse } from "next/server";
import { createOrchestrator, type SourceSnippet, type RiskItemDraft } from "@/src/lib/agents";
import { demoProject } from "@/src/lib/demo-data";
import { getRealisticSourceSnippets } from "@/src/lib/mock-documents";

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));

    const projectId = body.projectId || demoProject.id;
    const changeControlId = body.changeControlId || "CC-2026-014";

    // Load source documents (use realistic mock data if not provided)
    // These documents contain intentional issues for the AI to find
    const realisticSnippets = getRealisticSourceSnippets();
    const sourceDocuments: SourceSnippet[] = body.sourceDocuments || realisticSnippets;

    // Existing risk items (for delta analysis)
    const existingRiskItems: RiskItemDraft[] = body.existingRiskItems || [];

    // Create orchestrator with environment API keys
    const orchestrator = createOrchestrator();

    // Run the multi-agent analysis
    const result = await orchestrator.runAnalysis(
      projectId,
      changeControlId,
      sourceDocuments,
      existingRiskItems
    );

    return NextResponse.json({
      success: true,
      result: {
        riskItems: result.finalRiskItems,
        findings: result.allFindings,
        gaps: result.gaps,
        escalatedItems: result.escalatedItems,
        iterationsUsed: result.iterationsUsed,
        conversation: result.agentConversation,
        tokenUsage: result.totalTokenUsage,
        processingTimeMs: result.processingTimeMs,
      },
      meta: {
        projectId,
        changeControlId,
        timestamp: new Date().toISOString(),
        agents: {
          author: process.env.OPENAI_MODEL || "gpt-4o",
          critic: process.env.ANTHROPIC_MODEL || "claude-sonnet-4-20250514",
          resolver: process.env.OPENAI_MODEL || "gpt-4o",
        },
      },
    });
  } catch (error) {
    console.error("Multi-agent analysis failed:", error);

    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    const isApiKeyError = errorMessage.includes("API key") || errorMessage.includes("authentication");

    return NextResponse.json(
      {
        success: false,
        error: errorMessage,
        hint: isApiKeyError
          ? "Check that OPENAI_API_KEY and ANTHROPIC_API_KEY are set in .env"
          : "Check server logs for details",
      },
      { status: isApiKeyError ? 401 : 500 }
    );
  }
}

/**
 * GET: Return API info and health check
 */
export async function GET() {
  const hasOpenAI = !!process.env.OPENAI_API_KEY;
  const hasAnthropic = !!process.env.ANTHROPIC_API_KEY;

  return NextResponse.json({
    endpoint: "/api/ai/analyze",
    method: "POST",
    description: "Multi-agent risk analysis with GPT-4o (Author/Resolver) and Claude (Critic)",
    health: {
      openai: hasOpenAI ? "configured" : "missing",
      anthropic: hasAnthropic ? "configured" : "missing",
      ready: hasOpenAI && hasAnthropic,
    },
    models: {
      author: process.env.OPENAI_MODEL || "gpt-4o",
      critic: process.env.ANTHROPIC_MODEL || "claude-sonnet-4-20250514",
      resolver: process.env.OPENAI_MODEL || "gpt-4o",
    },
    workflow: [
      "1. Author (GPT-4o): Creates initial risk drafts from source documents",
      "2. Critic (Claude): Reviews drafts, verifies claims, finds issues",
      "3. Resolver (GPT-4o): Mediates disagreements, revises or escalates",
      "4. Loop: Repeat 2-3 until acceptable or max iterations reached",
    ],
    requestBody: {
      projectId: "string (optional, defaults to demo project)",
      changeControlId: "string (optional, defaults to CC-2026-014)",
      sourceDocuments: "SourceSnippet[] (optional, defaults to demo snippets)",
      existingRiskItems: "RiskItemDraft[] (optional, for delta analysis)",
    },
  });
}
