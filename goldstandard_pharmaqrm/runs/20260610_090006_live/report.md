# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live`
- Zeitpunkt: 2026-06-10T09:00:06+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-4o`

## Gesamtergebnis

- **Sensitivität:** 13 von 25 versteckten Fehlern gefunden (52%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 128 von 156 Findings mit verifiziertem Zitat (82%)

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 54 | 31 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_02 | needs_human_review | 33 | 25 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_03 | needs_human_review | 24 | 29 | 2/2 | 0/2 | blocked_due_to_model_failure |
| CASE_04 | completed | 39 | 33 | 3/3 | 0/1 | human_review_required |
| CASE_05 | needs_human_review | 21 | 18 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_06 | needs_human_review | 15 | 20 | 1/2 | 0/1 | blocked_due_to_model_failure |
| CASE_07 | failed | 0 | 0 | 0/2 | 0/1 | - |
| CASE_08 | failed | 0 | 0 | 0/3 | 0/1 | - |
| CASE_09 | failed | 0 | 0 | 0/3 | 0/1 | - |
| CASE_10 | failed | 0 | 0 | 0/3 | 0/1 | - |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): The QA review signature on deviation DEV-2026-891 is dated 14.12.2026, which is approximately 9 months after the deviation recording date of 12.03.2026 and approximately 9 months after the batch release decision of 25.03.2026. The batch XYL-2026-004A was released for packaging on 25.03.2026 (QA-RELEASE-XYL-004A) before the QA review of the deviation was completed (14.12.2026). This constitutes a data integrity finding under req_gs_data_integrity_signatures and a QA approval sequencing failure under req_gs_qa_approval_documented. A batch released before QA deviation review is complete represents a potential product quality and regulatory risk.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): The deviation classification as 'Minor' with exclusion of product quality impact is based solely on visual homogeneity assessment. No physicochemical analytical data (e.g., assay, particle size, rheology specification compliance) is cited to support the impact exclusion. Per req_gs_deviation_classification, classification without reliable physicochemical data is not permissible. The viscosity increase observed during the temperature drop (2400 to 2910 mPas) is noted but no specification limits for viscosity are provided, making it impossible to confirm the 'Minor' classification is adequately supported.
- ℹ️ 29 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): A yield value in batch record CPH-2026-991 was struck through (96.47%) and altered to 98.1% with only operator initials 'TS' and a brief note citing an incomplete weighing document. No CAPA record, no deviation report, no QA approval, no date of correction, and no effectiveness check are documented. The corrected value (98.1%) was then accepted by QA release without apparent scrutiny of the alteration. This constitutes a data integrity violation and an undocumented deviation with no CAPA linkage, no root-cause analysis, and no impact assessment on batch CPH-2026-991 or any other potentially affected batch.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_substring (Score 1.0): Adversarial review found required evidence missing or not clearly present in the claim ledger.
- ℹ️ 23 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): There is a temporal inconsistency between the recorded time of the particle peak and the employee entry time, which could indicate a data integrity issue.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): The SOP referenced in CAPA-2026-014 (SOP-QS-REIN-001, Version 2.0, valid from 2018-01-12) is over 8 years old relative to the deviation date of 2026-04-18. No evidence is present that this SOP version is current, has been reviewed for applicability to the current process state, or that a change control was initiated to update it. Per req_gs_qa_approval_documented, SOP and change references must be version-consistent, and per req_gs_validation_coverage, cleaning evidence must cover the current process state.
- ℹ️ 27 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): The batch record for PAR-2026-H102 (WS-03) shows a product temperature of 48.2°C at 13:30, which significantly exceeds both the specification limit of 42.0°C and the maximum value of 44.5°C documented in the deviation report DEV-P-2026-092. The deviation report states the temperature rose to a maximum of 44.5°C for 3 minutes, but the batch record shows 48.2°C. This is a material cross-document inconsistency. The impact assessment and CAPA are based on the 44.5°C figure; if the actual peak was 48.2°C, the impact assessment and CAPA scope may be insufficient.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): The CAPA root cause is attributed solely to 'insufficient operator attention during temperature monitoring' (mangelnde Aufmerksamkeit des Bedienpersonals). However, the deviation report (DEV-P-2026-092) identifies a suspected stuck valve in the heating register of the supply air system as the root cause. These two root cause attributions are contradictory. Per req_gs_deviation_classification, root cause attributions such as 'operator error' must be substantiated. The CAPA action (retraining) is based on the operator-error root cause, but if the actual root cause is a mechanical/equipment failure (stuck valve), the CAPA is misdirected and will not prevent recurrence.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): The batch review document for PAR-2026-H102 states the batch is quality-compliant and released for the next processing step, but no approver name, role, or date is documented for this QA approval. Per req_gs_qa_approval_documented, QA approvals must be documented before closure; planned but undocumented approvals are not sufficient. The absence of a named QA approver and approval date means the release decision cannot be traced or verified.
- ℹ️ 30 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): The validation note VAL-NOTE-AT-442 confirms that autoclave AT-442 was released for program 'Standard-Zubehör-121' following re-validation in January 2026, and that exact loading patterns and maximum total weights for glassware are documented in Annex 4. However, the sterilization cycle record ZYK-STER-992 does not reference or confirm compliance with the validated loading pattern (Annex 4). Without this confirmation, it cannot be verified that the cycle was performed within the validated state.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): The cleanroom security report states that employee PNN-8812 entered the personnel airlock to the preparation room (R-102) at 08:45 and had no prior presence in the autoclave area before 08:45. However, the sterilization cycle ZYK-STER-992 shows loading completed at 08:15 and program start at 08:20. This means the loading and program initiation of the sterilization cycle were performed before PNN-8812 could physically have been present in the area, according to the access control system. This is a temporal impossibility that raises serious concerns about who actually loaded and started the autoclave, and whether the sterilization record accurately reflects the actual execution.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): The sterilization cycle ZYK-STER-992 on autoclave AT-442 was documented as executed by employee P.M. (personnel number PNN-8812), but the cleanroom security report for the same date (2026-05-11) records that personnel number PNN-8812 has initials 'A.S.' in the electronic system. This is a direct identity contradiction across documents for the same personnel number on the same day, constituting a data integrity finding under ALCOA+ requirements. The executing person's identity cannot be unambiguously established, which undermines the traceability and integrity of the sterilization record.
- ℹ️ 15 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Batch CS-AMX-9982 water content (13.2%) exceeds the upper specification limit of 12.8% per Prüf-Spez-API-04, yet the supplier CoA (doc_da2a581158644755bf41b5460602063a) records the batch as released ('Freigegeben durch Qualitätskontrolle ChemieSynthese'). This constitutes a confirmed out-of-specification result against a critical process parameter. Per req_gs_spec_limits, specification exceedances must be evaluated as deviations even if the product appears visually unremarkable. The supplier release status is inconsistent with the OOS finding documented in the deviation report, representing a cross-document contradiction requiring immediate human QA review.
- ❌ `ERR_06_02` (critical) — übersehen: Wirkstofffreigabe durch QA trotz ungelöster und aktive Laborabweichung.
- ℹ️ 19 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ❌ `ERR_07_01` (high) — übersehen: Yield-Unterschreitung wird fälschlicherweise als konform deklariert.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.

### CASE_08

- ❌ `ERR_08_01` (critical) — übersehen: Unerkannter bzw. bewusst ignorierter Wiederholungsfehler (Trend-Fehler) bei Stempelbeschädigungen.
- ❌ `ERR_08_02` (high) — übersehen: Mangelhafte Ausdehnung des Batch-Impact-Assessments auf potenziell mitbetroffene Vorgängerchargen.
- ❌ `ERR_08_03` (medium) — übersehen: Unrealistisches, nicht plausibles CAPA-Zieldatum ohne adäquate Projektrealisierungszeit.

### CASE_09

- ❌ `ERR_09_01` (critical) — übersehen: Intentionale Falschdokumentation im Batch Record im Widerspruch zum SCADA-Audit-Trail.
- ❌ `ERR_09_02` (high) — übersehen: Fehlerhafte Root-Cause-Ermittlung durch Ignorieren der System-Logfiles.
- ❌ `ERR_09_03` (medium) — übersehen: Unvollständig genehmigtes Change-Control-Dokument ohne finale QK-Freigabe.

### CASE_10

- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- ❌ `ERR_10_02` (high) — übersehen: Fehlende Definition des Maßnahmenverantwortlichen im CAPA-Formular.
- ❌ `ERR_10_03` (critical) — übersehen: Grob fehlerhafte, verharmlosende QS-Bewertung eines kritischen Marktwaren-Stabilitätsausfalls.
