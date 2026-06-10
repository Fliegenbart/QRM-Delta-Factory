# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `mock`
- Zeitpunkt: 2026-06-10T06:59:44+00:00
- Anthropic-Modell: `None`
- OpenAI-Modell: `None`

## Gesamtergebnis

- **Sensitivität:** 3 von 25 versteckten Fehlern gefunden (12%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 28 von 28 Findings mit verifiziertem Zitat (100%)

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | completed | 7 | 4 | 0/2 | 0/1 | human_review_required |
| CASE_02 | completed | 1 | 2 | 1/2 | 0/1 | human_review_required |
| CASE_03 | completed | 4 | 4 | 0/2 | 0/2 | human_review_required |
| CASE_04 | completed | 5 | 4 | 1/3 | 0/1 | human_review_required |
| CASE_05 | completed | 0 | 0 | 0/3 | 0/1 | human_review_required |
| CASE_06 | completed | 1 | 2 | 0/2 | 0/1 | human_review_required |
| CASE_07 | completed | 3 | 3 | 0/2 | 0/1 | human_review_required |
| CASE_08 | completed | 9 | 4 | 0/3 | 0/1 | human_review_required |
| CASE_09 | completed | 1 | 2 | 1/3 | 0/1 | human_review_required |
| CASE_10 | completed | 2 | 3 | 0/3 | 0/1 | human_review_required |

### CASE_01

- ❌ `ERR_01_01` (medium) — übersehen: Ungültiges, in der Zukunft liegendes Signaturdatum der QS-Prüfung.
- ❌ `ERR_01_02` (high) — übersehen: Fehlklassifizierung einer kritischen Prozessparameter-Abweichung.
- ℹ️ 4 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_02` (medium) — gefunden via evidence_substring (Score 1.0): Adversarial review found required evidence missing or not clearly present in the claim ledger.
- ❌ `ERR_02_01` (high) — übersehen: Undokumentierte und nicht gegengezeichnete manuelle Datenkorrektur im Ausbeuteprotokoll.
- ℹ️ 1 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ❌ `ERR_03_01` (high) — übersehen: Anachronistische Zeitstempel zwischen Raum-Logbuch und Probenahme-Protokoll.
- ❌ `ERR_03_02` (medium) — übersehen: Referenzierung einer veralteten, potenziell ungültigen SOP-Version im CAPA-Plan.
- ℹ️ 4 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): CAPA reference requires effectiveness evidence if linked to quality risk.
- ❌ `ERR_04_01` (high) — übersehen: Diskrepanz des maximalen Temperaturwerts zwischen Abweichungsbericht und Herstellprotokoll.
- ❌ `ERR_04_03` (critical) — übersehen: Kritische Chargenfreigabe beruhend auf fehlerhafter und unvollständiger Abweichungsbewertung.
- ℹ️ 3 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ❌ `ERR_05_01` (medium) — übersehen: Verweis auf ein nicht vorhandenes bzw. fehlendes Dokumentenelement (Anhang 4).
- ❌ `ERR_05_02` (high) — übersehen: Kritischer Zeitkonflikt zwischen manuellem Prozess-Logbuch und automatisiertem Zutrittskontrollsystem.
- ❌ `ERR_05_03` (medium) — übersehen: Mangelnde Zuordnungsgenauigkeit von Unterschrift/Initialen zur Personalnummer.

### CASE_06

- ❌ `ERR_06_01` (high) — übersehen: Akzeptanzkriterium der internen Spezifikation wird durch das Lieferanten-Zertifikat verletzt.
- ❌ `ERR_06_02` (critical) — übersehen: Wirkstofffreigabe durch QA trotz ungelöster und aktive Laborabweichung.
- ℹ️ 2 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ❌ `ERR_07_01` (high) — übersehen: Yield-Unterschreitung wird fälschlicherweise als konform deklariert.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 3 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ❌ `ERR_08_01` (critical) — übersehen: Unerkannter bzw. bewusst ignorierter Wiederholungsfehler (Trend-Fehler) bei Stempelbeschädigungen.
- ❌ `ERR_08_02` (high) — übersehen: Mangelhafte Ausdehnung des Batch-Impact-Assessments auf potenziell mitbetroffene Vorgängerchargen.
- ❌ `ERR_08_03` (medium) — übersehen: Unrealistisches, nicht plausibles CAPA-Zieldatum ohne adäquate Projektrealisierungszeit.
- ℹ️ 4 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Adversarial review found required evidence missing or not clearly present in the claim ledger.
- ❌ `ERR_09_02` (high) — übersehen: Fehlerhafte Root-Cause-Ermittlung durch Ignorieren der System-Logfiles.
- ❌ `ERR_09_03` (medium) — übersehen: Unvollständig genehmigtes Change-Control-Dokument ohne finale QK-Freigabe.
- ℹ️ 1 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- ❌ `ERR_10_02` (high) — übersehen: Fehlende Definition des Maßnahmenverantwortlichen im CAPA-Formular.
- ❌ `ERR_10_03` (critical) — übersehen: Grob fehlerhafte, verharmlosende QS-Bewertung eines kritischen Marktwaren-Stabilitätsausfalls.
- ℹ️ 3 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
