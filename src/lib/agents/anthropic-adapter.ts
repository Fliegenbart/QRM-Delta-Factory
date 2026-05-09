/**
 * Anthropic Adapter for Critic Agent
 *
 * Uses Claude for:
 * - Critical review of Author's work
 * - Document verification
 * - Finding gaps and inconsistencies
 */

import Anthropic from "@anthropic-ai/sdk";
import type {
  AgentContext,
  AuthorOutput,
  CriticOutput,
  CriticFinding,
  CriticSeverity,
  TokenUsage,
  VerifiedClaim,
  ClaimConfidence,
  RiskItemDraft,
  GapItem,
} from "./types";
import {
  AUTHOR_SYSTEM_PROMPT,
  CRITIC_SYSTEM_PROMPT,
  DOCUMENT_VERIFICATION_PROMPT,
  buildAuthorPrompt,
  buildCriticPrompt,
} from "./prompts";

// Cost per 1M tokens (Claude Sonnet pricing)
const CLAUDE_SONNET_INPUT_COST_PER_1M = 3.00;
const CLAUDE_SONNET_OUTPUT_COST_PER_1M = 15.00;

export class AnthropicAdapter {
  private client: Anthropic;
  private model: string;

  constructor(apiKey: string, model: string = "claude-sonnet-4-20250514") {
    this.client = new Anthropic({ apiKey });
    this.model = model;
  }

  /**
   * Generate Author-style output (for ensemble comparison)
   * Claude can also act as an Author to provide independent analysis
   */
  async generateCriticAsAuthor(context: AgentContext): Promise<AuthorOutput> {
    const userPrompt = buildAuthorPrompt({
      changeControlSummary: `Project: ${context.projectId}\nChange Control: ${context.changeControlId}`,
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

    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 4000,
      system: AUTHOR_SYSTEM_PROMPT,
      messages: [{ role: "user", content: userPrompt }],
    });

    const content = this.extractTextContent(response.content);
    const parsed = this.parseAuthorResponse(content);
    const usage = this.calculateTokenUsage(response.usage);

    return {
      riskItems: this.mapToRiskItemDrafts(parsed.riskItems || []),
      identifiedGaps: this.mapToGapItems(parsed.gaps || [], "AUTHOR"),
      questionsForSme: parsed.smeQuestions || [],
      processingNotes: `Claude ${this.model} analysis`,
      tokenUsage: usage,
    };
  }

