/**
 * Ensemble Orchestrator
 *
 * Runs multiple AI models in parallel and calculates agreement scores.
 * Disagreement = Signal for human review
 *
 * Models:
 * - GPT-4o (OpenAI)
 * - Claude (Anthropic)
 * - Gemini 1.5 Pro (Google)
 */

import { OpenAIAdapter } from "./openai-adapter";
import { AnthropicAdapter } from "./anthropic-adapter";
import { GeminiAdapter } from "./gemini-adapter";
import type {
  AgentContext,
  AuthorOutput,
  RiskItemDraft,
  GapItem,
  TokenUsage,
  SourceSnippet,
} from "./types";

// =============================================================================
// TYPES
// =============================================================================

export type ModelProvider = "openai" | "anthropic" | "gemini";

export interface ModelResult {
  provider: ModelProvider;
  model: string;
  riskItems: RiskItemDraft[];
  gaps: GapItem[];
  tokenUsage: TokenUsage;
  processingTimeMs: number;
  error?: string;
}

export interface RiskAgreement {
  riskId: string;
  failureMode: string;
  foundBy: ModelProvider[];
  agreementScore: number; // 0-1: percentage of models that found this risk
  severityScores: { provider: ModelProvider; severity: number }[];
  severityAgreement: number; // 0-1: how close are severity scores
  needsHumanReview: boolean;
  reviewReason?: string;
}

export interface EnsembleResult {
  modelResults: ModelResult[];
  riskAgreements: RiskAgreement[];
  combinedRiskItems: RiskItemDraft[];
  combinedGaps: GapItem[];
  overallAgreementScore: number;
  highConfidenceItems: string[]; // Risk IDs with high agreement
  needsReviewItems: string[]; // Risk IDs needing human review
  totalTokenUsage: TokenUsage;
  totalProcessingTimeMs: number;
  canaryResults?: CanaryTestResult[];
}

export interface CanaryTestResult {
  canaryId: string;
  expectedRisk: string;
  foundBy: ModelProvider[];
  passed: boolean;
}

export interface EnsembleConfig {
  openaiApiKey?: string;
  anthropicApiKey?: string;
  geminiApiKey?: string;
  openaiModel?: string;
  anthropicModel?: string;
  geminiModel?: string;
  agreementThreshold?: number; // Default 0.67 (2/3 agreement)
  severityTolerrance?: number; // Default 2 (scores within 2 points = agree)
}

// =============================================================================
// CANARY TESTS - Known risks that MUST be found
// =============================================================================

export const CANARY_RISKS = [
  {
    id: "CANARY-001",
    expectedRisk: "Missing validation evidence for new threshold 0.72",
    keywords: ["validation", "0.72", "threshold", "missing", "evidence"],
  },
  {
    id: "CANARY-002",
    expectedRisk: "Training gap for operators on new threshold",
    keywords: ["training", "operator", "gap", "curriculum"],
  },
  {
    id: "CANARY-003",
    expectedRisk: "Audit trail review scope does not cover threshold changes",
    keywords: ["audit", "trail", "scope", "threshold"],
  },
  {
    id: "CANARY-004",
    expectedRisk: "Batch reconciliation formula ambiguity",
    keywords: ["batch", "reconciliation", "formula", "ambiguous", "unclear"],
  },
  {
    id: "CANARY-005",
    expectedRisk: "Engineering assessment based on modeling only, not physical testing",
    keywords: ["engineering", "modeling", "physical", "testing"],
  },
];

// =============================================================================
// ENSEMBLE ORCHESTRATOR
// =============================================================================

export class EnsembleOrchestrator {
  private openaiAdapter?: OpenAIAdapter;
  private anthropicAdapter?: AnthropicAdapter;
  private geminiAdapter?: GeminiAdapter;
  private config: Required<Pick<EnsembleConfig, "agreementThreshold" | "severityTolerrance">>;

