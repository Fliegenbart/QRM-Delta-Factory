# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hetzner` | Engine: `requirement`
- Zeitpunkt: 2026-08-22T19:11:33+00:00
- Anthropic-Modell: `-`
- OpenAI-Modell: `-`
- Hetzner-Modell: `Qwen3.8-27B`

## Gesamtergebnis

- **Sensitivität:** 8 von 25 versteckten Fehlern gefunden (32%)
- **In Prüfmappe sichtbar:** 7 von 25 versteckten Fehlern (28%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 10 von 208 (5%) — 7 als Treffer gewertet, 3 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 198 von 208 (95%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 20.8 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 45 von 208 Findings mit verifiziertem Zitat (22%)

## Qualitätsmetriken

- Must-detect Recall: `0.32`
- Wiederholungen: `3` (Redundanzrate `0.3`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `5/3/0`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| hetzner | 178 | 687,947 | 100,638 | 788,585 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 22 | 0 | 22 | 0/2 | 0/2 | 0/1 | - |
| CASE_02 | completed | 0 | 21 | 0 | 21 | 0/2 | 0/2 | 0/1 | - |
| CASE_03 | completed | 0 | 21 | 0 | 20 | 1/2 | 1/2 | 0/2 | - |
| CASE_04 | completed_with_model_failures | 0 | 20 | 2 | 16 | 2/3 | 2/3 | 0/1 | - |
| CASE_05 | completed | 0 | 18 | 0 | 18 | 0/3 | 0/3 | 0/1 | - |
| CASE_06 | completed | 0 | 19 | 1 | 17 | 1/2 | 1/2 | 0/1 | - |
| CASE_07 | completed_with_model_failures | 0 | 22 | 0 | 22 | 0/2 | 0/2 | 0/1 | - |
| CASE_08 | completed | 0 | 21 | 0 | 20 | 2/3 | 1/3 | 0/1 | - |
| CASE_09 | completed | 0 | 23 | 0 | 23 | 0/3 | 0/3 | 0/1 | - |
| CASE_10 | completed | 0 | 21 | 0 | 19 | 2/3 | 2/3 | 0/1 | - |

## Modellausfälle

- **ProviderCallError** (1×): hetzner provider call failed with HTTP 504
  - betroffen: CASE_04/challenge:12
- **ProviderCallError** (1×): hetzner provider returned invalid JSON
  - betroffen: CASE_07/extract[doc_2c20abccb5e644e98c63d5c485045f50:werte]:15

### CASE_01

- ❌ `ERR_01_01` (medium) — übersehen: Ungültiges, in der Zukunft liegendes Signaturdatum der QS-Prüfung.
- ❌ `ERR_01_02` (high) — übersehen: Fehlklassifizierung einer kritischen Prozessparameter-Abweichung.
- ℹ️ 22 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ❌ `ERR_02_01` (high) — übersehen: Undokumentierte und nicht gegengezeichnete manuelle Datenkorrektur im Ausbeuteprotokoll.
- ❌ `ERR_02_02` (medium) — übersehen: Yield außerhalb der Toleranzgrenze ohne Einleitung einer OOS/Abweichungsuntersuchung.
- ℹ️ 21 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_fuzzy (Score 0.449): Es gibt einen zeitlichen Widerspruch in den Dokumenten. Im Deviation Report wird angegeben: 'Eintritt des Mitarbeiters in Raum R-202 laut elektronischem Logbuch: 14:35 Uhr' und 'Probenahme / Peak-Zeitstempel: 14:15 Uhr'. Der Peak wurde also 20 Minuten vor dem dokumentierten Eintritt des Mitarbeiters gemessen. Diese Inkonsistenz muss aufgeklärt werden, da sie die Plausibilität der Daten in Frage stellt.
- ❌ `ERR_03_02` (medium) — übersehen: Referenzierung einer veralteten, potenziell ungültigen SOP-Version im CAPA-Plan.
- ℹ️ 20 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass CAPA-Maßnahmen, die mit einem Qualitätsrisiko verknüpft sind, nur mit einer definierten und dokumentierten Wirksamkeitsprüfung (Effectiveness Check) abgeschlossen werden dürfen. Der vorliegende CAPA-Plan definiert die Maßnahme (Re-Training) und den Termin, enthält aber keinerlei Beschreibung, wie die Wirksamkeit dieser Maßnahme überprüft werden soll (z. B. Prüfung der nächsten Chargen auf Temperaturabweichungen, Audit des Bedienverhaltens, etc.). Da die Abweichung ein Qualitätsrisiko darstellt (Temperaturüberschreitung bei Paracetamol), ist die fehlende Definition der Wirksamkeitsprüfung ein Verstoß gegen die Anforderung, dass diese dokumentiert sein muss, bevor die CAPA als abgeschlossen gilt oder auch nur geplant wird.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass die Dispositionsentscheidung begründet und mit den Batch Records verknüpft ist. Die Freigabeanmerkung (document_04) begründet die Entscheidung ('kein nennenswerter Substanzabbau erwartet') und verweist explizit auf die Abweichung DEV-P-2026-092. Die Charge PAR-2026-H102 ist sowohl in der Freigabeanmerkung als auch im Batch Record (document_02) eindeutig identifiziert. Die Verknüpfung ist somit hergestellt und die Begründung ist vorhanden. Obwohl die Tiefe der Begründung in einem anderen Verdict als unzureichend für das Impact Assessment kritisiert wurde, ist die formale Verknüpfung und Begründung der Disposition im Sinne dieser spezifischen Anforderung (Nachvollziehbarkeit) erfüllt.
- ❌ `ERR_04_01` (high) — übersehen: Diskrepanz des maximalen Temperaturwerts zwischen Abweichungsbericht und Herstellprotokoll.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 16 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ❌ `ERR_05_01` (medium) — übersehen: Verweis auf ein nicht vorhandenes bzw. fehlendes Dokumentenelement (Anhang 4).
- ❌ `ERR_05_02` (high) — übersehen: Kritischer Zeitkonflikt zwischen manuellem Prozess-Logbuch und automatisiertem Zutrittskontrollsystem.
- ❌ `ERR_05_03` (medium) — übersehen: Mangelnde Zuordnungsgenauigkeit von Unterschrift/Initialen zur Personalnummer.
- ℹ️ 18 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_fuzzy (Score 0.679): Die Unterlagen belegen den Auslöser der Anforderung: Eine Abweichung (LAB-DEV-2026-031) wurde eröffnet, da der Wassergehalt (13,2%) außerhalb der internen Spezifikation (11,5% - 12,8%) liegt. Die Anforderung verlangt jedoch eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit sowie eine Auflistung aller potenziell betroffenen Chargen. Im vorliegenden Laborabweichungsbericht wird lediglich der Status 'In Untersuchung' angegeben, es fehlen jedoch die geforderten Impact Assessment-Dokumente, die Risikobewertung und die Chargenliste. Da der Auslöser (die Abweichung) belegt ist, der Nachweis der Bewertung aber fehlt, liegt ein Verstoß vor.
- ❌ `ERR_06_02` (critical) — übersehen: Wirkstofffreigabe durch QA trotz ungelöster und aktive Laborabweichung.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 17 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ❌ `ERR_07_01` (high) — übersehen: Yield-Unterschreitung wird fälschlicherweise als konform deklariert.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 22 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht behauptet, dass es sich um ein isoliertes Ereignis handelt und der Einfluss auf andere Chargen ausgeschlossen ist. Es fehlt jedoch eine vollständige Erfassung potenziell betroffener Chargen (z. B. eine Liste von Vorgänger- oder Folgechargen, die geprüft wurden). Die bloße Behauptung des Ausschlusses ohne Beleg der Prüfung aller relevanten Chargen erfüllt die Anforderung an eine vollständige Erfassung nicht.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.458): Der Abweichungsbericht behauptet, dass es sich um ein isoliertes Ereignis handelt und der Einfluss auf andere Chargen ausgeschlossen ist. Es fehlt jedoch eine vollständige Erfassung potenziell betroffener Chargen (z. B. eine Liste von Vorgänger- oder Folgechargen, die geprüft wurden). Die bloße Behauptung des Ausschlusses ohne Beleg der Prüfung aller relevanten Chargen erfüllt die Anforderung an eine vollständige Erfassung nicht.
- ❌ `ERR_08_03` (medium) — übersehen: Unrealistisches, nicht plausibles CAPA-Zieldatum ohne adäquate Projektrealisierungszeit.
- ℹ️ 20 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ❌ `ERR_09_01` (critical) — übersehen: Intentionale Falschdokumentation im Batch Record im Widerspruch zum SCADA-Audit-Trail.
- ❌ `ERR_09_02` (high) — übersehen: Fehlerhafte Root-Cause-Ermittlung durch Ignorieren der System-Logfiles.
- ❌ `ERR_09_03` (medium) — übersehen: Unvollständig genehmigtes Change-Control-Dokument ohne finale QK-Freigabe.
- ℹ️ 23 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan weist im Feld 'Verantwortlich' explizit '[Kein Eintrag / Offen]' aus. Die Anforderung verlangt einen benannten Maßnahmenverantwortlichen. Da dieses Pflichtfeld leer ist, liegt ein Verstoß vor.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge INS-GLA-2025-05 wurde bereits im Juni 2025 in den Handel überführt (Freigabe/Disposition erfolgt). Der Stabilitätsbericht vom 15.05.2026 dokumentiert jedoch einen OOS-Befund (Verunreinigung 0,32% > 0,20%). Der QA-Vermerk vom 19.05.2026 stellt fest, dass 'Sämtliche Analytikvorgaben werden als vorläufig erfüllt betrachtet', obwohl die Abweichungsbewertung und das Re-Testing noch nicht abgeschlossen sind ('bis zum finalen Abschluss des Labor-Re-Testings'). Die Freigabe der Charge erfolgte, bevor die aktuelle Abweichungsbewertung abgeschlossen war. Dies verstößt gegen die Regel, dass keine Freigabe vor abgeschlossener Bewertung erfolgen darf, insbesondere da die aktuelle Stabilitätsprüfung einen OOS-Wert ergab, der die Konformität in Frage stellt.
- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- ℹ️ 19 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
