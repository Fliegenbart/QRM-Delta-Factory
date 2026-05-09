/**
 * Gemini Adapter for Ensemble Analysis
 *
 * Uses Gemini 1.5 Pro as third opinion in the ensemble
 */

import { GoogleGenerativeAI } from "@google/generative-ai";
import type {
  AgentContext,
  AuthorOutput,
  RiskItemDraft,
  GapItem,
  TokenUsage,
  VerifiedClaim,
} from "./types";
import {
  AUTHOR_SYSTEM_PROMPT,
  buildAuthorPrompt,
} from "./prompts";

// Cost per 1M tokens (Gemini 1.5 Pro pricing)
const GEMINI_INPUT_COST_PER_1M = 1.25;
const GEMINI_OUTPUT_COST_PER_1M = 5.00;

export class GeminiAdapter {
  private client: GoogleGenerativeAI;
  private model: string;

  constructor(apiKey: string, model: string = "gemini-2.0-flash") {
    this.client = new GoogleGenerativeAI(apiKey);
    this.model = model;
  }

  /**
   * Generate risk analysis (same role as Author)
   */
  async generateAuthorDraft(context: AgentContext): Promise<AuthorOutput> {
    const userPrompt = buildAuthorPrompt({
      changeControlSummary: this.buildChangeControlSummary(context),
      sourceSnippets: context.sourceDocuments.map(s => ({
        id: s.id,
        content: s.content,
        documentType: s.documentType,
      })),
      existingRisks: context.existingRiskItems.map(r => ({
        id: r.riskId,
        failureMode: r.failureMode,
      })),
    });

    const model = this.client.getGenerativeModel({
      model: this.model,
      generationConfig: {
        temperature: 0.3,
        maxOutputTokens: 4000,
        responseMimeType: "application/json",
      },
    });

    const fullPrompt = `${AUTHOR_SYSTEM_PROMPT}\n\n${userPrompt}`;

    const result = await model.generateContent(fullPrompt);
    const response = result.response;
    const content = response.text();

    // Parse JSON from response
    let parsed: AuthorResponseSchema;
    try {
      // Gemini sometimes wraps JSON in markdown code blocks
      const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/) ||
                        content.match(/```\s*([\s\S]*?)\s*```/);
      const jsonStr = jsonMatch ? jsonMatch[1] : content;
      parsed = JSON.parse(jsonStr) as AuthorResponseSchema;
    } catch {
      console.error("Failed to parse Gemini response:", content);
      parsed = { riskItems: [], gaps: [], smeQuestions: [] };
    }

    // Estimate token usage (Gemini doesn't always provide exact counts)
    const usage = this.estimateTokenUsage(fullPrompt, content);

    return {
      riskItems: this.mapToRiskItemDrafts(parsed.riskItems || []),
      identifiedGaps: this.mapToGapItems(parsed.gaps || [], "AUTHOR"),
      questionsForSme: parsed.smeQuestions || [],
      processingNotes: `Gemini ${this.model} analysis`,
      tokenUsage: usage,
    };
  }

  // ===========================================================================
  // HELPER METHODS
  // ===========================================================================

  private buildChangeControlSummary(context: AgentContext): string {
    return `Project: ${context.projectId}\nChange Control: ${context.changeControlId}\nIteration: ${context.iterationCount}/${context.maxIterations}`;
  }

  private estimateTokenUsage(input: string, output: string): TokenUsage {
    // Rough estimation: ~4 characters per token
    const inputTokens = Math.ceil(input.length / 4);
    const outputTokens = Math.ceil(output.length / 4);
    const total = inputTokens + outputTokens;
    const cost = (inputTokens / 1_000_000) * GEMINI_INPUT_COST_PER_1M +
                 (outputTokens / 1_000_000) * GEMINI_OUTPUT_COST_PER_1M;

    return {
      inputTokens,
      outputTokens,
      totalTokens: total,
      estimatedCostUsd: Math.round(cost * 10000) / 10000,
    };
  }

  private mapToRiskItemDrafts(items: RiskItemSchema[]): RiskItemDraft[] {
    return items.map(item => ({
      riskId: item.riskId || `RISK-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      processStep: item.processStep || "",
      failureMode: item.failureMode || "",
      potentialCause: item.potentialCause || "",
      potentialEffect: item.potentialEffect || "",
      severity: this.clampScore(item.severity),
      occurrence: this.clampScore(item.occurrence),
      detectability: this.clampScore(item.detectability),
      initialRpn: this.clampScore(item.severity) * this.clampScore(item.occurrence) * this.clampScore(item.detectability),
      existingControls: item.existingControls || [],
      proposedControls: item.proposedControls || [],
      requiredEvidence: item.requiredEvidence || [],
      impactCategories: item.impactCategories || [],
      claims: this.mapToClaims(item.claims || []),
      authorNotes: item.notes || "",
      confidenceLevel: item.confidence || "MEDIUM",
    }));
  }

  private mapToClaims(claims: ClaimSchema[]): VerifiedClaim[] {
    return claims.map(c => ({
      claim: c.claim || "",
      sourceSnippetId: c.sourceId || null,
      sourceText: c.sourceText || null,
      confidence: c.verified ? "VERIFIED" : "UNVERIFIED",
      verificationNote: c.note || "",
    }));
  }

  private mapToGapItems(gaps: GapSchema[], identifiedBy: "AUTHOR" | "CRITIC" | "RESOLVER"): GapItem[] {
    return gaps.map(g => ({
      id: g.id || `GAP-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      riskItemId: g.riskItemId || null,
      priority: g.priority || "MEDIUM",
      category: g.category || "EVIDENCE",
      description: g.description || "",
      suggestedResolution: g.resolution || "",
      identifiedBy,
    }));
  }

  private clampScore(score: number | undefined): number {
    if (!score || isNaN(score)) return 5;
    return Math.max(1, Math.min(10, Math.round(score)));
  }
}

// ===========================================================================
// RESPONSE SCHEMAS (for JSON parsing)
// ===========================================================================

interface AuthorResponseSchema {
  riskItems?: RiskItemSchema[];
  gaps?: GapSchema[];
  smeQuestions?: string[];
  notes?: string;
}

interface RiskItemSchema {
  riskId?: string;
  processStep?: string;
  failureMode?: string;
  potentialCause?: string;
  potentialEffect?: string;
  severity?: number;
  occurrence?: number;
  detectability?: number;
  existingControls?: string[];
  proposedControls?: string[];
  requiredEvidence?: string[];
  impactCategories?: string[];
  claims?: ClaimSchema[];
  notes?: string;
  confidence?: "HIGH" | "MEDIUM" | "LOW";
}

interface ClaimSchema {
  claim?: string;
  sourceId?: string;
  sourceText?: string;
  verified?: boolean;
  note?: string;
}

interface GapSchema {
  id?: string;
  riskItemId?: string;
  priority?: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  category?: "EVIDENCE" | "DOCUMENTATION" | "TRAINING" | "VALIDATION" | "PROCESS";
  description?: string;
  resolution?: string;
}
