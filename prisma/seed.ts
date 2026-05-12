import { PrismaClient } from "@prisma/client";

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

  console.log("Initialized empty Pharma QRM Delta Engine database.");
}

main()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
