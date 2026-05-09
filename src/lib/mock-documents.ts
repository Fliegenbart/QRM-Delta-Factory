/**
 * Realistic Mock Documents for Multi-Agent Analysis
 *
 * These documents contain intentional issues that should be found:
 * 1. Missing validation evidence for new threshold
 * 2. Training gap for operators
 * 3. Conflicting statements about audit trail scope
 * 4. Unclear batch reconciliation criteria
 * 5. Potential data integrity concerns
 */

export const realisticDocuments = {
  changeControl: {
    id: "doc-cc-2026-014",
    type: "change-control",
    title: "CC-2026-014: AVI Rejection Threshold Modification",
    content: `
CHANGE CONTROL RECORD
=====================
CC Number: CC-2026-014
Date Initiated: 2026-03-15
Initiator: Dr. Marcus Weber, Process Engineering
Status: PENDING QRM REVIEW

1. DESCRIPTION OF CHANGE
------------------------
Modification of the automated visual inspection (AVI) rejection threshold
for sterile injectable products from 0.85 to 0.72 sensitivity setting.

The current threshold (0.85) results in a false reject rate of approximately
12.3% which impacts batch yield and production efficiency. The proposed
threshold (0.72) is expected to reduce false rejects to approximately 4.8%
while maintaining acceptable detection capability.

2. JUSTIFICATION
----------------
- Current false reject rate exceeds target of <8%
- Similar threshold used successfully at sister facility (Site B)
- Engineering assessment indicates detection capability maintained
- Potential annual savings of €2.4M through reduced reprocessing

3. IMPACT ASSESSMENT (PRELIMINARY)
----------------------------------
☐ Process validation impact - TO BE DETERMINED
☐ SOP updates required - YES (SOP-AVI-001, SOP-AVI-003)
☑ Training required - YES, all AVI operators (12 persons)
☐ Equipment qualification impact - UNDER REVIEW
☑ Risk assessment required - YES, QRM delta analysis

4. REGULATORY CONSIDERATIONS
----------------------------
Change category: Manufacturing process parameter modification
Prior approval required: NO (per internal SOP-CC-001 v4.2)
Post-implementation notification: YES, within 30 days per regional requirements

5. PROPOSED IMPLEMENTATION TIMELINE
-----------------------------------
Phase 1: Validation protocol execution - 4 weeks
Phase 2: SOP revision and training - 2 weeks
Phase 3: Controlled production runs - 3 batches
Phase 4: Full implementation - pending QA approval

6. ATTACHMENTS
--------------
☐ Engineering Assessment Report (EA-2026-0892) - ATTACHED
☐ Validation Protocol (VP-AVI-THR-001) - DRAFT, NOT YET APPROVED
☐ Training Plan - NOT YET DEVELOPED
☑ Sister Site Comparison Data - ATTACHED (limited scope)

SIGNATURES
----------
Initiator: Dr. Marcus Weber _____________ Date: 2026-03-15
QA Review: PENDING
QRM Review: PENDING
    `.trim()
  },

  validationReport: {
    id: "doc-val-2025",
    type: "validation-report",
    title: "Validation Report VAL-AVI-2025-003",
    content: `
VALIDATION REPORT
=================
Document: VAL-AVI-2025-003
Title: AVI System Performance Qualification
Status: APPROVED
Approval Date: 2025-08-22

EXECUTIVE SUMMARY
-----------------
This validation report documents the performance qualification of the
automated visual inspection system installed on Filling Line 3.

SCOPE
-----
This validation covers:
- System installation verification
- Operational qualification at CURRENT threshold setting (0.85)
- Performance qualification with standard defect set
- Audit trail functionality verification

IMPORTANT LIMITATION:
This validation was performed at the CURRENT threshold setting of 0.85.
Performance at alternative threshold settings has NOT been validated.

TEST RESULTS SUMMARY
--------------------
| Test | Result | Acceptance Criteria |
|------|--------|---------------------|
| IQ-001 Installation | PASS | Per equipment specs |
| OQ-001 Functionality | PASS | All functions operate |
| OQ-002 Alarm Testing | PASS | Alarms trigger correctly |
| PQ-001 Sensitivity @ 0.85 | PASS | >99.5% detection rate |
| PQ-002 False Reject @ 0.85 | MARGINAL | 12.3% (target <10%) |
| PQ-003 Defect Set Coverage | PASS | All 15 defect types detected |
| DI-001 Audit Trail | PASS | All events logged |

DEVIATIONS DURING VALIDATION
----------------------------
DEV-VAL-2025-018: False reject rate exceeded target (12.3% vs <10%)
Status: Closed with justification - operational acceptance approved
Note: Higher false reject rate accepted due to conservative threshold
      setting for patient safety considerations.

CONCLUSION
----------
The AVI system is validated for use at the current threshold setting (0.85).

⚠️ WARNING: Any change to threshold settings requires revalidation or
   a documented engineering assessment with QRM review.

Prepared by: Sarah Chen, Validation Engineer
Reviewed by: Dr. James Morrison, Validation Manager
Approved by: Lisa Schmidt, QA Director
    `.trim()
  },

  sopAviOperation: {
    id: "doc-sop-avi-001",
    type: "sop",
    title: "SOP-AVI-001: AVI System Operation",
    content: `
STANDARD OPERATING PROCEDURE
============================
Document: SOP-AVI-001
Title: Automated Visual Inspection System Operation
Version: 4.2
Effective Date: 2025-09-01
Review Date: 2026-09-01

1. PURPOSE
----------
This SOP describes the operation of the automated visual inspection
system for sterile injectable products.

2. SCOPE
--------
Applies to all personnel operating the AVI system on Filling Line 3.

3. RESPONSIBILITIES
-------------------
3.1 Operators: Execute AVI operations per this procedure
3.2 Supervisors: Ensure compliance, review batch records
3.3 QA: Audit trail review, batch release decisions

4. PROCEDURE
------------
4.1 PRE-BATCH SETUP
   4.1.1 Verify recipe selection matches batch record
   4.1.2 Confirm threshold setting [CURRENTLY: 0.85]
   4.1.3 Execute challenge test with reference standards
   4.1.4 Document setup verification in batch record

4.2 BATCH OPERATION
   4.2.1 Start inspection sequence per batch record
   4.2.2 Monitor reject rate continuously
   4.2.3 If reject rate exceeds 15%, STOP and notify supervisor
   4.2.4 Document any stoppages or anomalies

4.3 POST-BATCH ACTIVITIES
   4.3.1 Record final counts: accepted, rejected, manual review
   4.3.2 Perform batch reconciliation calculation
   4.3.3 Archive electronic records
   4.3.4 Clean and prepare for next batch

5. TRAINING REQUIREMENTS
------------------------
Personnel must complete:
- TRN-AVI-001: AVI System Basics (4 hours)
- TRN-AVI-002: Defect Recognition (8 hours)
- TRN-AVI-003: Troubleshooting (4 hours)
- Annual requalification

NOTE: Training records are maintained in the Learning Management System.
      Current training status must be verified before independent operation.

6. REFERENCES
-------------
- VAL-AVI-2025-003: Validation Report
- PM-AVI-001: Preventive Maintenance Procedure
- SOP-BR-001: Batch Record Completion

REVISION HISTORY
----------------
v4.2 (2025-09-01): Updated threshold reference to 0.85
v4.1 (2025-03-15): Added challenge test requirement
v4.0 (2024-12-01): Major revision for new equipment
    `.trim()
  },

  deviationRecord: {
    id: "doc-dev-2026-118",
    type: "deviation",
    title: "DEV-2026-118: Batch Reconciliation Discrepancy",
    content: `
DEVIATION RECORD
================
Deviation Number: DEV-2026-118
Date Identified: 2026-04-02
Batch Number: B2026-1847
Product: Sterile Injectable Product A

DESCRIPTION
-----------
During batch record review, a discrepancy was identified in the AVI
reconciliation section. The batch record wording is ambiguous regarding
how manually re-inspected units should be counted.

Current batch record states:
"Total units = Accepted + Rejected + Re-inspected"

However, re-inspected units are either ultimately accepted or rejected,
leading to potential double-counting.

For batch B2026-1847:
- Accepted: 18,432
- Rejected: 2,891
- Re-inspected: 847
- Expected total: 21,323 (per filling record)
- Calculated per BR: 22,170 (overcounted by 847)

IMMEDIATE ACTIONS
-----------------
1. Batch held pending investigation
2. Manual reconciliation performed - no missing units
3. QA notified

ROOT CAUSE (PRELIMINARY)
------------------------
Batch record reconciliation formula is unclear. The field "Re-inspected"
should clarify whether these units are ADDITIONAL to accepted/rejected
or a SUBSET that were manually reviewed.

INVESTIGATION STATUS: ONGOING

CAPA REFERENCE
--------------
To be assigned pending investigation completion.

RISK ASSESSMENT NOTE
--------------------
⚠️ This deviation may indicate a systemic issue with batch record design
   that could affect data integrity and audit trail accuracy. QRM review
   recommended to assess impact on threshold change implementation.

Reported by: Michael Torres, Production Supervisor
Investigated by: PENDING ASSIGNMENT
    `.trim()
  },

  auditTrailReview: {
    id: "doc-atr-2026-q1",
    type: "audit-trail-review",
    title: "Periodic Audit Trail Review Q1-2026",
    content: `
PERIODIC AUDIT TRAIL REVIEW RECORD
==================================
Review Period: Q1 2026 (January - March)
System: AVI Inspection System - Line 3
Reviewer: Jennifer Adams, Data Integrity Specialist
Review Date: 2026-04-08

1. SCOPE OF REVIEW
------------------
This periodic review covers:
☑ User access rights
☑ Login/logout events
☑ Recipe changes
☐ Threshold setting changes [NOT IN CURRENT CHECKLIST SCOPE]
☑ Alarm acknowledgments
☑ Data modifications (if any)

2. FINDINGS
-----------
2.1 USER ACCESS
   - 14 active users reviewed
   - 2 terminated employees still had active accounts (now disabled)
   - Finding: MINOR - accounts disabled, no unauthorized access detected

2.2 RECIPE CHANGES
   - 3 recipe changes during period
   - All properly authorized and documented
   - Finding: COMPLIANT

2.3 ALARM EVENTS
   - 127 alarm events logged
   - All acknowledged within 15 minutes
   - Finding: COMPLIANT

2.4 DATA MODIFICATIONS
   - No data modifications detected
   - Finding: COMPLIANT

3. LIMITATIONS
--------------
⚠️ IMPORTANT: The current audit trail review checklist (CHK-ATR-001 v2.1)
   does NOT explicitly include review of threshold parameter changes.

   Threshold changes are logged in the audit trail but are not part of
   the standard periodic review scope. This may represent a gap in the
   data integrity oversight program.

4. RECOMMENDATIONS
------------------
1. Disable user accounts within 24 hours of termination (vs current 7 days)
2. Consider adding threshold parameter changes to review checklist
3. Evaluate need for more frequent reviews during change control periods

5. CONCLUSION
-------------
The audit trail review for Q1 2026 is COMPLETE with minor findings.
Two recommendations for process improvement are raised.

Reviewer: Jennifer Adams _____________ Date: 2026-04-08
Manager Approval: Thomas Brown _____________ Date: 2026-04-10
    `.trim()
  },

  trainingRecords: {
    id: "doc-trn-status",
    type: "training-status",
    title: "AVI Operator Training Status Report",
    content: `
TRAINING STATUS REPORT
======================
Report Date: 2026-04-15
System: AVI Inspection System - Line 3
Report Generated By: Learning Management System

REQUIRED TRAINING FOR AVI OPERATION
-----------------------------------
TRN-AVI-001: AVI System Basics (4 hours)
TRN-AVI-002: Defect Recognition (8 hours)
TRN-AVI-003: Troubleshooting (4 hours)

CURRENT TRAINING STATUS
-----------------------
| Employee ID | Name | TRN-001 | TRN-002 | TRN-003 | Status |
|-------------|------|---------|---------|---------|--------|
| EMP-1001 | A. Smith | ✓ | ✓ | ✓ | QUALIFIED |
| EMP-1002 | B. Jones | ✓ | ✓ | ✓ | QUALIFIED |
| EMP-1003 | C. Davis | ✓ | ✓ | ✓ | QUALIFIED |
| EMP-1004 | D. Wilson | ✓ | ✓ | ✓ | QUALIFIED |
| EMP-1005 | E. Brown | ✓ | ✓ | ✓ | QUALIFIED |
| EMP-1006 | F. Taylor | ✓ | ✓ | EXPIRED | REQUALIFY |
| EMP-1007 | G. Anderson | ✓ | ✓ | ✓ | QUALIFIED |
| EMP-1008 | H. Thomas | ✓ | ✓ | ✓ | QUALIFIED |
| EMP-1009 | I. Jackson | ✓ | PENDING | - | IN TRAINING |
| EMP-1010 | J. White | ✓ | ✓ | ✓ | QUALIFIED |
| EMP-1011 | K. Harris | ✓ | ✓ | ✓ | QUALIFIED |
| EMP-1012 | L. Martin | NEW | NEW | NEW | NOT STARTED |

SUMMARY
-------
Total operators assigned: 12
Fully qualified: 9 (75%)
Requiring requalification: 1
Currently in training: 1
Not yet started: 1

⚠️ CRITICAL GAP FOR CC-2026-014:
No training curriculum has been developed for the new threshold setting.
Current training materials reference the 0.85 threshold exclusively.

If the threshold change is implemented, ALL operators will require
supplemental training on:
- New threshold value and rationale
- Updated challenge test procedures (if changed)
- Modified acceptance criteria

TRAINING DEVELOPMENT STATUS: NOT STARTED
ESTIMATED DEVELOPMENT TIME: 2-3 weeks
ESTIMATED DEPLOYMENT TIME: 1 week per shift (3 shifts total)

Report Distribution: QA, Training, Production Management
    `.trim()
  },

  engineeringAssessment: {
    id: "doc-ea-2026-0892",
    type: "engineering-assessment",
    title: "Engineering Assessment EA-2026-0892",
    content: `
ENGINEERING ASSESSMENT
======================
Document: EA-2026-0892
Subject: AVI Threshold Modification Technical Feasibility
Prepared by: Engineering Department
Date: 2026-03-10

1. OBJECTIVE
------------
Assess technical feasibility of modifying AVI rejection threshold
from 0.85 to 0.72 while maintaining acceptable detection capability.

2. METHODOLOGY
--------------
- Review of equipment manufacturer specifications
- Analysis of historical inspection data (24 months)
- Comparison with sister facility (Site B) operating at 0.70
- Statistical modeling of detection rates

3. TECHNICAL ANALYSIS
---------------------
3.1 DETECTION CAPABILITY
   Current (0.85): 99.7% detection rate for critical defects
   Projected (0.72): 98.9% detection rate for critical defects

   ⚠️ NOTE: This is a PROJECTED value based on modeling.
   Actual performance at 0.72 has NOT been tested on this equipment.

3.2 FALSE REJECT ANALYSIS
   Current (0.85): 12.3% false reject rate
   Projected (0.72): 4.8% false reject rate

   Projected annual savings: €2.4M (reduced reprocessing)

3.3 SISTER SITE COMPARISON
   Site B operates at 0.70 threshold with:
   - Detection rate: 98.5%
   - False reject rate: 3.2%

   ⚠️ IMPORTANT LIMITATIONS:
   - Site B has different equipment model (AVI-3000 vs our AVI-2500)
   - Site B processes different product portfolio
   - Direct comparison may not be valid

4. RISK CONSIDERATIONS
----------------------
4.1 PRIMARY RISK
   Reduced threshold may allow marginally defective units to pass.
   Probability: Low (based on modeling)
   Impact: High (patient safety)

4.2 MITIGATION
   - Enhanced post-change monitoring (first 10 batches)
   - Retain manual re-inspection for borderline rejects
   - Establish rollback criteria

5. CONCLUSION
-------------
From an engineering perspective, the threshold change is TECHNICALLY
FEASIBLE. However, this assessment:

✓ Confirms equipment can operate at 0.72
✗ Does NOT validate actual detection performance at 0.72
✗ Does NOT replace formal validation requirements
✗ Does NOT address regulatory or quality risk aspects

RECOMMENDATION:
Proceed with validation protocol development, but formal validation
MUST be completed before production implementation.

Prepared by: Dr. Marcus Weber, Process Engineering
Reviewed by: Anna Kowalski, Engineering Manager
    `.trim()
  }
};