  constructor(config: EnsembleConfig) {
    if (config.openaiApiKey) {
      this.openaiAdapter = new OpenAIAdapter(
        config.openaiApiKey,
        config.openaiModel || "gpt-4o"
      );
    }
    if (config.anthropicApiKey) {
      this.anthropicAdapter = new AnthropicAdapter(
        config.anthropicApiKey,
        config.anthropicModel || "claude-sonnet-4-20250514"
      );
    }
    if (config.geminiApiKey) {
      this.geminiAdapter = new GeminiAdapter(
        config.geminiApiKey,
        config.geminiModel || "gemini-2.0-flash"
      );
    }

    this.config = {
      agreementThreshold: config.agreementThreshold ?? 0.67,
      severityTolerrance: config.severityTolerrance ?? 2,
    };
  }

  /**
   * Run all available models in parallel
   */
  async runEnsembleAnalysis(
    projectId: string,
    changeControlId: string,
    sourceDocuments: SourceSnippet[],
    existingRiskItems: RiskItemDraft[] = []
  ): Promise<EnsembleResult> {
    const startTime = Date.now();

    const context: AgentContext = {
      projectId,
      changeControlId,
      sourceDocuments,
      existingRiskItems,
      previousFindings: [],
      iterationCount: 1,
      maxIterations: 1,
    };

    // Run all models in parallel
    const modelPromises: Promise<ModelResult>[] = [];

    if (this.openaiAdapter) {
      modelPromises.push(this.runModel("openai", "gpt-4o", context));
    }
    if (this.anthropicAdapter) {
      modelPromises.push(this.runModel("anthropic", "claude-sonnet-4-20250514", context));
    }
    if (this.geminiAdapter) {
      modelPromises.push(this.runModel("gemini", "gemini-2.0-flash", context));
    }

    const modelResults = await Promise.all(modelPromises);
    const successfulResults = modelResults.filter(r => !r.error);

    // Calculate agreement
    const riskAgreements = this.calculateRiskAgreement(successfulResults);

    // Run canary tests
    const canaryResults = this.runCanaryTests(successfulResults);

    // Combine results with confidence weighting
    const combinedRiskItems = this.combineRiskItems(riskAgreements, successfulResults);
    const combinedGaps = this.combineGaps(successfulResults);

    // Calculate overall metrics
    const overallAgreementScore = this.calculateOverallAgreement(riskAgreements);
    const highConfidenceItems = riskAgreements
      .filter(r => r.agreementScore >= this.config.agreementThreshold && !r.needsHumanReview)
      .map(r => r.riskId);
    const needsReviewItems = riskAgreements
      .filter(r => r.needsHumanReview)
      .map(r => r.riskId);

    // Sum token usage
    const totalTokenUsage = this.sumTokenUsage(modelResults.map(r => r.tokenUsage));

    return {
      modelResults,
      riskAgreements,
      combinedRiskItems,
      combinedGaps,
      overallAgreementScore,
      highConfidenceItems,
      needsReviewItems,
      totalTokenUsage,
      totalProcessingTimeMs: Date.now() - startTime,
      canaryResults,
    };
  }

