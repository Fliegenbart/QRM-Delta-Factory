# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-06-13T20:57:28+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 2 von 2 versteckten Fehlern gefunden (100%)
- **Spezifität (Decoys):** 1 von 1 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 11 von 14 Findings mit verifiziertem Zitat (79%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 1 | 16 | 10 | 26 |
| extraction:mistral | 1 | 3,172 | 2,148 | 5,320 |
| mistral | 7 | 126,815 | 20,048 | 146,863 |
| openai | 1 | 16,410 | 2,755 | 19,165 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_06 | needs_human_review | 21 | 14 | 2/2 | 0/1 | blocked_due_to_model_failure |

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Die Reinigungsvalidierung deckt die geänderte Materialcharge CS-AMX-9982 (Amoxicillin Trihydrat) nicht explizit ab. Es gibt keine dokumentierte Bewertung, ob die bestehende Reinigungsvalidierungsmatrix für das neue Material oder die geänderte Wassergehaltspezifikation (13,2% statt 11,5–12,8%) gültig ist.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_fuzzy (Score 0.718): Der gemessene Wassergehalt von 13,2% bei der Charge CS-AMX-9982 überschreitet die interne Spezifikation (11,5% bis 12,8%) für Amoxicillin Trihydrat. Dies stellt eine Verletzung der Akzeptanzkriterien dar, unabhängig von der Konformitätsaussage des Lieferantenzertifikats.
- ℹ️ 12 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
