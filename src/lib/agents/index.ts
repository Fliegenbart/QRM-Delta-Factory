/**
 * Multi-Agent QRM System
 *
 * Exports for the Agent Orchestration System
 */

// Core orchestrator
export { AgentOrchestrator, createOrchestrator } from "./orchestrator";

// Individual adapters (for advanced use)
export { OpenAIAdapter } from "./openai-adapter";
export { AnthropicAdapter } from "./anthropic-adapter";
export { GeminiAdapter } from "./gemini-adapter";

// Ensemble orchestrator
export {
  EnsembleOrchestrator,
  createEnsembleOrchestrator,
  CANARY_RISKS,
  type ModelProvider,
  type ModelResult,
  type RiskAgreement,
  type EnsembleResult,
  type CanaryTestResult,
  type EnsembleConfig,
} from "./ensemble-orchestrator";

// Document verification
export { DocumentVerifier, getDocumentVerifier } from "./document-verifier";

// Types
export type {
  // Core types
  AgentRole,
  CriticSeverity,
  ClaimConfidence,
  AgentDecision,

  // Document types
  SourceSnippet,
  VerifiedClaim,
  DocumentSearchResult,

  // Risk types
  RiskItemDraft,
  GapItem,

  // Agent outputs
  AuthorOutput,
  CriticFinding,
  CriticOutput,
  ResolverDecision,
  ResolverOutput,

  // Orchestration
  AgentContext,
  OrchestrationResult,
  AgentMessage,
  TokenUsage,

  // Configuration
  AgentConfig,
  LLMAdapter,
} from "./types";

// Prompts (for customization)
export {
  AUTHOR_SYSTEM_PROMPT,
  CRITIC_SYSTEM_PROMPT,
  RESOLVER_SYSTEM_PROMPT,
  DOCUMENT_VERIFICATION_PROMPT,
  buildAuthorPrompt,
  buildCriticPrompt,
  buildResolverPrompt,
} from "./prompts";
