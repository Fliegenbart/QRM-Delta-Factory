import { PrismaClient } from "@prisma/client";
import bcrypt from "bcryptjs";
import {
  demoAuditLogs,
  demoDocuments,
  demoGaps,
  demoPlausibilityChecks,
  demoProject,
  demoRedTeamFindings,
  demoRiskItems,
  demoRiskLibrary,
  demoSnippets,
  demoUsers
} from "../src/lib/demo-data";
import { generateValidationPack } from "../src/lib/validation-pack";
import { sha256 } from "../src/lib/qrm-engine";

const prisma = new PrismaClient();

async function main() {
  await prisma.auditLog.deleteMany();
  await prisma.validationArtifact.deleteMany();
  await prisma.exportPackage.deleteMany();
  await prisma.approval.deleteMany();
  await prisma.reviewComment.deleteMany();
  await prisma.redTeamFinding.deleteMany();
  await prisma.plausibilityCheck.deleteMany();
  await prisma.gap.deleteMany();
  await prisma.evidenceLink.deleteMany();
  await prisma.controlMeasure.deleteMany();
  await prisma.riskSourceLink.deleteMany();
  await prisma.riskItemVersion.deleteMany();
  await prisma.riskItem.deleteMany();
  await prisma.auditFinding.deleteMany();
  await prisma.cAPARecord.deleteMany();
  await prisma.deviationRecord.deleteMany();
  await prisma.changeRecord.deleteMany();
  await prisma.riskLibraryItem.deleteMany();
  await prisma.existingRiskFile.deleteMany();
  await prisma.sourceSnippet.deleteMany();
  await prisma.sourceDocument.deleteMany();
  await prisma.project.deleteMany();
  await prisma.user.deleteMany();

  const passwordHash = await bcrypt.hash("demo123", 10);
  for (const user of demoUsers) {
    await prisma.user.create({
      data: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        passwordHash
      }
    });
  }

  await prisma.project.create({
    data: {
      id: demoProject.id,
      name: demoProject.name,
      productProcessSystem: demoProject.productProcessSystem,
      gmpArea: demoProject.gmpArea,
      scopeStatement: demoProject.scopeStatement,
      outOfScopeStatement: demoProject.outOfScopeStatement,
      triggerType: demoProject.triggerType,
      methodology: demoProject.methodology,
      scoringModel: demoProject.scoringModel,
      requiredSmeReviewers: demoProject.requiredSmeReviewers.join(", "),
      requiredQaApprover: demoProject.requiredQaApprover,
      authorId: "user-author"
    }
  });

  for (const document of demoDocuments) {
    await prisma.sourceDocument.create({
      data: {
        id: document.id,
        projectId: demoProject.id,
        documentType: document.documentType,
        fileName: document.fileName,
        mimeType: document.fileName.endsWith(".csv") ? "text/csv" : "text/markdown",
        content: document.content,
        metadataJson: JSON.stringify({
          synthetic: true,
          supportedMvpFormats: [".txt", ".md", ".csv", "manual rows"],
          todos: ["PDF ingestion", "DOCX ingestion", "XLSX ingestion", "OCR", "SharePoint/Teams", "Veeva/TrackWise/Documentum"]
        })
      }
    });
  }

  for (const snippet of demoSnippets) {
    await prisma.sourceSnippet.create({
      data: {
        id: snippet.id,
        documentId: snippet.documentId,
        documentType: snippet.documentType,
        sectionTitle: snippet.sectionTitle,
        lineReference: snippet.lineReference,
        text: snippet.text,
        snippetHash: snippet.snippetHash
      }
    });
  }

  for (const item of demoRiskLibrary) {
    await prisma.riskLibraryItem.create({
      data: {
        id: item.id,
        libraryId: item.libraryId,
        gmpArea: item.gmpArea,
        processStep: item.processStep,
        failureMode: item.failureMode,
        typicalCauses: item.typicalCauses,
        patientSafetyEffect: item.patientSafetyEffect,
        productQualityEffect: item.productQualityEffect,
        dataIntegrityEffect: item.dataIntegrityEffect,
        gmpComplianceEffect: item.gmpComplianceEffect,
        commonExistingControls: item.commonExistingControls,
        typicalAdditionalControls: item.typicalAdditionalControls,
        typicalEvidence: item.typicalEvidence,
        defaultScoringGuidance: item.defaultScoringGuidance,
        requiredSmeDiscipline: item.requiredSmeDiscipline,
        approvalStatus: item.approvalStatus,
        approvedBy: item.approvedBy ?? undefined,
        approvedDate: item.approvedDate ? new Date(item.approvedDate) : undefined,
        version: item.version,
        retired: item.retired
      }
    });
  }

  await prisma.changeRecord.create({
    data: {
      projectId: demoProject.id,
      title: "CC-042 modified AVI rejection threshold",
      triggerText: "Modified automated visual inspection rejection threshold to reduce false rejects."
    }
  });
  await prisma.deviationRecord.create({
    data: {
      projectId: demoProject.id,
      title: "DEV-118 unclear AVI reconciliation wording",
      summary: "Reject-count reconciliation wording is unclear in batch-record excerpt."
    }
  });
  await prisma.cAPARecord.create({
    data: {
      projectId: demoProject.id,
      title: "CAPA placeholder for threshold verification follow-up",
      summary: "Synthetic CAPA record for enhanced evidence collection and training completion."
    }
  });
  await prisma.auditFinding.create({
    data: {
      projectId: demoProject.id,
      title: "Audit finding placeholder: audit trail review scope",
      summary: "Synthetic finding asks whether threshold configuration is explicitly covered in review."
    }
  });

  for (const risk of demoRiskItems) {
    await prisma.riskItem.create({
      data: {
        id: risk.id,
        projectId: risk.projectId,
        riskLibraryItemId: risk.libraryItemId,
        riskCode: risk.id.toUpperCase(),
        processStep: risk.processStep,
        gmpArea: risk.gmpArea,
        failureMode: risk.failureMode,
        potentialCause: risk.potentialCause,
        potentialEffect: risk.potentialEffect,
        impactCategories: risk.impactCategories.join(", "),
        existingControls: risk.existingControls.join("; "),
        severitySuggestion: risk.severity,
        occurrenceSuggestion: risk.occurrence,
        detectabilitySuggestion: risk.detectability,
        initialRpn: risk.severity * risk.occurrence * risk.detectability,
        initialRiskClass: risk.priority,
        humanSeverity: risk.humanSeverity,
        humanOccurrence: risk.humanOccurrence,
        humanDetectability: risk.humanDetectability,
        humanInitialRisk: risk.priority,
        proposedAdditionalControls: risk.proposedControls.join("; "),
        requiredEvidence: risk.requiredEvidence.join("; "),
        evidenceQualityStatus: risk.evidenceStatus,
        residualSeverity: risk.humanSeverity,
        residualOccurrence: Math.max(1, (risk.humanOccurrence ?? risk.occurrence) - 1),
        residualDetectability: risk.humanDetectability,
        residualRpn: (risk.humanSeverity ?? risk.severity) * Math.max(1, (risk.humanOccurrence ?? risk.occurrence) - 1) * (risk.humanDetectability ?? risk.detectability),
        residualRiskClass: risk.priority,
        residualRiskRationale: risk.residualRiskRationale,
        aiConfidence: risk.confidence,
        deterministicGateResult: risk.deterministicGateResult,
        plausibilityCheckResult: risk.plausibilityResult,
        redTeamResult: risk.redTeamResult,
        reviewLevel: risk.reviewLevel,
        reviewStatus: risk.reviewStatus,
        smeReviewer: "Dr. Sam SME",
        qaApprover: "Quinn QA Approver",
        status: risk.status,
        version: risk.version
      }
    });

    for (const sourceId of risk.sourceLinks) {
      await prisma.riskSourceLink.create({
        data: {
          riskItemId: risk.id,
          sourceSnippetId: sourceId,
          claimText: risk.failureMode,
          linkType: "SOURCE_SUPPORT_OR_GAP_BASIS"
        }
      });
    }

    await prisma.riskItemVersion.create({
      data: {
        riskItemId: risk.id,
        version: risk.version,
        snapshotJson: JSON.stringify(risk)
      }
    });
  }

  for (const gap of demoGaps) {
    await prisma.gap.create({
      data: {
        id: gap.id,
        projectId: demoProject.id,
        riskItemId: gap.riskItemId,
        description: gap.description,
        priority: gap.priority,
        status: gap.status,
        question: gap.question
      }
    });
  }

  for (const check of demoPlausibilityChecks) {
    await prisma.plausibilityCheck.create({
      data: {
        id: check.id,
        projectId: demoProject.id,
        riskItemId: check.riskItemId,
        result: check.result,
        reviewerType: check.requiredHumanReviewerType,
        comments: check.comments,
        issueList: check.issues.join("; ")
      }
    });
  }

  for (const finding of demoRedTeamFindings) {
    await prisma.redTeamFinding.create({
      data: {
        id: finding.id,
        projectId: demoProject.id,
        category: finding.category,
        description: finding.description,
        sourceBasis: finding.sourceBasis,
        priority: finding.priority,
        status: finding.status
      }
    });
  }

  for (const artifact of generateValidationPack(demoProject.name)) {
    await prisma.validationArtifact.create({
      data: {
        projectId: demoProject.id,
        artifactType: artifact.title,
        title: artifact.title,
        content: artifact.content
      }
    });
  }

  for (const log of demoAuditLogs) {
    await prisma.auditLog.create({
      data: {
        id: log.id,
        timestamp: new Date(log.timestamp),
        action: log.action,
        entityType: log.entityType,
        entityId: log.entityId,
        beforeValue: null,
        afterValue: log.reason,
        reason: log.reason,
        eventPayloadHash: sha256(log),
        previousEventHash: log.previousEventHash
      }
    });
  }

  console.log("Seeded synthetic Pharma QRM Delta Engine demo data.");
}

main()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
