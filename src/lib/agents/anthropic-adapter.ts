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
} from "./types";
import {
  CRITIC_SYSTEM_PROMPT,
  DOCUMENT_VERIFICATION_PROMPT,
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
