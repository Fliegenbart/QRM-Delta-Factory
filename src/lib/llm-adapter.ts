import { demoGaps, demoPlausibilityChecks, demoProject, demoRedTeamFindings, demoRiskItems } from "./demo-data";

export interface AuthorDeltaResult {
  triggerSummary: string;
  affectedProcessSteps: string[];
  impactedRiskItemIds: string[];
  proposedRiskItems: typeof demoRiskItems;
  gaps: typeof demoGaps;
}

export interface CriticResult {
  checks: typeof demoPlausibilityChecks;
}

export interface RedTeamResult {
  findings: typeof demoRedTeamFindings;
}

export interface LLMAdapter {
  generateAuthorDelta(projectId: string): Promise<AuthorDeltaResult>;
  runCriticCheck(projectId: string): Promise<CriticResult>;
  runRedTeam(projectId: string): Promise<RedTeamResult>;
}

export class MockLLMAdapter implements LLMAdapter {
  async generateAuthorDelta(projectId: string) {
    return {
      triggerSummary:
        "DRAFT: Change control proposes a modified automated visual inspection rejection threshold. The package indicates new-threshold evidence is planned but not yet present.",
      affectedProcessSteps: ["Automated visual inspection", "AVI result handling", "Batch record reconciliation", "Training rollout"],
      impactedRiskItemIds: demoRiskItems.map((item) => item.id),
      proposedRiskItems: demoRiskItems.filter((item) => item.projectId === projectId || projectId === demoProject.id),
      gaps: demoGaps
    };
  }

  async runCriticCheck(_projectId: string) {
    return { checks: demoPlausibilityChecks };
  }

  async runRedTeam(_projectId: string) {
    return { findings: demoRedTeamFindings };
  }
}

export const llmAdapter = new MockLLMAdapter();
