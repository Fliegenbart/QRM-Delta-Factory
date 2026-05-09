/**
 * Agent Orchestrator
 *
 * Coordinates the multi-agent workflow:
 * 1. Author (GPT-4o) creates initial risk drafts
 * 2. Critic (Claude) reviews and finds issues
 * 3. Resolver (GPT-4o) mediates and revises or escalates
 *
 * "Best Buddies, Gnadenlose Kritiker"
 */

import { OpenAIAdapter } from "./openai-adapter";
import { AnthropicAdapter } from "./anthropic-adapter";
import { DocumentVerifier, getDocumentVerifier } from "./document-verifier";
import type {
  AgentContext,
  AgentConfig,
  AgentMessage,
  OrchestrationResult,
  TokenUsage,
  RiskItemDraft,
  CriticFinding,
  GapItem,
  SourceSnippet,
  DEFAULT_AGENT_CONFIG,
} from "./types";

export class AgentOrchestrator {
  private openai: OpenAIAdapter;
  private anthropic: AnthropicAdapter;
  private verifier: DocumentVerifier;
  private config: AgentConfig;

  constructor(config: Partial<AgentConfig> & { openaiApiKey: string; anthropicApiKey: string }) {
    this.config = {
      openaiApiKey: config.openaiApiKey,
      anthropicApiKey: config.anthropicApiKey,
      openaiModel: config.openaiModel || "gpt-4o",
      anthropicModel: config.anthropicModel || "claude-sonnet-4-20250514",
      maxRevisionLoops: config.maxRevisionLoops || 2,
      enableDocumentVerification: config.enableDocumentVerification ?? true,
      escalateOnDisagreement: config.escalateOnDisagreement ?? true,
      escalateHighSeverityAlways: config.escalateHighSeverityAlways ?? true,
    };

    this.openai = new OpenAIAdapter(this.config.openaiApiKey, this.config.openaiModel);
    this.anthropic = new AnthropicAdapter(this.config.anthropicApiKey, this.config.anthropicModel);
    this.verifier = getDocumentVerifier();
  }

  /**
   * Run the full multi-agent analysis workflow
   */
  async runAnalysis(
    projectId: string,
    changeControlId: string,
    sourceDocuments: SourceSnippet[],
    existingRiskItems: RiskItemDraft[] = []
  ): Promise<OrchestrationResult> {
    const startTime = Date.now();
    const conversation: AgentMessage[] = [];
    const allFindings: CriticFinding[] = [];
    const allGaps: GapItem[] = [];
    let totalTokenUsage: TokenUsage = {
      inputTokens: 0,
      outputTokens: 0,
      totalTokens: 0,
      estimatedCostUsd: 0,
    };

    // Initialize context
    const context: AgentContext = {
      projectId,
      changeControlId,
      sourceDocuments,
      existingRiskItems,
      previousFindings: [],
      iterationCount: 0,
      maxIterations: this.config.maxRevisionLoops,
    };

    // Update verifier with source documents
    this.verifier = new DocumentVerifier(sourceDocuments);

    let currentRiskItems = existingRiskItems;
    let escalatedItems: string[] = [];
    let iterationsUsed = 0;

    // =========================================================================
    // PHASE 1: AUTHOR CREATES INITIAL DRAFT
    // =========================================================================
    console.log("🖊️ Phase 1: Author (GPT-4o) creating initial draft...");

    const authorOutput = await this.openai.generateAuthorDraft(context);
    this.addTokenUsage(totalTokenUsage, authorOutput.tokenUsage);

    conversation.push({
      role: "AUTHOR",
      timestamp: new Date().toISOString(),
      content: `Created ${authorOutput.riskItems.length} risk items, identified ${authorOutput.identifiedGaps.length} gaps, raised ${authorOutput.questionsForSme.length} SME questions.`,
      tokenUsage: authorOutput.tokenUsage,
    });

    currentRiskItems = authorOutput.riskItems;
    allGaps.push(...authorOutput.identifiedGaps);

    // =========================================================================
    // REVISION LOOP: CRITIC -> RESOLVER -> (repeat if needed)
    // =========================================================================
    let requiresAnotherLoop = true;

    while (requiresAnotherLoop && iterationsUsed < this.config.maxRevisionLoops) {
      iterationsUsed++;
      context.iterationCount = iterationsUsed;
      context.previousFindings = allFindings;

      // -----------------------------------------------------------------------
      // PHASE 2: CRITIC REVIEWS
      // -----------------------------------------------------------------------
      console.log(`🔍 Phase 2 (Iteration ${iterationsUsed}): Critic (Claude) reviewing...`);

      const criticOutput = await this.anthropic.generateCriticReview(
        { ...context, existingRiskItems: currentRiskItems },
        { ...authorOutput, riskItems: currentRiskItems }
      );
      this.addTokenUsage(totalTokenUsage, criticOutput.tokenUsage);

      conversation.push({
        role: "CRITIC",
        timestamp: new Date().toISOString(),
        content: `Found ${criticOutput.findings.length} issues (${criticOutput.findings.filter(f => f.severity === "BLOCKER").length} blockers). Overall: ${criticOutput.overallAssessment}. Commendations: ${criticOutput.commendations.join(", ") || "None"}`,
        tokenUsage: criticOutput.tokenUsage,
      });

      allFindings.push(...criticOutput.findings);

      // If acceptable with no blockers, we're done
      if (criticOutput.overallAssessment === "ACCEPTABLE") {
        console.log("✅ Critic approved! No further iterations needed.");
        requiresAnotherLoop = false;
        break;
      }

      // -----------------------------------------------------------------------
      // PHASE 3: RESOLVER MEDIATES
      // -----------------------------------------------------------------------
      console.log(`⚖️ Phase 3 (Iteration ${iterationsUsed}): Resolver (GPT-4o) mediating...`);

      const resolverOutput = await this.openai.generateResolverDecision(
        { ...context, existingRiskItems: currentRiskItems },
        { ...authorOutput, riskItems: currentRiskItems },
        criticOutput
      );
      this.addTokenUsage(totalTokenUsage, resolverOutput.tokenUsage);

      conversation.push({
        role: "RESOLVER",
        timestamp: new Date().toISOString(),
        content: `Made ${resolverOutput.decisions.length} decisions. Escalated: ${resolverOutput.escalatedItems.length}. Response: "${resolverOutput.responseToColleague}"`,
        tokenUsage: resolverOutput.tokenUsage,
      });

      // Update risk items with revisions
      if (resolverOutput.revisedRiskItems.length > 0) {
        currentRiskItems = this.mergeRiskItems(currentRiskItems, resolverOutput.revisedRiskItems);
      }

      // Track escalations
      escalatedItems = [...new Set([...escalatedItems, ...resolverOutput.escalatedItems])];

      // Check if another loop is needed
      requiresAnotherLoop = resolverOutput.requiresAnotherLoop;

      if (requiresAnotherLoop) {
        console.log(`🔄 Another revision loop needed (${iterationsUsed}/${this.config.maxRevisionLoops})`);
      }
    }

    // =========================================================================
    // HIGH SEVERITY ESCALATION CHECK
    // =========================================================================
    if (this.config.escalateHighSeverityAlways) {
      const highSeverityItems = currentRiskItems
        .filter(r => r.severity >= 7)
        .map(r => r.riskId);
      escalatedItems = [...new Set([...escalatedItems, ...highSeverityItems])];
    }

    // =========================================================================
    // FINALIZE RESULTS
    // =========================================================================
    const processingTimeMs = Date.now() - startTime;

    console.log(`\n📊 Analysis complete in ${processingTimeMs}ms`);
    console.log(`   - ${currentRiskItems.length} risk items`);
    console.log(`   - ${allFindings.length} total findings`);
    console.log(`   - ${escalatedItems.length} items escalated to human review`);
    console.log(`   - ${iterationsUsed} iterations used`);
    console.log(`   - $${totalTokenUsage.estimatedCostUsd.toFixed(4)} estimated cost`);

    return {
      finalRiskItems: currentRiskItems,
      allFindings,
      gaps: allGaps,
      escalatedItems,
      iterationsUsed,
      agentConversation: conversation,
      totalTokenUsage,
      processingTimeMs,
    };
  }

