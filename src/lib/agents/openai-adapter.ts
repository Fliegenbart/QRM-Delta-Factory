/**
 * OpenAI Adapter for Author and Resolver Agents
 *
 * Uses GPT-4o for:
 * - Author: Creating initial risk drafts
 * - Resolver: Mediating between Author and Critic
 */

import OpenAI from "openai";
import type {
  AgentContext,
  AuthorOutput,
  ResolverOutput,
  RiskItemDraft,
  GapItem,
  ResolverDecision,
  TokenUsage,
  CriticOutput,
  VerifiedClaim,
} from "./types";
import {
  AUTHOR_SYSTEM_PROMPT,
  RESOLVER_SYSTEM_PROMPT,
  buildAuthorPrompt,
  buildResolverPrompt,
} from "./prompts";

// Cost per 1M tokens (GPT-4o pricing as of 2024)
const GPT4O_INPUT_COST_PER_1M = 2.50;
const GPT4O_OUTPUT_COST_PER_1M = 10.00;

export class OpenAIAdapter {
  private client: OpenAI;
  private model: string;

  constructor(apiKey: string, model: string = "gpt-4o") {
    this.client = new OpenAI({ apiKey });
    this.model = model;
  }

  /**
   * Author Agent: Generate initial risk item drafts
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

    const response = await this.client.chat.completions.create({
      model: this.model,
      messages: [
        { role: "system", content: AUTHOR_SYSTEM_PROMPT },
        { role: "user", content: userPrompt },
      ],
      response_format: { type: "json_object" },
      temperature: 0.3, // Lower temperature for more consistent analysis
      max_tokens: 4000,
    });

    const content = response.choices[0]?.message?.content || "{}";
    const parsed = JSON.parse(content) as AuthorResponseSchema;
    const usage = this.calculateTokenUsage(response.usage);

    return {
      riskItems: this.mapToRiskItemDrafts(parsed.riskItems || []),
      identifiedGaps: this.mapToGapItems(parsed.gaps || [], "AUTHOR"),
      questionsForSme: parsed.smeQuestions || [],
      processingNotes: parsed.notes || "",
      tokenUsage: usage,
    };
  }

  /**
   * Resolver Agent: Mediate between Author and Critic
   */
  async generateResolverDecision(
    context: AgentContext,
    authorOutput: AuthorOutput,
    criticOutput: CriticOutput
  ): Promise<ResolverOutput> {
    const userPrompt = buildResolverPrompt({
      authorDraft: JSON.stringify(authorOutput.riskItems, null, 2),
      criticFindings: JSON.stringify(criticOutput.findings, null, 2),
      sourceSnippets: context.sourceDocuments.map(s => ({
        id: s.id,
        content: s.content,
        documentType: s.documentType,
      })),
      iterationCount: context.iterationCount,
    });

    const response = await this.client.chat.completions.create({
      model: this.model,
      messages: [
        { role: "system", content: RESOLVER_SYSTEM_PROMPT },
        { role: "user", content: userPrompt },
      ],
      response_format: { type: "json_object" },
      temperature: 0.2, // Very low temperature for consistent decisions
      max_tokens: 4000,
    });

    const content = response.choices[0]?.message?.content || "{}";
    const parsed = JSON.parse(content) as ResolverResponseSchema;
    const usage = this.calculateTokenUsage(response.usage);

    const decisions = this.mapToResolverDecisions(parsed.decisions || []);
    const escalatedItems = decisions
      .filter(d => d.decision === "ESCALATE_TO_HUMAN")
      .map(d => d.riskItemId);

    // Check if another loop is needed
    const hasUnresolvedBlockers = criticOutput.findings.some(
      f => f.severity === "BLOCKER" &&
           !decisions.find(d => d.riskItemId === f.riskItemId && d.decision === "ACCEPT")
    );
    const requiresAnotherLoop = hasUnresolvedBlockers && context.iterationCount < context.maxIterations;

    return {
      decisions,
      revisedRiskItems: this.mapToRiskItemDrafts(parsed.revisedItems || []),
      escalatedItems,
      responseToColleague: parsed.colleagueResponse || "Danke für das gründliche Review!",
      requiresAnotherLoop,
      tokenUsage: usage,
    };
  }

  // ===========================================================================
  // HELPER METHODS
  // ===========================================================================

  private buildChangeControlSummary(context: AgentContext): string {
    return `Project: ${context.projectId}\nChange Control: ${context.changeControlId}\nIteration: ${context.iterationCount}/${context.maxIterations}`;
  }

  private calculateTokenUsage(usage: OpenAI.CompletionUsage | undefined): TokenUsage {
    const input = usage?.prompt_tokens || 0;
    const output = usage?.completion_tokens || 0;
    const total = input + output;
    const cost = (input / 1_000_000) * GPT4O_INPUT_COST_PER_1M +
                 (output / 1_000_000) * GPT4O_OUTPUT_COST_PER_1M;

    return {
      inputTokens: input,
      outputTokens: output,
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

  private mapToResolverDecisions(decisions: DecisionSchema[]): ResolverDecision[] {
    return decisions.map(d => ({
      riskItemId: d.riskItemId || "",
      decision: d.decision || "ESCALATE_TO_HUMAN",
      originalClaim: d.originalClaim || null,
      criticFinding: d.criticFinding || null,
      resolution: d.resolution || "",
      revisedContent: d.revisedContent || null,
      escalationReason: d.escalationReason || null,
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

interface ResolverResponseSchema {
  decisions?: DecisionSchema[];
  revisedItems?: RiskItemSchema[];
  colleagueResponse?: string;
}

interface DecisionSchema {
  riskItemId?: string;
  decision?: "ACCEPT" | "REVISE" | "ESCALATE_TO_HUMAN";
  originalClaim?: string;
  criticFinding?: string;
  resolution?: string;
  revisedContent?: Partial<RiskItemDraft>;
  escalationReason?: string;
}
