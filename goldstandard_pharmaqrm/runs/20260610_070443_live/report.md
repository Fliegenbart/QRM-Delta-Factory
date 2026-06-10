# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live`
- Zeitpunkt: 2026-06-10T07:04:43+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-4o`

## Gesamtergebnis

- **Sensitivität:** 0 von 25 versteckten Fehlern gefunden (0%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 0 von 0 Findings mit verifiziertem Zitat

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | failed | 0 | 0 | 0/2 | 0/1 | - |
| CASE_02 | failed | 0 | 0 | 0/2 | 0/1 | - |
| CASE_03 | failed | 0 | 0 | 0/2 | 0/2 | - |
| CASE_04 | failed | 0 | 0 | 0/3 | 0/1 | - |
| CASE_05 | failed | 0 | 0 | 0/3 | 0/1 | - |
| CASE_06 | failed | 0 | 0 | 0/2 | 0/1 | - |
| CASE_07 | failed | 0 | 0 | 0/2 | 0/1 | - |
| CASE_08 | failed | 0 | 0 | 0/3 | 0/1 | - |
| CASE_09 | failed | 0 | 0 | 0/3 | 0/1 | - |
| CASE_10 | failed | 0 | 0 | 0/3 | 0/1 | - |

### CASE_01

- ❌ `ERR_01_01` (medium) — übersehen: Ungültiges, in der Zukunft liegendes Signaturdatum der QS-Prüfung.
- ❌ `ERR_01_02` (high) — übersehen: Fehlklassifizierung einer kritischen Prozessparameter-Abweichung.

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

### CASE_05

- ❌ `ERR_05_01` (medium) — übersehen: Verweis auf ein nicht vorhandenes bzw. fehlendes Dokumentenelement (Anhang 4).
- ❌ `ERR_05_02` (high) — übersehen: Kritischer Zeitkonflikt zwischen manuellem Prozess-Logbuch und automatisiertem Zutrittskontrollsystem.
- ❌ `ERR_05_03` (medium) — übersehen: Mangelnde Zuordnungsgenauigkeit von Unterschrift/Initialen zur Personalnummer.

### CASE_06

- ❌ `ERR_06_01` (high) — übersehen: Akzeptanzkriterium der internen Spezifikation wird durch das Lieferanten-Zertifikat verletzt.
- ❌ `ERR_06_02` (critical) — übersehen: Wirkstofffreigabe durch QA trotz ungelöster und aktive Laborabweichung.

### CASE_07

- ❌ `ERR_07_01` (high) — übersehen: Yield-Unterschreitung wird fälschlicherweise als konform deklariert.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.

### CASE_08

- ❌ `ERR_08_01` (critical) — übersehen: Unerkannter bzw. bewusst ignorierter Wiederholungsfehler (Trend-Fehler) bei Stempelbeschädigungen.
- ❌ `ERR_08_02` (high) — übersehen: Mangelhafte Ausdehnung des Batch-Impact-Assessments auf potenziell mitbetroffene Vorgängerchargen.
- ❌ `ERR_08_03` (medium) — übersehen: Unrealistisches, nicht plausibles CAPA-Zieldatum ohne adäquate Projektrealisierungszeit.

### CASE_09

- ❌ `ERR_09_01` (critical) — übersehen: Intentionale Falschdokumentation im Batch Record im Widerspruch zum SCADA-Audit-Trail.
- ❌ `ERR_09_02` (high) — übersehen: Fehlerhafte Root-Cause-Ermittlung durch Ignorieren der System-Logfiles.
- ❌ `ERR_09_03` (medium) — übersehen: Unvollständig genehmigtes Change-Control-Dokument ohne finale QK-Freigabe.

### CASE_10

- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- ❌ `ERR_10_02` (high) — übersehen: Fehlende Definition des Maßnahmenverantwortlichen im CAPA-Formular.
- ❌ `ERR_10_03` (critical) — übersehen: Grob fehlerhafte, verharmlosende QS-Bewertung eines kritischen Marktwaren-Stabilitätsausfalls.
