# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-06-13T11:43:02+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 3 von 3 versteckten Fehlern gefunden (100%)
- **Spezifität (Decoys):** 1 von 1 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 27 von 27 Findings mit verifiziertem Zitat (100%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 1 | 10,899 | 6,439 | 17,338 |
| extraction:mistral | 1 | 3,352 | 2,284 | 5,636 |
| mistral | 7 | 69,766 | 26,705 | 96,471 |
| openai | 1 | 9,118 | 3,463 | 12,581 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_10 | completed | 19 | 27 | 3/3 | 0/1 | human_review_required |

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Abweichung der unbekannten Verunreinigung (0,32% bei Spezifikationsgrenze von maximal 0,20%) wurde als 'temporärer Ausreißer' bewertet, ohne dass eine vollständige Risikoeinstufung (Minor/Major/Kritisch) gemäß SOP-DEV-001 Abschnitt 6.2 dokumentiert ist. Eine Einstufung ohne belastbare physikalisch-chemische Daten oder Root-Cause-Analyse ist nicht zulässig.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme 'CAPA-OOS-INS' enthält keine dokumentierte Wirksamkeitsprüfung (Effectiveness Check) gemäß SOP-CAPA-003 Abschnitt 7.5. Das Zieldatum der Umsetzung (16.05.2026) liegt in der Zukunft, und die Verantwortlichkeit ist nicht spezifiziert.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Batch-Impact-Bewertung der Charge INS-GLA-2025-05 enthält Aussagen zur vorläufigen Erfüllung aller Analytikvorgaben und zur fehlenden Notwendigkeit marktregulierender Maßnahmen, ohne dass eine dokumentierte QA-Freigabe gemäß SOP-QA-004 Abschnitt 5.1 vorliegt. Die Freigabeentscheidung ist nicht mit den Batch Records verknüpft.
- ℹ️ 24 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