/**
 * Convert realistic documents to source snippets for the orchestrator
 */
export function getRealisticSourceSnippets() {
  const documents = realisticDocuments;

  return [
    {
      id: "snip-cc-summary",
      documentId: documents.changeControl.id,
      documentType: "change-control",
      sectionTitle: "Change Description and Impact",
      content: documents.changeControl.content,
      lineReference: "full document",
      snippetHash: "cc-2026-014-hash"
    },
    {
      id: "snip-val-scope",
      documentId: documents.validationReport.id,
      documentType: "validation-report",
      sectionTitle: "Validation Scope and Limitations",
      content: documents.validationReport.content,
      lineReference: "full document",
      snippetHash: "val-2025-003-hash"
    },
    {
      id: "snip-sop-procedure",
      documentId: documents.sopAviOperation.id,
      documentType: "sop",
      sectionTitle: "AVI Operation Procedure",
      content: documents.sopAviOperation.content,
      lineReference: "full document",
      snippetHash: "sop-avi-001-hash"
    },
    {
      id: "snip-deviation",
      documentId: documents.deviationRecord.id,
      documentType: "deviation",
      sectionTitle: "Batch Reconciliation Issue",
      content: documents.deviationRecord.content,
      lineReference: "full document",
      snippetHash: "dev-2026-118-hash"
    },
    {
      id: "snip-audit-trail",
      documentId: documents.auditTrailReview.id,
      documentType: "audit-trail-review",
      sectionTitle: "Periodic Audit Trail Review",
      content: documents.auditTrailReview.content,
      lineReference: "full document",
      snippetHash: "atr-2026-q1-hash"
    },
    {
      id: "snip-training",
      documentId: documents.trainingRecords.id,
      documentType: "training-records",
      sectionTitle: "Operator Training Status",
      content: documents.trainingRecords.content,
      lineReference: "full document",
      snippetHash: "trn-status-hash"
    },
    {
      id: "snip-engineering",
      documentId: documents.engineeringAssessment.id,
      documentType: "engineering-assessment",
      sectionTitle: "Technical Feasibility Assessment",
      content: documents.engineeringAssessment.content,
      lineReference: "full document",
      snippetHash: "ea-2026-0892-hash"
    }
  ];
}

