# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live`
- Zeitpunkt: 2026-06-10T07:06:41+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-4o`

## Gesamtergebnis

- **Sensitivität:** 2 von 2 versteckten Fehlern gefunden (100%)
- **Spezifität (Decoys):** 1 von 1 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 5 von 6 Findings mit verifiziertem Zitat (83%)

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 56 | 6 | 2/2 | 0/1 | blocked_due_to_model_failure |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): The QA review signature date is inconsistent with the recording date, indicating a potential data integrity issue.
- ✅ `ERR_01_02` (high) — gefunden via evidence_fuzzy (Score 0.437): The CAPA plan (CAPA-2026-441) does not document a QA review or QA approval of the CAPA plan itself. The QA release document (QA-RELEASE-XYL-004A) approves the batch for packaging but does not explicitly reference or approve CAPA-2026-441. Per req_gs_qa_approval_documented, QA approvals must be documented before closure. The absence of a QA sign-off on the CAPA plan is a compliance gap.
- ℹ️ 4 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
