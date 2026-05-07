const draftNotice =
  "DRAFT TEMPLATE ONLY. This artifact supports validation planning and review. It does not establish that the system is validated or acceptable for production GxP use.";

export const validationArtifacts = [
  "User Requirements Specification",
  "Functional Specification",
  "GxP Impact Assessment",
  "System Risk Assessment",
  "Data Integrity Assessment",
  "Annex 11 control checklist",
  "Part 11 control checklist",
  "Test Plan",
  "Test Cases",
  "Requirements Traceability Matrix",
  "Validation Summary Report template",
  "SOP for AI-assisted QRM workflow",
  "SOP for human review and approval",
  "SOP for risk-library management",
  "SOP for periodic review",
  "SOP for audit trail review",
  "SOP for model/configuration change control"
];

export function generateValidationPack(projectName: string) {
  return validationArtifacts.map((title) => ({
    title,
    status: "DRAFT_TEMPLATE",
    content: [
      `# ${title}`,
      "",
      draftNotice,
      "",
      `System: Pharma QRM Delta Engine`,
      `Project context: ${projectName}`,
      "",
      "## Purpose",
      "Define reviewable, source-based expectations for AI-assisted QRM drafting in a GMP environment.",
      "",
      "## Draft content",
      "- Scope and responsibilities must be completed by the regulated company.",
      "- Human review, QA decision workflow, audit trail review, backup/restore, access control, and periodic review must be defined before production use.",
      "- Supplier assessment, security review, privacy review, model governance, and formal validation evidence are required for production deployment.",
      "",
      "## Acceptance notes",
      "Acceptance criteria must be reviewed and executed by qualified personnel under the company's quality system."
    ].join("\n")
  }));
}
