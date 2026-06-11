# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-06-11T06:07:40+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 24 von 25 versteckten Fehlern gefunden (96%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 262 von 281 Findings mit verifiziertem Zitat (93%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 10 | 126,397 | 75,142 | 201,539 |
| extraction:mistral | 10 | 34,824 | 28,613 | 63,437 |
| mistral | 70 | 787,487 | 234,331 | 1,021,818 |
| openai | 10 | 106,574 | 29,291 | 135,865 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 49 | 28 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_02 | needs_human_review | 29 | 21 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_03 | completed | 19 | 32 | 2/2 | 0/2 | human_review_required |
| CASE_04 | completed | 30 | 37 | 3/3 | 0/1 | human_review_required |
| CASE_05 | needs_human_review | 21 | 25 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_06 | completed | 21 | 25 | 2/2 | 0/1 | human_review_required |
| CASE_07 | needs_human_review | 19 | 25 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_08 | needs_human_review | 31 | 23 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_09 | completed | 32 | 33 | 3/3 | 0/1 | human_review_required |
| CASE_10 | completed | 22 | 32 | 2/3 | 0/1 | human_review_required |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Data integrity issue: QA review signature date (2026-12-14) is in the future relative to deviation recording date (2026-03-12), violating ALCOA+ principles for timely and plausible electronic signatures.
- ✅ `ERR_01_02` (high) — gefunden via evidence_fuzzy (Score 0.525): QA release document (QA-RELEASE-XYL-004A) for batch XYL-2026-004A lacks explicit linkage to deviation DEV-2026-891 and its impact assessment, violating cross-document consistency requirements.
- ℹ️ 26 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): The batch yield correction for batch CPH-2026-991 lacks documented evidence of an audit trail review for the electronic record changes, violating ALCOA+ principles for data integrity. The correction was made due to an incomplete weighing slip, but no review record or justification for the change is provided.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_fuzzy (Score 0.496): Cross-document inconsistency detected between batch record (doc_37d19f84d90241e28b8b87a43929164e) and QA release document (doc_eb7c977c18174ee7ac5ac14494dc7cc6). The batch record notes a yield correction due to an incomplete weighing slip, but the QA release document does not reference this deviation or its resolution, violating req_gs_cross_document_consistency.
- ℹ️ 19 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Timestamp plausibility issue: Employee entry time (14:35) is recorded after the peak measurement time (14:15), which is chronologically inconsistent and raises data integrity concerns per ALCOA+ principles.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Deviation ID DEV-QS-2026-014 is referenced in multiple documents, but the CAPA record (CAPA-2026-014) cites an SOP (SOP-QS-REIN-001, Version 2.0) with an effective date of 2018-01-12, which predates the deviation date of 2026-04-18. This raises concerns about the applicability and consistency of referenced procedures.
- ℹ️ 30 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Cross-document inconsistency detected between the deviation record and batch impact assessment for batch PAR-2026-H102. The deviation record states a temperature excursion of 44.5°C for 3 minutes, while the impact assessment claims no substance degradation. No lab data or stability data is provided to support the impact assessment, violating req_gs_deviation_classification.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Root cause for deviation DEV-P-2026-092 is documented as 'stuck valve in air heater register,' but the CAPA record attributes the root cause to 'lack of attention by operator during temperature monitoring.' This inconsistency violates req_gs_cross_document_consistency and may impact the effectiveness of CAPA actions.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Batch impact assessment for deviation DEV-P-2026-092 lacks explicit disposition rationale for batch PAR-2026-H102, violating requirement req_gs_batch_impact_completeness. The batch is claimed to be quality compliant and released, but the evidence does not clearly link the disposition decision to the impact assessment or batch records.
- ℹ️ 34 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): The executed sterilization cycle on AT-442 references program 121°C/20 min, while the validation note states that exact loading patterns and maximum allowable total weights for glassware are specified in Annex 4. Because no claim provides the actual load pattern, weight, or Annex 4 conformity for this cycle, the supplied validation evidence does not fully demonstrate coverage of the current executed process state.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Operator P.M. (PNN-8812) is recorded as completing autoclave loading at 08:15, but the same operator (PNN-8812, initials A.S.) is documented entering the sterile preparation room at 08:45. This creates a contradiction in operator presence and timeline plausibility, raising concerns about data integrity and audit trail reliability.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Operator P.M. (PNN-8812) is recorded as completing autoclave loading at 08:15, but the same operator (PNN-8812, initials A.S.) is documented entering the sterile preparation room at 08:45. This creates a contradiction in operator presence and timeline plausibility, raising concerns about data integrity and audit trail reliability.
- ℹ️ 23 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Widerspruch im Wassergehalt von Amoxicillin Trihydrat (Chargennummer CS-AMX-9982): Das Analysenzertifikat des Lieferanten gibt 13,2% Wassergehalt an, was außerhalb der internen Spezifikation von 11,5% bis 12,8% liegt. Die QA-Freigabe der Formulierungscharge AMO-SUP-2026-01 erfolgte trotz dieser Abweichung ohne dokumentierte Risikobewertung oder Impact Assessment.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_fuzzy (Score 0.718): Cross-document inconsistency detected: The water content result for raw material CS-AMX-9982 is reported as 13.2% in the deviation record, but no corresponding update or reference is found in the QA release document for batch AMO-SUP-2026-01.
- ℹ️ 23 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): The batch (MET-2026-C09) recorded a net yield of 92.4%, which is below the specified tolerance range of 95.0% to 102.0%. This deviation from the yield specification may indicate a potential impact on product quality, but there is no documented evidence of a thorough impact assessment or QA disposition decision.
- ✅ `ERR_07_02` (medium) — gefunden via evidence_fuzzy (Score 0.437): Fuer CAPA-MET-2026-09 existiert kein Claim, der einen definierten oder dokumentierten Effectiveness Check (Wirksamkeitspruefung) belegt. Gemaess req_gs_capa_effectiveness duerfen CAPA-Massnahmen nur mit dokumentierter Wirksamkeitspruefung abgeschlossen werden. Das Fehlen dieses Nachweises stellt einen Pflichtnachweis-Mangel dar.
- ℹ️ 23 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): The deviation DEV-IBU-2026-112 involves a mechanical failure (hairline crack on upper punch station 12) during tablet compression, but there is no documented validation or bridging study to confirm the impact of the tool replacement on product quality or process validation. The claim of 'isolated single event' lacks supporting validation evidence.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): The deviation record claims 'no influence on other batches or steps,' but there is no documented batch impact assessment or list of potentially affected batches to support this claim. This violates the requirement for a complete batch impact assessment.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): The CAPA record (CAPA-112-IBU) outlines actions to install an inline metal detector and prioritize procurement, but there is no documented effectiveness check to confirm the resolution of the root cause (tool breakage). This violates the requirement for mandatory effectiveness checks before CAPA closure.
- ℹ️ 20 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Contradiction in deviation impact assessment: The pH value drifted outside the specified upper limit (7.40) for 6 hours, reaching a peak of 7.85, but the batch impact assessment claims 'processing_continued' with 'no special incidents' and 'stable values'. This contradicts the requirement for a documented impact assessment on product quality and patient safety (req_gs_deviation_impact, req_gs_spec_limits).
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Contradiction in root cause analysis: The deviation report states the root cause for the pH drift is 'unresolved', but the change control CC-2026-104 implies a preventive sensor replacement, suggesting a known issue. This contradicts the requirement for a documented and justified root cause (req_gs_deviation_classification).
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Missing QA approval for change control CC-2026-104: The QC head signature field is empty, and the QA approval status is unclear. This contradicts the requirement for documented QA approval before closure (req_gs_qa_approval_documented). The change control involves a pH sensor replacement, which is directly related to the deviation DEV-CEF-77.
- ℹ️ 30 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): CAPA plan CAPA-OOS-INS lacks a defined responsible party and does not provide sufficient evidence of a documented effectiveness check, violating req_gs_capa_effectiveness.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Batch impact assessment for INS-GLA-2025-05 is partially documented. While provisional compliance is noted, the lack of explicit linkage to all affected batches and disposition decisions violates req_gs_batch_impact_completeness.
- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- ℹ️ 30 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
