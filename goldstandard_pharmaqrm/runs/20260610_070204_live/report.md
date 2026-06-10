# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live`
- Zeitpunkt: 2026-06-10T07:02:04+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-4o`

## Gesamtergebnis

- **Sensitivität:** 2 von 2 versteckten Fehlern gefunden (100%)
- **Spezifität (Decoys):** 1 von 1 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 5 von 6 Findings mit verifiziertem Zitat (83%)

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 52 | 6 | 2/2 | 0/1 | blocked_due_to_model_failure |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): The recording date of the deviation report (2026-03-12) is inconsistent with the QA review signature date (2026-12-14), which may indicate a data integrity issue.
- ✅ `ERR_01_02` (high) — gefunden via evidence_fuzzy (Score 0.447): The CAPA root cause is documented as operator error ('Bedienerfehler' – operator Max Mustermann to be retrained on reactor system operation and temperature monitoring). Per req_gs_deviation_classification, root cause attributions of 'operator error' must be substantiated. No technical investigation evidence (e.g., equipment maintenance records, calibration data, alarm logs for reactor R-02) is present to confirm that the root cause is exclusively operator-related and not equipment failure. The batch record notes 'Die Kühlung regelte unvorhergesehen herunter' (the cooling system unexpectedly reduced output), which suggests a potential equipment/system cause that has not been ruled out by documented technical investigation.
- ℹ️ 4 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
