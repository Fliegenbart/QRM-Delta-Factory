/**
 * Multi-Agent QRM System Types
 *
 * Architecture: Author (GPT) -> Critic (Claude) -> Resolver (GPT)
 */

// =============================================================================
// CORE TYPES
// =============================================================================

export type AgentRole = "AUTHOR" | "CRITIC" | "RESOLVER";
export type CriticSeverity = "BLOCKER" | "CONCERN" | "SUGGESTION";
export type ClaimConfidence = "VERIFIED" | "INFERRED" | "UNVERIFIED" | "CONTRADICTED";
export type AgentDecision = "ACCEPT" | "REVISE" | "ESCALATE_TO_HUMAN";

// =============================================================================
// DOCUMENT VERIFICATION
// =============================================================================

export interface SourceSnippet {
  id: string;
  documentId: string;
  documentType: string;
  sectionTitle: string;
  content: string;
  lineReference: string;
  snippetHash: string;
}

export interface VerifiedClaim {
  claim: string;
  sourceSnippetId: string | null;
  sourceText: string | null;
  confidence: ClaimConfidence;
  verificationNote: string;
}

export interface DocumentSearchResult {
  snippetId: string;
  documentType: string;
  sectionTitle: string;
  content: string;
  relevanceScore: number;
}

// =============================================================================
// RISK ITEM DRAFT
// =============================================================================

export interface RiskItemDraft {
  riskId: string;
  processStep: string;
  failureMode: string;
  potentialCause: string;
  potentialEffect: string;
  severity: number;
  occurrence: number;
  detectability: number;
  initialRpn: number;
  existingControls: string[];
  proposedControls: string[];
  requiredEvidence: string[];
  impactCategories: string[];
  claims: VerifiedClaim[];
  authorNotes: string;
  confidenceLevel: "HIGH" | "MEDIUM" | "LOW";
}

// =============================================================================
// AGENT OUTPUTS
// =============================================================================

export interface AuthorOutput {
  riskItems: RiskItemDraft[];
  identifiedGaps: GapItem[];
  questionsForSme: string[];
  processingNotes: string;
  tokenUsage: TokenUsage;
}

export interface CriticFinding {
  riskItemId: string;
  severity: CriticSeverity;
  category: "EVIDENCE_GAP" | "LOGIC_FLAW" | "MISSING_RISK" | "SCORE_DISPUTE" | "UNVERIFIED_CLAIM" | "REGULATORY_CONCERN";
  description: string;
  suggestedAction: string;
  affectedClaims: string[];
  verificationAttempt: VerifiedClaim | null;
}

export interface CriticOutput {
  findings: CriticFinding[];
  overallAssessment: "ACCEPTABLE" | "NEEDS_REVISION" | "MAJOR_ISSUES";
  commendations: string[];  // What the Author did well (Best Buddies!)
  processingNotes: string;
  tokenUsage: TokenUsage;
}

export interface ResolverDecision {
  riskItemId: string;
  decision: AgentDecision;
  originalClaim: string | null;
  criticFinding: string | null;
  resolution: string;
  revisedContent: Partial<RiskItemDraft> | null;
  escalationReason: string | null;
}

export interface ResolverOutput {
  decisions: ResolverDecision[];
  revisedRiskItems: RiskItemDraft[];
  escalatedItems: string[];  // Risk IDs that need human review
  responseToColleague: string;  // Friendly response to Critic
  requiresAnotherLoop: boolean;
  tokenUsage: TokenUsage;
}

// =============================================================================
// GAP TRACKING
// =============================================================================

export interface GapItem {
  id: string;
  riskItemId: string | null;
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  category: "EVIDENCE" | "DOCUMENTATION" | "TRAINING" | "VALIDATION" | "PROCESS";
  description: string;
  suggestedResolution: string;
  identifiedBy: AgentRole;
}

// =============================================================================
// ORCHESTRATION
// =============================================================================

export interface AgentContext {
  projectId: string;
  changeControlId: string;
  sourceDocuments: SourceSnippet[];
  existingRiskItems: RiskItemDraft[];
  previousFindings: CriticFinding[];
  iterationCount: number;
  maxIterations: number;
}

export interface OrchestrationResult {
  finalRiskItems: RiskItemDraft[];
  allFindings: CriticFinding[];
  gaps: GapItem[];
  escalatedItems: string[];
  iterationsUsed: number;
  agentConversation: AgentMessage[];
  totalTokenUsage: TokenUsage;
  processingTimeMs: number;
}

export interface AgentMessage {
  role: AgentRole;
  timestamp: string;
  content: string;
  tokenUsage: TokenUsage;
}

// =============================================================================
// TOKEN TRACKING
// =============================================================================

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  estimatedCostUsd: number;
}

// =============================================================================
// LLM ADAPTER INTERFACE
// =============================================================================

export interface LLMAdapter {
  readonly provider: "openai" | "anthropic";
  readonly model: string;

  generateAuthorDraft(context: AgentContext): Promise<AuthorOutput>;
  generateCriticReview(context: AgentContext, authorOutput: AuthorOutput): Promise<CriticOutput>;
  generateResolverDecision(context: AgentContext, authorOutput: AuthorOutput, criticOutput: CriticOutput): Promise<ResolverOutput>;
}

// =============================================================================
// CONFIGURATION
// =============================================================================

export interface AgentConfig {
  openaiApiKey: string;
  anthropicApiKey: string;
  openaiModel: string;
  anthropicModel: string;
  maxRevisionLoops: number;
  enableDocumentVerification: boolean;
  escalateOnDisagreement: boolean;
  escalateHighSeverityAlways: boolean;
}

export const DEFAULT_AGENT_CONFIG: Partial<AgentConfig> = {
  openaiModel: "gpt-4o",
  anthropicModel: "claude-sonnet-4-20250514",
  maxRevisionLoops: 2,
  enableDocumentVerification: true,
  escalateOnDisagreement: true,
  escalateHighSeverityAlways: true,
};
