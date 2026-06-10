# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `mock` | Stack: `-`
- Zeitpunkt: 2026-06-10T13:39:09+00:00
- Anthropic-Modell: `-`
- OpenAI-Modell: `-`
- Mistral-Modell: `-`

## Gesamtergebnis

- **Sensitivität:** 0 von 2 versteckten Fehlern gefunden (0%)
- **Spezifität (Decoys):** 1 von 1 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 4 von 4 Findings mit verifiziertem Zitat (100%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| mock | 7 | 112 | 146 | 258 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | completed | 7 | 4 | 0/2 | 0/1 | human_review_required |

### CASE_01

- ❌ `ERR_01_01` (medium) — übersehen: Ungültiges, in der Zukunft liegendes Signaturdatum der QS-Prüfung.
- ❌ `ERR_01_02` (high) — übersehen: Fehlklassifizierung einer kritischen Prozessparameter-Abweichung.
- ℹ️ 4 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
