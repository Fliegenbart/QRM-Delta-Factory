# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `eu`
- Zeitpunkt: 2026-06-10T09:49:22+00:00
- Anthropic-Modell: `-`
- OpenAI-Modell: `-`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 23 von 25 versteckten Fehlern gefunden (92%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 127 von 143 Findings mit verifiziertem Zitat (89%)

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 35 | 12 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_02 | needs_human_review | 27 | 16 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_03 | completed | 18 | 11 | 2/2 | 0/2 | human_review_required |
| CASE_04 | needs_human_review | 39 | 16 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_05 | completed | 20 | 21 | 3/3 | 0/1 | human_review_required |
| CASE_06 | completed | 21 | 8 | 1/2 | 0/1 | human_review_required |
| CASE_07 | needs_human_review | 17 | 9 | 1/2 | 0/1 | blocked_due_to_model_failure |
| CASE_08 | needs_human_review | 29 | 16 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_09 | needs_human_review | 32 | 20 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_10 | completed | 20 | 14 | 3/3 | 0/1 | human_review_required |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): QA approval date (14.12.2026) is in the future relative to the deviation capture date (12.03.2026), violating ALCOA+ principles for data integrity and raising concerns about the validity of the approval process.
- ✅ `ERR_01_02` (high) — gefunden via evidence_fuzzy (Score 0.437): Batch disposition rationale for XYL-2026-004A is missing or incomplete. The QA release document (QA-RELEASE-XYL-004A) states the batch is approved for packaging, but lacks explicit justification linking the deviation impact assessment to the batch-specific disposition decision.
- ℹ️ 10 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Batch yield correction from 96.47% to 98.1% is justified by an incomplete weighing slip, but no evidence of QA approval or documented rationale for the correction is provided. This violates SOP-QA-004 Section 5.1 and SOP-DOC-005 Section 2.6.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_substring (Score 1.0): Adversarial review found required evidence missing or not clearly present in the claim ledger.
- ℹ️ 14 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Timestamp inconsistency detected between peak measurement (14:15) and employee entry (14:35) in deviation DEV-QS-2026-014. This raises concerns about the plausibility and integrity of electronic records, as the peak occurred before the recorded employee entry, which is temporally implausible.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): The CAPA action modifies the cleaning procedure for the walls of cleanroom R-202, but there is no documented evidence that the updated cleaning validation matrix or studies account for the transient particle peak or its potential impact on cleaning efficacy and residue levels.
- ℹ️ 9 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Inconsistencies in temperature measurements and operator logs for batch PAR-2026-H102 may indicate data integrity issues, but further review is required to confirm compliance with SOP-DI-002 Datenintegritaet Section 4.1.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Root cause for deviation DEV-P-2026-092 is stated as 'lack of attention' by the operator, but no evidence is provided to substantiate this claim, violating SOP-DEV-001 Abweichungsmanagement Section 6.2.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Batch PAR-2026-H102 is claimed to be 'quality compliant' and 'released for the next step' without documented QA approval, violating SOP-QA-004 QA Freigabe Section 5.1.
- ℹ️ 13 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): The sterilization cycle ZYK-STER-992 was performed on 11.05.2026, but the re-validation for autoclave AT-442 was completed in January 2026. There is no evidence that the specific loading patterns or materials used in this cycle were evaluated in the re-validation, creating a potential gap in validation coverage.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): The operator PNN-8812 accessed the sterile preparation room at 08:45, but the sterilization cycle had already started at 08:20. There is no evidence confirming the operator's presence or absence in the autoclave area prior to 08:45, which may impact sterility assurance.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): The operator PNN-8812 accessed the sterile preparation room at 08:45, but the sterilization cycle had already started at 08:20. There is no evidence confirming the operator's presence or absence in the autoclave area prior to 08:45, which may impact sterility assurance.
- ℹ️ 19 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_06

- ✅ `ERR_06_02` (critical) — gefunden via evidence_fuzzy (Score 0.486): Cross-document inconsistency detected: Deviation LAB-DEV-2026-031 cites a water content of 13.2% for raw material CS-AMX-9982, while the QA release document for batch AMO-SUP-2026-01 does not address this specification breach, violating SOP-DOC-005 Dokumentationspraxis Section 2.6.
- ❌ `ERR_06_01` (high) — übersehen: Akzeptanzkriterium der internen Spezifikation wird durch das Lieferanten-Zertifikat verletzt.
- ℹ️ 7 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): Batch impact assessment for batch MET-2026-C09 is incomplete. Net yield of 92.4% is below the specified tolerance range of 95.0% to 102.0%, but no documented disposition decision or linkage to batch records is provided.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 8 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): The deviation DEV-IBU-2026-112 lacks documented evidence that the validation scope for the tablet compression process covers the identified root cause (hairline crack in the upper punch). No bridging study or addendum is referenced to confirm the continued validity of the process post-deviation.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.697): Contradiction in deviation impact assessment: Claim states deviation DEV-IBU-2026-112 is an isolated single event with no influence on other batches, but no documented evidence of a comprehensive batch impact assessment listing all potentially affected batches as required by req_gs_deviation_impact and req_gs_batch_impact_completeness.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): The CAPA (CAPA-112-IBU) includes the installation of an inline metal detector and prioritizes its procurement and qualification. However, there is no documented effectiveness check to confirm the CAPA actions fully mitigate the risk of metallic fragments in the product.
- ℹ️ 13 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Inconsistencies in pH value reporting across documents for deviation DEV-CEF-77. Batch record states 'Werte stabil' while deviation report indicates pH drift above limit (7.85 vs 7.40). This violates SOP-DOC-005 Dokumentationspraxis Section 2.6 and poses a medium risk to data integrity.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Root cause investigation for pH drift deviation (DEV-CEF-77) is incomplete and unresolved, violating SOP-DEV-001 Abweichungsmanagement Section 6.2. This poses a high risk to product quality and regulatory compliance due to lack of actionable corrective measures.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Missing signature of Quality Control Head in change control document (CC-2026-104) violates SOP-QA-004 QA Freigabe Section 5.1 and SOP-DI-002 Datenintegritaet Section 4.1, posing a high risk to data integrity and regulatory compliance.
- ℹ️ 17 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): The unknown impurity level in batch INS-GLA-2025-05 exceeds the specified limit of 0.20% (measured at 0.32%), indicating a deviation that requires a documented impact assessment and CAPA. The deviation is currently assessed as a temporary outlier, but the lack of immediate corrective actions or bridging studies raises concerns about sterility assurance and product quality.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Missing documented evidence of audit trail review for electronic records related to batch INS-GLA-2025-05. Requirement req_gs_data_integrity_signatures mandates that electronic signatures and audit trails must comply with ALCOA+ principles, including plausibility and consistency checks. No evidence of such review was found in the provided claims.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Cross-document inconsistency detected: Batch INS-GLA-2025-05 is claimed to meet analytical requirements provisionally, but unknown impurity exceeds specification limit without clear resolution.
- ℹ️ 11 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