  /**
   * Run document verification for a specific claim
   */
  async verifyClaimWithAI(claim: string, snippetId: string): Promise<{
    localVerification: ReturnType<DocumentVerifier["verifyClaim"]>;
    aiVerification: Awaited<ReturnType<AnthropicAdapter["verifyClaim"]>> | null;
  }> {
    const localResult = this.verifier.verifyClaim(claim, snippetId);
    const snippet = this.verifier.getSnippet(snippetId);

    let aiResult = null;
    if (snippet && (localResult.confidence === "UNVERIFIED" || localResult.confidence === "INFERRED")) {
      // Use Claude to double-check uncertain verifications
      aiResult = await this.anthropic.verifyClaim(claim, {
        id: snippet.id,
        content: snippet.content,
      });
    }

    return {
      localVerification: localResult,
      aiVerification: aiResult,
    };
  }

  // ===========================================================================
  // PRIVATE HELPERS
  // ===========================================================================

  private addTokenUsage(total: TokenUsage, addition: TokenUsage): void {
    total.inputTokens += addition.inputTokens;
    total.outputTokens += addition.outputTokens;
    total.totalTokens += addition.totalTokens;
    total.estimatedCostUsd += addition.estimatedCostUsd;
  }

  private mergeRiskItems(existing: RiskItemDraft[], revised: RiskItemDraft[]): RiskItemDraft[] {
    const merged = [...existing];

    for (const revisedItem of revised) {
      const existingIndex = merged.findIndex(e => e.riskId === revisedItem.riskId);
      if (existingIndex >= 0) {
        merged[existingIndex] = revisedItem;
      } else {
        merged.push(revisedItem);
      }
    }

    return merged;
  }
}

// ===========================================================================
// FACTORY FUNCTION
// ===========================================================================

export function createOrchestrator(config?: {
  openaiApiKey?: string;
  anthropicApiKey?: string;
  openaiModel?: string;
  anthropicModel?: string;
  maxRevisionLoops?: number;
}): AgentOrchestrator {
  const openaiApiKey = config?.openaiApiKey || process.env.OPENAI_API_KEY;
  const anthropicApiKey = config?.anthropicApiKey || process.env.ANTHROPIC_API_KEY;

  if (!openaiApiKey || !anthropicApiKey) {
    throw new Error("Missing API keys. Set OPENAI_API_KEY and ANTHROPIC_API_KEY environment variables.");
  }

  return new AgentOrchestrator({
    openaiApiKey,
    anthropicApiKey,
    openaiModel: config?.openaiModel || process.env.OPENAI_MODEL || "gpt-4o",
    anthropicModel: config?.anthropicModel || process.env.ANTHROPIC_MODEL || "claude-sonnet-4-20250514",
    maxRevisionLoops: config?.maxRevisionLoops || parseInt(process.env.MAX_REVISION_LOOPS || "2"),
  });
}
