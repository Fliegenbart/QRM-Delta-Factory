# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-06-10T20:34:14+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 2 von 2 versteckten Fehlern gefunden (100%)
- **Spezifität (Decoys):** 1 von 1 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 24 von 27 Findings mit verifiziertem Zitat (89%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 1 | 10,369 | 7,768 | 18,137 |
| extraction:mistral | 1 | 3,217 | 1,995 | 5,212 |
| mistral | 7 | 56,057 | 23,517 | 79,574 |
| openai | 1 | 8,697 | 3,329 | 12,026 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_07 | needs_human_review | 17 | 27 | 2/2 | 0/1 | blocked_due_to_model_failure |

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): The deviation DEV-MET-09 involved a clogged spray nozzle during the coating process, which was restored after mechanical cleaning. However, there is no documented evidence that the existing validation covers the impact of this deviation on the uniformity of the coating process or the final product quality. The yield for batch MET-2026-C09 (92.4%) fell below the specified tolerance range (95.0% to 102.0%), indicating a potential validation gap.
- ✅ `ERR_07_02` (medium) — gefunden via evidence_fuzzy (Score 0.449): Im CAPA-Dokument CAPA-MET-2026-09 ist kein Effectiveness-Check-Nachweis dokumentiert. Gemäß req_gs_capa_effectiveness dürfen CAPA-Maßnahmen nur mit definierter und dokumentierter Wirksamkeitsprüfung abgeschlossen werden. Es existiert kein Claim, der einen Effectiveness Check für diese CAPA belegt.
- ℹ️ 25 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
