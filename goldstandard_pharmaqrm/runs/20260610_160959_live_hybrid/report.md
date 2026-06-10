# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-06-10T16:09:59+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 23 von 25 versteckten Fehlern gefunden (92%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 228 von 236 Findings mit verifiziertem Zitat (97%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 10 | 111,077 | 74,401 | 185,478 |
| extraction:mistral | 10 | 34,852 | 27,119 | 61,971 |
| mistral | 70 | 721,491 | 208,024 | 929,515 |
| openai | 10 | 102,793 | 28,674 | 131,467 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 34 | 16 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_02 | completed | 23 | 26 | 2/2 | 0/1 | human_review_required |
| CASE_03 | completed | 19 | 20 | 2/2 | 0/2 | human_review_required |
| CASE_04 | needs_human_review | 30 | 22 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_05 | completed | 18 | 27 | 3/3 | 0/1 | human_review_required |
| CASE_06 | needs_human_review | 20 | 20 | 1/2 | 0/1 | blocked_due_to_model_failure |
| CASE_07 | needs_human_review | 21 | 26 | 1/2 | 0/1 | blocked_due_to_model_failure |
| CASE_08 | needs_human_review | 35 | 24 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_09 | needs_human_review | 32 | 23 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_10 | needs_human_review | 21 | 32 | 3/3 | 0/1 | blocked_due_to_model_failure |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): The QA approval signature date (14.12.2026) is in the future relative to the deviation recording date (12.03.2026), violating ALCOA+ principles for data integrity as required by SOP-DI-002.
- ✅ `ERR_01_02` (high) — gefunden via evidence_fuzzy (Score 0.437): The batch impact assessment for XYL-2026-004A does not explicitly list all potentially affected batches or link the disposition decision to batch records, as required by the QRM Batch Impact Checkliste.
- ℹ️ 14 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Electronic signature and timestamp for the batch record correction (yield adjustment to 98.1%) lack evidence of audit trail review and plausibility check. The timestamp (2026-04-04T06:15:00) is not corroborated by a documented audit trail review, violating ALCOA+ principles for data integrity.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_substring (Score 1.0): Adversarial review found required evidence missing or not clearly present in the claim ledger.
- ℹ️ 24 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): The deviation report records an employee entry time (14:35) that is after the peak measurement time (14:15). This temporal inconsistency may indicate a data integrity issue, as the employee entry could not have caused the particle peak if it occurred later.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): The CAPA action (CAPA-2026-014) adjusts the cleaning procedure for the walls of Room R-202, but there is no evidence that the cleaning validation matrix has been updated to cover the new procedure or the conditions leading to the particle deviation. This may result in inadequate cleaning validation for the changed scope.
- ℹ️ 18 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): The deviation DEV-P-2026-092 involved a temperature excursion (44.5°C for 3 minutes) exceeding the specified limit (42.0°C) during the drying phase of batch PAR-2026-H102. The sterility assurance impact of this temperature excursion on the product and process has not been explicitly documented or validated.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): The deviation report (doc_f2fdec7f28274d6e993ba2e699a3d8a5) identifies the suspected root cause as a stuck valve in the heating register of the air supply system (equipment failure). However, the CAPA document (doc_92bac35e4c44459b9861e7135d1b9bd5) attributes the root cause to 'lack of attention by operating personnel during temperature monitoring' (operator error) and assigns retraining as the sole CAPA action. These are contradictory root causes. If the true root cause is equipment failure (stuck valve), operator retraining is an inadequate and misdirected CAPA that will not prevent recurrence. No evidence of valve inspection, repair, or preventive maintenance is present in any claim.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): CAPA closure rationale for deviation DEV-P-2026-092 is partially documented but lacks explicit linkage to effectiveness check results, creating potential compliance gap.
- ℹ️ 19 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): The loading patterns and maximum allowable weights for the sterilization cycle ZYK-STER-992 are referenced in Annex 4 but are not explicitly confirmed as compliant in the provided documents. This introduces uncertainty regarding adherence to validated cleaning and loading procedures.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): The timeline of operator presence and process execution raises data integrity concerns. The operator (PNN-8812) is recorded as entering the preparation room at 08:45, while the sterilization program started at 08:20. This discrepancy suggests potential issues with the audit trail or process documentation.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): The timeline of operator presence and process execution raises data integrity concerns. The operator (PNN-8812) is recorded as entering the preparation room at 08:45, while the sterilization program started at 08:20. This discrepancy suggests potential issues with the audit trail or process documentation.
- ℹ️ 25 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_06

- ✅ `ERR_06_02` (critical) — gefunden via evidence_fuzzy (Score 0.718): The supplier's analysis certificate confirms conformity of the active substance, but the internal re-analysis revealed a water content deviation (13.2%). No documented reconciliation or root-cause analysis is provided to address the discrepancy between supplier and internal test results.
- ❌ `ERR_06_01` (high) — übersehen: Akzeptanzkriterium der internen Spezifikation wird durch das Lieferanten-Zertifikat verletzt.
- ℹ️ 19 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): Batch impact assessment for deviation DEV-MET-09 lacks documented disposition rationale for batch MET-2026-C09, despite yield falling below the specified tolerance range (92.4% vs. 95.0%-102.0%). No evidence of QA disposition decision or justification for batch release is provided.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 25 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): The batch impact assessment for CAPA-112-IBU states that the deviation is an isolated incident with no effect on other batches. However, historical deviations (DEV-IBU-2026-042, DEV-IBU-2026-081) on the same equipment (TAB-02) suggest a potential pattern that may not have been fully evaluated.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.697): The deviation involves a tooling failure during tablet compression, which may compromise the sterility assurance of the final product. There is no documented evidence that the sterility assurance protocols address the risk of metallic contamination or tooling failures in the compression process.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): CAPA action for deviation DEV-IBU-2026-112 includes installation of an inline metal detector, but there is no documented effectiveness check or validation deadline aligned with the CAPA record.
- ℹ️ 21 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Operator OPERATOR-TL manually changed the pH setpoint from 7.20 to 7.70 at 14:15 on 05.05.2026, deliberately raising it above the specified upper limit of pH 7.40. This action directly caused or enabled the pH excursion to 7.85. The batch record handwritten note states 'no special incidents, values stable', which directly contradicts the SCADA-documented warning, manual override, and 6-hour pH excursion. This constitutes a data integrity violation under ALCOA+ (contemporaneous, accurate) and a false entrainment in the batch record.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): CAPA effectiveness check evidence is missing for deviation DEV-CEF-77. No documented effectiveness check or verification of corrective actions was found, violating requirement req_gs_capa_effectiveness.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Quality Control Lead signature is missing in change control CC-2026-104, violating requirement req_gs_qa_approval_documented. QA approval is incomplete without all required signatures.
- ℹ️ 20 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Inconsistency in impact assessment: The deviation for unknown impurity is initially assessed as a temporary outlier with no immediate impact, yet a CAPA plan (CAPA-OOS-INS) is initiated, suggesting a more serious issue. This contradiction requires clarification.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): The CAPA plan (CAPA-OOS-INS) lacks a documented effectiveness check and responsible party. The implementation target date is set for 2026-05-16, but there is no evidence of a planned or executed effectiveness check to verify the CAPA's success in addressing the impurity deviation.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): The batch impact assessment for INS-GLA-2025-05 lacks a complete list of all potentially affected batches. While the assessment states no regulatory measures are required, there is no documented linkage between the deviation, the batch record, and the disposition decision.
- ℹ️ 29 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
