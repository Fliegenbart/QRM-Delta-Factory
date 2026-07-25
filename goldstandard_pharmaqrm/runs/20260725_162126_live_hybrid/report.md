# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-07-25T16:21:26+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 22 von 25 versteckten Fehlern gefunden (88%)
- **In Prüfmappe sichtbar:** 17 von 25 versteckten Fehlern (68%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Trefferquote der Ausgabe:** 22 von 48 Findings zeigen auf einen echten Fehler (46%)
- **Findings pro Fall:** 4.8 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 47 von 48 Findings mit verifiziertem Zitat (98%)

## Qualitätsmetriken

- Must-detect Recall: `8.8334`
- Duplikate: `6`
- Unsupported Findings: `8.9167`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `13/4/5`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 10 | 160 | 67 | 227 |
| mistral | 70 | 1,120 | 483 | 1,603 |
| openai | 10 | 153,021 | 27,032 | 180,053 |

## Fälle

| Fall | Status | Claims | Findings | ohne Fehlerbezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 18 | 8 | 6 | 2/2 | 2/2 | 0/1 | out_of_scope |
| CASE_02 | needs_human_review | 4 | 3 | 2 | 2/2 | 1/2 | 0/1 | out_of_scope |
| CASE_03 | needs_human_review | 7 | 6 | 5 | 1/2 | 1/2 | 0/2 | out_of_scope |
| CASE_04 | needs_human_review | 7 | 5 | 2 | 3/3 | 3/3 | 0/1 | out_of_scope |
| CASE_05 | needs_human_review | 2 | 1 | 0 | 2/3 | 1/3 | 0/1 | out_of_scope |
| CASE_06 | needs_human_review | 3 | 4 | 3 | 2/2 | 2/2 | 0/1 | out_of_scope |
| CASE_07 | needs_human_review | 6 | 6 | 4 | 2/2 | 1/2 | 0/1 | out_of_scope |
| CASE_08 | needs_human_review | 14 | 7 | 5 | 3/3 | 2/3 | 0/1 | out_of_scope |
| CASE_09 | needs_human_review | 5 | 4 | 2 | 2/3 | 1/3 | 0/1 | out_of_scope |
| CASE_10 | needs_human_review | 5 | 4 | 1 | 3/3 | 3/3 | 0/1 | out_of_scope |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Im Abweichungsbericht DEV-2026-891 ist das QA-Signaturdatum 14.12.2026 zeitlich unplausibel im Verhältnis zum Erfassungsdatum 12.03.2026 und zur QA-Freigabe der Charge XYL-2026-004A am 25.03.2026; dies ist ein Datenintegritäts- und Dokumentenkonsistenzrisiko.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): Die Einstufung von DEV-2026-891 als Minor und die Aussage "Ein Einfluss auf die Produktqualität wird ausgeschlossen" sind nicht ausreichend durch Daten belegt, obwohl der kritische Prozessparameter Manteltemperatur für 45 Minuten auf 34,2°C unter die Spezifikation 40°C bis 45°C gefallen ist.
- ℹ️ 6 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Spezifikationsverletzung/Yield-Unterschreitung: Ausbeute berechnet sich außerhalb der zulässigen Spezifikationsgrenzen; Ausbeute 96.47% liegt außerhalb des spezifizierten Bereichs 98% bis 101%. Yield-Unterschreitung wird fälschlicherweise als Freigabe deklariert; OOS/Abweichungsuntersuchung erforderlich.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_substring (Score 1.0): Spezifikationsverletzung/Yield-Unterschreitung: Ausbeute berechnet sich außerhalb der zulässigen Spezifikationsgrenzen; Ausbeute 96.47% liegt außerhalb des spezifizierten Bereichs 98% bis 101%. Yield-Unterschreitung wird fälschlicherweise als Freigabe deklariert; OOS/Abweichungsuntersuchung erforderlich.
- ℹ️ 2 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-2026-014 stuetzt die Aenderung des Reinigungsverfahrens auf "SOP-QS-REIN-001, Version 2.0 (gültig vom 12.01.2018)", wodurch im Paket nur veraltete Evidenz fuer den aktuellen Zustand belegt ist.
- ❌ `ERR_03_01` (high) — übersehen: Anachronistische Zeitstempel zwischen Raum-Logbuch und Probenahme-Protokoll.
- ℹ️ 5 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Zwischen Abweichungsbericht DEV-P-2026-092 und Batch Record PAR-2026-H102 besteht ein wesentlicher Widerspruch zur dokumentierten Maximaltemperatur: Im Abweichungsbericht werden maximal 44.5°C fuer 3 Minuten genannt, waehrend der Batch Record 48,2°C um 13:30 Uhr ausweist. Dadurch ist die Batch-Impact-Bewertung und die Entwarnung zur Charge PAR-2026-H102 nicht belastbar.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA CAPA-DEV-092 adressiert als Ursache mangelnde Aufmerksamkeit des Bedienpersonals und setzt ein Re-Training fuer Operator J.K. an, obwohl der Abweichungsbericht DEV-P-2026-092 als vermutete Ursache ein "hängendes Ventil im Heizregister der Zuluftanlage" nennt. Damit ist eine Zuschreibung auf Bedienerfehler ohne dokumentierten Ausschluss technischer Ursachen widerspruechlich und als Root-Cause-/CAPA-Basis nicht belastbar.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Fuer die Charge PAR-2026-H102 liegt im Paket eine Freigabeaussage vor, obwohl kein dokumentierter QA Approval Record nachgewiesen ist. Die Formulierung "wird für den nächsten Schritt freigegeben" ist ohne belegte QA-Freigabe nicht ausreichend.
- ℹ️ 2 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Zwischen den Dokumenten besteht am 11.05.2026 ein wesentlicher Widerspruch zur Anwesenheit und Identitaet der Personalnummer PNN-8812: Im Autoklavierungs-Logbuch ist "P.M. (Personalnummer: PNN-8812)" als ausfuehrender Mitarbeiter fuer Prozesszeiten ab 08:15 Uhr dokumentiert, waehrend das elektronische Zutrittssystem fuer dieselbe Personalnummer erst einen Eintritt um 08:45 Uhr ausweist und eine vorherige Anwesenheit verneint. Dies stellt ein Datenintegritaets- und Dokumentationsrisiko fuer die Rueckverfolgbarkeit des Sterilisationsschritts der Charge OXA-2026-088 dar.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Zwischen den Dokumenten besteht am 11.05.2026 ein wesentlicher Widerspruch zur Anwesenheit und Identitaet der Personalnummer PNN-8812: Im Autoklavierungs-Logbuch ist "P.M. (Personalnummer: PNN-8812)" als ausfuehrender Mitarbeiter fuer Prozesszeiten ab 08:15 Uhr dokumentiert, waehrend das elektronische Zutrittssystem fuer dieselbe Personalnummer erst einen Eintritt um 08:45 Uhr ausweist und eine vorherige Anwesenheit verneint. Dies stellt ein Datenintegritaets- und Dokumentationsrisiko fuer die Rueckverfolgbarkeit des Sterilisationsschritts der Charge OXA-2026-088 dar.
- ❌ `ERR_05_01` (medium) — übersehen: Verweis auf ein nicht vorhandenes bzw. fehlendes Dokumentenelement (Anhang 4).

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Spezifikationsverletzung: Wassergehalt 13.2% verletzt das Akzeptanzkriterium der internen Spezifikation; das Lieferanten-Zertifikat beziehungsweise Analysenzertifikat wird trotzdem als konform/Freigabe behandelt. Wirkstofffreigabe durch QA trotz ungelöster und aktiver Laborabweichung.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_substring (Score 1.0): Spezifikationsverletzung: Wassergehalt 13.2% verletzt das Akzeptanzkriterium der internen Spezifikation; das Lieferanten-Zertifikat beziehungsweise Analysenzertifikat wird trotzdem als konform/Freigabe behandelt. Wirkstofffreigabe durch QA trotz ungelöster und aktiver Laborabweichung.
- ℹ️ 3 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): Spezifikationsverletzung/Yield-Unterschreitung: Ausbeute berechnet sich außerhalb der zulässigen Spezifikationsgrenzen; Ausbeute 92.4% liegt außerhalb des spezifizierten Bereichs 95% bis 102%. Yield-Unterschreitung wird fälschlicherweise als Pass deklariert; OOS/Abweichungsuntersuchung erforderlich.
- ✅ `ERR_07_02` (medium) — gefunden via evidence_fuzzy (Score 0.64): Zur CAPA-MET-2026-09 ist zwar eine Massnahme mit Verantwortlichem und Deadline 15.06.2026 dokumentiert, im Paket fehlt jedoch ein Nachweis einer definierten Wirksamkeitspruefung fuer diese qualitaetsrelevante CAPA zu DEV-MET-09.
- ℹ️ 4 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Im Abweichungsbericht DEV-IBU-2026-112 wird fuer Charge IBU-2026-P03 ein "isoliertes Einzelereignis" und ein auf andere Chargen "absolut ausgeschlossen"er Einfluss behauptet, obwohl die Historie an TAB-02 bereits fruehere vergleichbare Abweichungen bei IBU-2026-P01 und IBU-2026-P02 zeigt. Damit ist die Entwarnung nicht ausreichend durch die vorgelegten Daten belegt und die dokumentierte Auswirkungsbewertung erscheint unzureichend.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.458): Im Abweichungsbericht DEV-IBU-2026-112 wird fuer Charge IBU-2026-P03 ein "isoliertes Einzelereignis" und ein auf andere Chargen "absolut ausgeschlossen"er Einfluss behauptet, obwohl die Historie an TAB-02 bereits fruehere vergleichbare Abweichungen bei IBU-2026-P01 und IBU-2026-P02 zeigt. Damit ist die Entwarnung nicht ausreichend durch die vorgelegten Daten belegt und die dokumentierte Auswirkungsbewertung erscheint unzureichend.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA CAPA-112-IBU sieht fuer den Inline-Metalldetektor eine priorisierte "Beschaffung, Qualifizierung und Softwareintegration im Steuerungsnetzwerk" mit Deadline "11.05.2026 (Abschluss der gesamten Validierung)" vor, jedoch enthaelt das bereitgestellte Paket keinen Validierungsnachweis oder Change-Impact-Nachweis fuer diese Aenderung. Damit ist die Validierungsabdeckung des aktuellen Zustands fuer die geplante technische Massnahme nicht belegt.
- ℹ️ 5 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Es besteht ein wesentlicher dokumentenuebergreifender Widerspruch zur Abweichung DEV-CEF-77: Der Abweichungsbericht beschreibt eine nicht final aufgeklaerte pH-Drift ueber 6 Stunden mit Ueberschreitung der Obergrenze pH 7,40, waehrend der Batch Record/SCADA einen manuellen Eingriff mit Deaktivierung des automatischen Regelkreises und Anhebung des Sollwerts auf pH 7,70 dokumentiert und der handschriftliche Batch Record zugleich "Keine besonderen Vorkommnisse" festhaelt. Dieser Widerspruch gefaehrdet die Konsistenz der Vorgangsdokumentation und die belastbare Ursachen- und Impact-Bewertung.
- ✅ `ERR_09_02` (high) — gefunden via evidence_fuzzy (Score 0.412): Fuer die Abweichung DEV-CEF-77 ist in den vorliegenden Unterlagen keine dokumentierte Auswirkungsbewertung auf Produktqualitaet und betroffene Charge CEF-BIOR-2026-77 belegt, obwohl ein kritischer Prozessparameter die spezifizierte Obergrenze pH 7,40 ueberschritten hat und die Aufarbeitung fortgesetzt wurde.
- ❌ `ERR_09_03` (medium) — übersehen: Unvollständig genehmigtes Change-Control-Dokument ohne finale QK-Freigabe.
- ℹ️ 2 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Spezifikationsverletzung/OOS-Stabilitätsfehler: Verunreinigung 0.32% liegt außerhalb der Maximalgrenze 0.2%. Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler; Prüfung wird als konform/fortgesetzt/erfuellt behandelt.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Sofortmassnahme CAPA-OOS-INS fuer die Charge INS-GLA-2025-05 hat zwar ein Zieldatum 16.05.2026, aber keinen benannten Verantwortlichen. Damit ist die Umsetzungsverantwortung fuer eine qualitaetsrelevante Sofortmassnahme nicht ausreichend festgelegt.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Fuer die Marktware-Charge INS-GLA-2025-05 wird am 19.05.2026 eine vorlaeufige Entwarnung bzw. Dispositionsaussage dokumentiert, obwohl der 12-Monats-Stabilitaetspruefpunkt am 15.05.2026 eine Verunreinigung von 0,32% gegen die Zulassungsgrenze maximal 0,20% zeigte und das Labor-Re-Testing laut CAPA noch final offen ist. Das ist ein Risiko einer Disposition bzw. Marktentscheidung vor abgeschlossener OOS-/Abweichungsbewertung.
- ℹ️ 1 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
