# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live`
- Zeitpunkt: 2026-06-10T07:09:30+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-4o`

## Gesamtergebnis

- **Sensitivität:** 0 von 7 versteckten Fehlern gefunden (0%)
- **Spezifität (Decoys):** 4 von 4 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 0 von 0 Findings mit verifiziertem Zitat

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_02 | failed | 0 | 0 | 0/2 | 0/1 | - |
| CASE_03 | failed | 0 | 0 | 0/2 | 0/2 | - |
| CASE_04 | failed | 0 | 0 | 0/3 | 0/1 | - |

### CASE_02

- ❌ `ERR_02_01` (high) — übersehen: Undokumentierte und nicht gegengezeichnete manuelle Datenkorrektur im Ausbeuteprotokoll.
- ❌ `ERR_02_02` (medium) — übersehen: Yield außerhalb der Toleranzgrenze ohne Einleitung einer OOS/Abweichungsuntersuchung.

### CASE_03

- ❌ `ERR_03_01` (high) — übersehen: Anachronistische Zeitstempel zwischen Raum-Logbuch und Probenahme-Protokoll.
- ❌ `ERR_03_02` (medium) — übersehen: Referenzierung einer veralteten, potenziell ungültigen SOP-Version im CAPA-Plan.

### CASE_04

- ❌ `ERR_04_01` (high) — übersehen: Diskrepanz des maximalen Temperaturwerts zwischen Abweichungsbericht und Herstellprotokoll.
- ❌ `ERR_04_02` (high) — übersehen: Fehlende Verknüpfung zwischen technischer Root Cause und personeller CAPA-Maßnahme.
- ❌ `ERR_04_03` (critical) — übersehen: Kritische Chargenfreigabe beruhend auf fehlerhafter und unvollständiger Abweichungsbewertung.