  /**
   * Run a single model and capture results
   */
  private async runModel(
    provider: ModelProvider,
    model: string,
    context: AgentContext
  ): Promise<ModelResult> {
    const startTime = Date.now();

    try {
      let output: AuthorOutput;

      switch (provider) {
        case "openai":
          output = await this.openaiAdapter!.generateAuthorDraft(context);
          break;
        case "anthropic":
          output = await this.anthropicAdapter!.generateCriticAsAuthor(context);
          break;
        case "gemini":
          output = await this.geminiAdapter!.generateAuthorDraft(context);
          break;
      }

      return {
        provider,
        model,
        riskItems: output.riskItems,
        gaps: output.identifiedGaps,
        tokenUsage: output.tokenUsage,
        processingTimeMs: Date.now() - startTime,
      };
    } catch (error) {
      console.error(`Error running ${provider}:`, error);
      return {
        provider,
        model,
        riskItems: [],
        gaps: [],
        tokenUsage: { inputTokens: 0, outputTokens: 0, totalTokens: 0, estimatedCostUsd: 0 },
        processingTimeMs: Date.now() - startTime,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  /**
   * Calculate agreement between models on each risk
   */
  private calculateRiskAgreement(results: ModelResult[]): RiskAgreement[] {
    // Collect all unique risks by matching failure modes
    const riskMap = new Map<string, {
      failureMode: string;
      foundBy: Map<ModelProvider, RiskItemDraft>;
    }>();

    for (const result of results) {
      for (const risk of result.riskItems) {
        // Normalize failure mode for comparison
        const normalizedMode = this.normalizeText(risk.failureMode);

        // Find existing similar risk or create new entry
        let matched = false;
        for (const [key, existing] of riskMap.entries()) {
          if (this.textSimilarity(normalizedMode, this.normalizeText(existing.failureMode)) > 0.6) {
            existing.foundBy.set(result.provider, risk);
            matched = true;
            break;
          }
        }

        if (!matched) {
          const key = `risk-${riskMap.size + 1}`;
          riskMap.set(key, {
            failureMode: risk.failureMode,
            foundBy: new Map([[result.provider, risk]]),
          });
        }
      }
    }

    // Convert to RiskAgreement array
    const totalModels = results.length;
    const agreements: RiskAgreement[] = [];

    for (const [riskId, data] of riskMap.entries()) {
      const foundByProviders = Array.from(data.foundBy.keys());
      const agreementScore = foundByProviders.length / totalModels;

      // Calculate severity agreement
      const severityScores = Array.from(data.foundBy.entries()).map(([provider, risk]) => ({
        provider,
        severity: risk.severity,
      }));
      const severityAgreement = this.calculateSeverityAgreement(severityScores);

      // Determine if human review is needed
      const needsHumanReview = agreementScore < this.config.agreementThreshold ||
                               severityAgreement < 0.5;
      let reviewReason: string | undefined;

      if (agreementScore < this.config.agreementThreshold) {
        const missing = results
          .filter(r => !foundByProviders.includes(r.provider))
          .map(r => r.provider);
        reviewReason = `Only ${foundByProviders.length}/${totalModels} models found this risk. Missing: ${missing.join(", ")}`;
      } else if (severityAgreement < 0.5) {
        const scores = severityScores.map(s => `${s.provider}: ${s.severity}`).join(", ");
        reviewReason = `Severity disagreement: ${scores}`;
      }

      agreements.push({
        riskId: data.foundBy.values().next().value?.riskId || riskId,
        failureMode: data.failureMode,
        foundBy: foundByProviders,
        agreementScore,
        severityScores,
        severityAgreement,
        needsHumanReview,
        reviewReason,
      });
    }

    return agreements.sort((a, b) => b.agreementScore - a.agreementScore);
  }

  /**
   * Run canary tests to verify model reliability
   */
  private runCanaryTests(results: ModelResult[]): CanaryTestResult[] {
    return CANARY_RISKS.map(canary => {
      const foundBy: ModelProvider[] = [];

      for (const result of results) {
        const found = result.riskItems.some(risk => {
          const riskText = `${risk.failureMode} ${risk.potentialCause} ${risk.potentialEffect}`.toLowerCase();
          return canary.keywords.some(keyword => riskText.includes(keyword.toLowerCase()));
        });

        if (found) {
          foundBy.push(result.provider);
        }
      }

      return {
        canaryId: canary.id,
        expectedRisk: canary.expectedRisk,
        foundBy,
        passed: foundBy.length > 0,
      };
    });
  }

  /**
   * Combine risk items with confidence based on agreement
   */
  private combineRiskItems(
    agreements: RiskAgreement[],
    results: ModelResult[]
  ): RiskItemDraft[] {
    const combined: RiskItemDraft[] = [];

    for (const agreement of agreements) {
      // Get the first available risk item for this agreement
      for (const result of results) {
        const matchingRisk = result.riskItems.find(risk =>
          this.textSimilarity(
            this.normalizeText(risk.failureMode),
            this.normalizeText(agreement.failureMode)
          ) > 0.6
        );

        if (matchingRisk) {
          // Calculate average severity from all models
          const avgSeverity = Math.round(
            agreement.severityScores.reduce((sum, s) => sum + s.severity, 0) /
            agreement.severityScores.length
          );

          combined.push({
            ...matchingRisk,
            riskId: agreement.riskId,
            severity: avgSeverity,
            initialRpn: avgSeverity * matchingRisk.occurrence * matchingRisk.detectability,
            confidenceLevel: agreement.agreementScore >= this.config.agreementThreshold ? "HIGH" : "LOW",
            authorNotes: `Agreement: ${Math.round(agreement.agreementScore * 100)}% (${agreement.foundBy.join(", ")})`,
          });
          break;
        }
      }
    }

    return combined;
  }

  /**
   * Combine gaps from all models
   */
  private combineGaps(results: ModelResult[]): GapItem[] {
    const gapMap = new Map<string, GapItem>();

    for (const result of results) {
      for (const gap of result.gaps) {
        const key = this.normalizeText(gap.description);
        if (!gapMap.has(key)) {
          gapMap.set(key, gap);
        }
      }
    }

    return Array.from(gapMap.values());
  }

  // ===========================================================================
  // HELPER METHODS
  // ===========================================================================

  private normalizeText(text: string): string {
    return text.toLowerCase().trim().replace(/\s+/g, " ");
  }

  private textSimilarity(a: string, b: string): number {
    // Simple Jaccard similarity on words
    const wordsA = new Set(a.split(" "));
    const wordsB = new Set(b.split(" "));
    const intersection = new Set([...wordsA].filter(x => wordsB.has(x)));
    const union = new Set([...wordsA, ...wordsB]);
    return intersection.size / union.size;
  }

  private calculateSeverityAgreement(scores: { provider: ModelProvider; severity: number }[]): number {
    if (scores.length <= 1) return 1;

    const severities = scores.map(s => s.severity);
    const max = Math.max(...severities);
    const min = Math.min(...severities);
    const range = max - min;

    // Full agreement if range is within tolerance
    if (range <= this.config.severityTolerrance) return 1;

    // Linear decrease in agreement as range increases
    return Math.max(0, 1 - (range - this.config.severityTolerrance) / 10);
  }

  private calculateOverallAgreement(agreements: RiskAgreement[]): number {
    if (agreements.length === 0) return 0;
    return agreements.reduce((sum, a) => sum + a.agreementScore, 0) / agreements.length;
  }

  private sumTokenUsage(usages: TokenUsage[]): TokenUsage {
    return usages.reduce(
      (sum, u) => ({
        inputTokens: sum.inputTokens + u.inputTokens,
        outputTokens: sum.outputTokens + u.outputTokens,
        totalTokens: sum.totalTokens + u.totalTokens,
        estimatedCostUsd: sum.estimatedCostUsd + u.estimatedCostUsd,
      }),
      { inputTokens: 0, outputTokens: 0, totalTokens: 0, estimatedCostUsd: 0 }
    );
  }
}

/**
 * Factory function to create ensemble orchestrator
 */
export function createEnsembleOrchestrator(): EnsembleOrchestrator {
  return new EnsembleOrchestrator({
    openaiApiKey: process.env.OPENAI_API_KEY,
    anthropicApiKey: process.env.ANTHROPIC_API_KEY,
    geminiApiKey: process.env.GEMINI_API_KEY,
    openaiModel: process.env.OPENAI_MODEL || "gpt-4o",
    anthropicModel: process.env.ANTHROPIC_MODEL || "claude-sonnet-4-20250514",
    geminiModel: process.env.GEMINI_MODEL || "gemini-2.0-flash",
  });
}