  /**
   * Critic Agent: Review Author's work with ruthless precision
   */
  async generateCriticReview(
    context: AgentContext,
    authorOutput: AuthorOutput
  ): Promise<CriticOutput> {
    const userPrompt = buildCriticPrompt({
      authorDraft: JSON.stringify(authorOutput.riskItems, null, 2),
      sourceSnippets: context.sourceDocuments.map(s => ({
        id: s.id,
        content: s.content,
        documentType: s.documentType,
      })),
    });

    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 4000,
      system: CRITIC_SYSTEM_PROMPT,
      messages: [
        { role: "user", content: userPrompt },
      ],
    });

    const content = this.extractTextContent(response.content);
    const parsed = this.parseJsonFromResponse(content);
    const usage = this.calculateTokenUsage(response.usage);

    // Verify claims against source documents
    const verifiedFindings = await this.verifyFindingsAgainstSources(
      parsed.findings || [],
      authorOutput,
      context
    );

    return {
      findings: verifiedFindings,
      overallAssessment: this.determineOverallAssessment(verifiedFindings),
      commendations: parsed.commendations || [],
      processingNotes: parsed.notes || "",
      tokenUsage: usage,
    };
  }

  /**
   * Verify a specific claim against source documents
   */
  async verifyClaim(
    claim: string,
    sourceSnippet: { id: string; content: string }
  ): Promise<VerifiedClaim> {
    const prompt = `Prüfe ob dieser Claim durch das Source-Dokument belegt ist:

CLAIM: "${claim}"

SOURCE SNIPPET [${sourceSnippet.id}]:
"${sourceSnippet.content}"

Antworte im JSON-Format:
{
  "confidence": "VERIFIED|INFERRED|UNVERIFIED|CONTRADICTED",
  "reasoning": "...",
  "relevantQuote": "..."
}`;

    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 500,
      system: DOCUMENT_VERIFICATION_PROMPT,
      messages: [{ role: "user", content: prompt }],
    });

    const content = this.extractTextContent(response.content);
    const parsed = this.parseVerificationResponse(content);

    return {
      claim,
      sourceSnippetId: sourceSnippet.id,
      sourceText: parsed.relevantQuote || null,
      confidence: (parsed.confidence as ClaimConfidence) || "UNVERIFIED",
      verificationNote: parsed.reasoning || "",
    };
  }

  private parseVerificationResponse(content: string): VerificationResponseSchema {
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[0]);
      } catch {
        // fallback
      }
    }
    return { confidence: "UNVERIFIED", reasoning: content, relevantQuote: null };
  }

  /**
   * Verify findings by checking claims against actual sources
   */
  private async verifyFindingsAgainstSources(
    findings: CriticFindingSchema[],
    authorOutput: AuthorOutput,
    context: AgentContext
  ): Promise<CriticFinding[]> {
    const verifiedFindings: CriticFinding[] = [];

    for (const finding of findings) {
      // If finding is about unverified claims, verify them
      let verificationAttempt: VerifiedClaim | null = null;

      if (finding.category === "UNVERIFIED_CLAIM" && finding.affectedClaims?.length) {
        const claimText = finding.affectedClaims[0];
        const riskItem = authorOutput.riskItems.find(r => r.riskId === finding.riskItemId);
        const relevantClaim = riskItem?.claims.find(c => c.claim === claimText);

        if (relevantClaim?.sourceSnippetId) {
          const sourceSnippet = context.sourceDocuments.find(
            s => s.id === relevantClaim.sourceSnippetId
          );
          if (sourceSnippet) {
            verificationAttempt = await this.verifyClaim(claimText, {
              id: sourceSnippet.id,
              content: sourceSnippet.content,
            });
          }
        }
      }

      verifiedFindings.push({
        riskItemId: finding.riskItemId || "",
        severity: this.mapSeverity(finding.severity),
        category: finding.category || "EVIDENCE_GAP",
        description: finding.description || "",
        suggestedAction: finding.suggestedAction || "",
        affectedClaims: finding.affectedClaims || [],
        verificationAttempt,
      });
    }

    return verifiedFindings;
  }

  // ===========================================================================
  // HELPER METHODS
  // ===========================================================================

  private extractTextContent(content: Anthropic.ContentBlock[]): string {
    return content
      .filter((block): block is Anthropic.TextBlock => block.type === "text")
      .map(block => block.text)
      .join("\n");
  }

  private parseJsonFromResponse(content: string): CriticResponseSchema {
    // Try to extract JSON from the response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[0]);
      } catch {
        // If JSON parsing fails, try to extract structured data
      }
    }

    // Fallback: return empty schema
    return { findings: [], commendations: [], notes: content };
  }

  private calculateTokenUsage(usage: Anthropic.Usage): TokenUsage {
    const input = usage.input_tokens || 0;
    const output = usage.output_tokens || 0;
    const total = input + output;
    const cost = (input / 1_000_000) * CLAUDE_SONNET_INPUT_COST_PER_1M +
                 (output / 1_000_000) * CLAUDE_SONNET_OUTPUT_COST_PER_1M;

    return {
      inputTokens: input,
      outputTokens: output,
      totalTokens: total,
      estimatedCostUsd: Math.round(cost * 10000) / 10000,
    };
  }

  private mapSeverity(severity: string | undefined): CriticSeverity {
    const upper = (severity || "").toUpperCase();
    if (upper === "BLOCKER") return "BLOCKER";
    if (upper === "CONCERN") return "CONCERN";
    return "SUGGESTION";
  }

  private determineOverallAssessment(
    findings: CriticFinding[]
  ): "ACCEPTABLE" | "NEEDS_REVISION" | "MAJOR_ISSUES" {
    const hasBlockers = findings.some(f => f.severity === "BLOCKER");
    const hasConcerns = findings.some(f => f.severity === "CONCERN");

    if (hasBlockers) return "MAJOR_ISSUES";
    if (hasConcerns) return "NEEDS_REVISION";
    return "ACCEPTABLE";
  }

  private parseAuthorResponse(content: string): AuthorResponseSchema {
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[0]);
      } catch {
        // fallback
      }
    }
    return { riskItems: [], gaps: [], smeQuestions: [] };
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
// RESPONSE SCHEMAS
// ===========================================================================

interface CriticResponseSchema {
  findings?: CriticFindingSchema[];
  commendations?: string[];
  notes?: string;
}

interface CriticFindingSchema {
  riskItemId?: string;
  severity?: string;
  category?: "EVIDENCE_GAP" | "LOGIC_FLAW" | "MISSING_RISK" | "SCORE_DISPUTE" | "UNVERIFIED_CLAIM" | "REGULATORY_CONCERN";
  description?: string;
  suggestedAction?: string;
  affectedClaims?: string[];
}

interface VerificationResponseSchema {
  confidence?: string;
  reasoning?: string;
  relevantQuote?: string | null;
}

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
