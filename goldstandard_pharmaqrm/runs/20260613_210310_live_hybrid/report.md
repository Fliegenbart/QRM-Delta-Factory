# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-06-13T21:03:10+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 2 von 2 versteckten Fehlern gefunden (100%)
- **Spezifität (Decoys):** 1 von 1 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 17 von 17 Findings mit verifiziertem Zitat (100%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 1 | 19,465 | 9,404 | 28,869 |
| extraction:mistral | 1 | 3,157 | 2,124 | 5,281 |
| mistral | 7 | 126,850 | 21,698 | 148,548 |
| openai | 1 | 16,428 | 3,140 | 19,568 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_06 | completed | 21 | 17 | 2/2 | 0/1 | human_review_required |

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Das QA-Freigabedokument QA-REL-AMO-01 beruft sich auf das Lieferanten-Analysenzertifikat als Konformitätsbeleg, während das Abweichungsdokument LAB-DEV-2026-031 eine interne OOS-Feststellung (13,2% Wassergehalt) dokumentiert. Dieser Widerspruch zwischen den Dokumenten ist nicht aufgeklärt: Es ist unklar, welchen Wassergehalt das Lieferantenzertifikat ausweist und warum die interne Messung davon abweicht. Die Freigabe auf Basis des Lieferantenzertifikats ohne Auflösung dieses Widerspruchs ist GMP-konform nicht zulässig.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_fuzzy (Score 0.718): Der Wassergehalt der Charge CS-AMX-9982 (13,2%) liegt außerhalb der internen Spezifikation (11,5% bis 12,8%), obwohl das Analysenzertifikat des Lieferanten Konformität bestätigt. Die interne Spezifikation wurde nicht eingehalten, und es fehlt eine dokumentierte Bewertung der Abweichung gemäß interner Akzeptanzkriterien.
- ℹ️ 15 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