/**
 * Summary of expected findings for UI display
 */
export const expectedFindings = {
  criticalGaps: [
    {
      id: "gap-val-new-threshold",
      title: "Missing Validation for New Threshold",
      description: "Validation report VAL-AVI-2025-003 explicitly states it covers ONLY the 0.85 threshold. No validation data exists for the proposed 0.72 threshold.",
      source: "VAL-AVI-2025-003",
      severity: "CRITICAL",
      requiresHuman: true
    },
    {
      id: "gap-training-curriculum",
      title: "No Training Developed for New Threshold",
      description: "Training status report indicates NO curriculum exists for the threshold change. All 12 operators would need new training.",
      source: "Training Status Report",
      severity: "HIGH",
      requiresHuman: true
    }
  ],
  dataIntegrityIssues: [
    {
      id: "di-audit-trail-scope",
      title: "Audit Trail Review Gap",
      description: "Periodic audit trail review does NOT include threshold parameter changes in its scope. This is a potential data integrity oversight gap.",
      source: "ATR-2026-Q1",
      severity: "HIGH",
      requiresHuman: true
    },
    {
      id: "di-reconciliation",
      title: "Batch Reconciliation Formula Unclear",
      description: "DEV-2026-118 documents ambiguous reconciliation wording that could lead to data integrity issues.",
      source: "DEV-2026-118",
      severity: "MEDIUM",
      requiresHuman: true
    }
  ],
  engineeringLimitations: [
    {
      id: "eng-sister-site",
      title: "Sister Site Comparison Not Valid",
      description: "Engineering assessment notes Site B uses different equipment model (AVI-3000 vs AVI-2500) - direct comparison may not be valid.",
      source: "EA-2026-0892",
      severity: "MEDIUM",
      requiresHuman: true
    },
    {
      id: "eng-projected-only",
      title: "Detection Rate is Projected, Not Tested",
      description: "The 98.9% detection rate at 0.72 is based on modeling only. Actual performance has NOT been tested.",
      source: "EA-2026-0892",
      severity: "HIGH",
      requiresHuman: true
    }
  ]
};
