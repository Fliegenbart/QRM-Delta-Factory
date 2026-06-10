# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live`
- Zeitpunkt: 2026-06-10T08:29:54+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-4o`

## Gesamtergebnis

- **Sensitivität:** 2 von 2 versteckten Fehlern gefunden (100%)
- **Spezifität (Decoys):** 1 von 1 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 16 von 33 Findings mit verifiziertem Zitat (48%)

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 53 | 33 | 2/2 | 0/1 | blocked_due_to_model_failure |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): The QA review signature date is inconsistent with the recording date, indicating a potential data integrity issue.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): The deviation report DEV-2026-891 lacks a root cause statement and CAPA actions, which contradicts the requirement for documented risk assessment and corrective actions.
- ℹ️ 31 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
