# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live`
- Zeitpunkt: 2026-06-10T07:12:56+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-4o`

## Gesamtergebnis

- **Sensitivität:** 15 von 25 versteckten Fehlern gefunden (60%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 38 von 44 Findings mit verifiziertem Zitat (86%)

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 55 | 6 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_02 | needs_human_review | 35 | 6 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_03 | needs_human_review | 24 | 3 | 1/2 | 0/2 | blocked_due_to_model_failure |
| CASE_04 | needs_human_review | 39 | 2 | 1/3 | 0/1 | out_of_scope |
| CASE_05 | needs_human_review | 15 | 4 | 2/3 | 0/1 | blocked_due_to_model_failure |
| CASE_06 | needs_human_review | 16 | 11 | 1/2 | 0/1 | blocked_due_to_model_failure |
| CASE_07 | needs_human_review | 26 | 2 | 1/2 | 0/1 | blocked_due_to_model_failure |
| CASE_08 | needs_human_review | 24 | 2 | 2/3 | 0/1 | blocked_due_to_model_failure |
| CASE_09 | needs_human_review | 21 | 5 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_10 | needs_human_review | 29 | 3 | 0/3 | 0/1 | blocked_due_to_model_failure |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): The QA review signature for deviation DEV-2026-891 (Dr. Anna Klar, QA) is dated 14.12.2026, which is approximately nine months after the deviation recording date of 12.03.2026 and after the QA release document date of 25.03.2026. The batch XYL-2026-004A was already released for packaging on 25.03.2026 (QA-RELEASE-XYL-004A), yet the QA review signature on the deviation report is dated 14.12.2026. This temporal inconsistency constitutes a data integrity finding under req_gs_data_integrity_signatures (ALCOA+: contemporaneous, plausible, consistent with audit trail). A QA review completed after batch release is not plausible as a pre-release control.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): There is a contradiction between the deviation classification as 'minor' and the requirement for a justified risk assessment with physical-chemical data.
- ℹ️ 4 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): No CAPA record, CAPA ID, CAPA actions, responsible party, due date, or effectiveness check is present anywhere in the document set. A yield correction was made in the batch record (96.47% crossed out and corrected to 98.1%) citing an incomplete weighing slip (Wiegebegleitschein), and the batch was released. This constitutes a documented deviation-triggering event with no associated CAPA process, no deviation classification, no root cause analysis, and no effectiveness check, in direct violation of req_gs_capa_effectiveness, req_gs_deviation_classification, and req_gs_deviation_impact.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_substring (Score 1.0): Adversarial review found required evidence missing or not clearly present in the claim ledger.
- ℹ️ 4 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): The timestamp of the particle peak at 14:15 is inconsistent with the employee entry at 14:35, suggesting a potential data integrity issue.
- ❌ `ERR_03_02` (medium) — übersehen: Referenzierung einer veralteten, potenziell ungültigen SOP-Version im CAPA-Plan.
- ℹ️ 2 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): There is a contradiction between the documented maximum temperature of 44.5°C and the specified maximum limit of 42.0°C for product temperature, which is not addressed in the deviation report.
- ❌ `ERR_04_02` (high) — übersehen: Fehlende Verknüpfung zwischen technischer Root Cause und personeller CAPA-Maßnahme.
- ❌ `ERR_04_03` (critical) — übersehen: Kritische Chargenfreigabe beruhend auf fehlerhafter und unvollständiger Abweichungsbewertung.
- ℹ️ 1 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): The sterilization cycle ZYK-STER-992 was performed with program start at 08:20 and sterile goods removal at 09:00. The cleanroom security report states that employee PNN-8812 entered the personnel airlock to the preparation room (R-102) at 08:45 and had no prior presence in the autoclave area before 08:45. This means the attributed operator was physically absent from the autoclave area during the loading phase (loading completed 08:15) and the program start (08:20), raising a critical question about who actually loaded and started the autoclave, and whether the attribution of cycle ZYK-STER-992 to PNN-8812 is valid. This is a direct ALCOA+ contemporaneity and attributability failure.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Personnel number PNN-8812 is attributed to operator 'P.M.' in the sterilization cycle record (ZYK-STER-992), but the same personnel number PNN-8812 is registered in the electronic access control system under initials 'A.S.' This direct contradiction between the batch record attribution and the system-stored identity constitutes a critical data integrity finding: either the operator identity in the batch record is incorrect, or the system record has been manipulated. ALCOA+ attributability cannot be confirmed.
- ❌ `ERR_05_01` (medium) — übersehen: Verweis auf ein nicht vorhandenes bzw. fehlendes Dokumentenelement (Anhang 4).
- ℹ️ 2 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Batch CS-AMX-9982 (Amoxicillin Trihydrat) has a measured water content of 13.2%, which exceeds the upper acceptance limit of 12.8% defined in Prüf-Spez-API-04. The deviation LAB-DEV-2026-031 is still open/under investigation. No disposition decision, no risk classification (Minor/Major/Critical), and no QA approval are documented. Release by ChemieSynthese QC does not substitute for an internal GMP-compliant disposition decision under the applicable specification.
- ❌ `ERR_06_02` (critical) — übersehen: Wirkstofffreigabe durch QA trotz ungelöster und aktive Laborabweichung.
- ℹ️ 10 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.475): The batch status is marked as 'Pass' despite the real net yield being below the specified acceptance criterion, indicating a potential contradiction in QA approval.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 1 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): There is a contradiction between the claim that the deviation is an isolated single event with no systematic character and the claim that there is no impact on other batches or preceding production steps.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.697): There is a contradiction between the claim that the deviation is an isolated single event with no systematic character and the claim that there is no impact on other batches or preceding production steps.
- ❌ `ERR_08_03` (medium) — übersehen: Unrealistisches, nicht plausibles CAPA-Zieldatum ohne adäquate Projektrealisierungszeit.
- ℹ️ 1 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Adversarial review found required evidence missing or not clearly present in the claim ledger.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): The pH value in bioreactor BIO-10 exceeded the specified upper limit of pH 7.40, reaching a peak value of pH 7.85, which is a deviation from critical process parameters. However, the root cause of the pH drift could not be determined, and the deviation report lacks a documented risk assessment with a justified classification.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Change Control CC-2026-104 proposes replacement of the pH sensor at BIO-10 as a preventive measure, but is classified as 'non-reactive/preventive' despite being directly linked to the unresolved pH drift deviation DEV-CEF-77. The change is deferred to September 2026 major maintenance, meaning the old analog sensors remain in use until then. No CAPA effectiveness check or interim control measure is documented to mitigate recurrence risk during the interim period. The Leitung QK signature field is empty/unsigned, meaning the change control lacks complete approval.
- ℹ️ 2 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- ❌ `ERR_10_02` (high) — übersehen: Fehlende Definition des Maßnahmenverantwortlichen im CAPA-Formular.
- ❌ `ERR_10_03` (critical) — übersehen: Grob fehlerhafte, verharmlosende QS-Bewertung eines kritischen Marktwaren-Stabilitätsausfalls.
- ℹ️ 3 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
