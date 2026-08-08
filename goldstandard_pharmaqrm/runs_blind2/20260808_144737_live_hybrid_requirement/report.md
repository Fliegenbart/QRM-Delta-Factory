# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid` | Engine: `requirement`
- Zeitpunkt: 2026-08-08T14:47:37+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 26 von 38 versteckten Fehlern gefunden (68%)
- **In Prüfmappe sichtbar:** 24 von 38 versteckten Fehlern (63%)
- **Spezifität (Decoys):** 41 von 42 Decoys korrekt nicht beanstandet (98%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 46 von 158 (29%) — 21 als Treffer gewertet, 25 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 112 von 158 (71%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 15.8 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 61 von 158 Findings mit verifiziertem Zitat (39%)

## Qualitätsmetriken

- Must-detect Recall: `0.6842`
- Wiederholungen: `25` (Redundanzrate `0.5435`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `11/10/5`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 61 | 113,119 | 26,280 | 139,399 |
| mistral | 202 | 1,608,280 | 386,950 | 1,995,230 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 18 | 4 | 12 | 2/3 | 2/3 | 1/5 | - |
| CASE_02 | completed_with_model_failures | 0 | 18 | 0 | 16 | 3/3 | 2/3 | 0/5 | - |
| CASE_03 | completed_with_model_failures | 0 | 13 | 0 | 12 | 1/3 | 1/3 | 0/4 | - |
| CASE_04 | completed_with_model_failures | 0 | 11 | 3 | 5 | 3/4 | 3/4 | 0/4 | - |
| CASE_05 | completed | 0 | 19 | 3 | 13 | 3/4 | 3/4 | 0/3 | - |
| CASE_06 | completed | 0 | 17 | 1 | 15 | 3/4 | 2/4 | 0/4 | - |
| CASE_07 | completed_with_model_failures | 0 | 18 | 3 | 12 | 4/4 | 4/4 | 0/5 | - |
| CASE_08 | completed | 0 | 15 | 9 | 2 | 4/4 | 4/4 | 0/4 | - |
| CASE_09 | completed_with_model_failures | 0 | 16 | 0 | 15 | 1/5 | 1/5 | 0/4 | - |
| CASE_10 | completed_with_model_failures | 0 | 13 | 2 | 10 | 2/4 | 2/4 | 0/4 | - |

## Modellausfälle

- **ProviderCallError** (7×): mistral provider output was truncated
  - betroffen: CASE_02/extract[doc_0cd57f84c5ef4d86911a27e515c8c9c2:werte]:20, CASE_03/extract[doc_49f663cb5bd142f795f285d0025018ca:werte]:24, CASE_04/extract[doc_325042f6f5a54a65b25c10ea193af2bd:felder]:25, CASE_07/extract[doc_282959ae53824aeaaf7f8391719656d5:werte]:27, CASE_09/extract[doc_5d92c778b240433682dbf8393d533245:werte]:31, CASE_10/extract[doc_55466cac06284375b5b7ee7119b62fd5:felder]:22
  - … und 1 weitere
- **ProviderStructuredOutputError** (1×): 1 validation error for RequirementGroupOutput
verdicts.0.evidence
  Input should be a valid list [type=list_type, input_value=None, input_type=NoneType]
    For
  - betroffen: CASE_10/assess:4

### CASE_01

- ✅ `BLIND201-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen erfüllen das ALCOA+-Kriterium der Vollständigkeit nicht. Im BMR-Auszug (BMR-CT-24118, Abschnitt 7.3b) wird ein nachträglicher Eintrag dokumentiert: "Die Uhrzeit zu Schritt 7.3 wurde am 14.03.2026 bei Schichtwechsel nicht in das BMR eingetragen. Ergänzung am 15.03.2026 um 08:40 Uhr durch Sandra Kremp anhand des Prozessleitsystem-Ausdrucks PLS-FS02-20260314, der der Chargendokumentation beiliegt." Dieser nachträgliche Eintrag ohne zeitgleiche Dokumentation verletzt das ALCOA+-Prinzip der Zeitgleichheit und Vollständigkeit.
- ✅ `BLIND201-E003` (medium) — gefunden via evidence_fuzzy (Score 0.452): Die QA-Freigabe und Genehmigungen sind vor Abschluss dokumentiert:
- Die QA-Bewertung QAB-2026-0142 (document_04_qa_bewertung.md) enthält eine signierte Freigabeerklärung der Qualitätsicherung (Dr. Marlene Ostwald, 19.03.2026) und den Chargenentscheid der Sachkundigen Person (Dr. Elif Bayram, 19.03.2026).
- Der CAPA-Plan CAPA-2026-0061 wurde von der Qualitätssicherung freigegeben (Dr. Marlene Ostwald, 18.03.2026).
- Die Unterschriftenliste (document_05_unterschriftenliste.md) bestätigt die Zeichnungsberechtigung der genannten Personen für QA-Freigaben.

Es gibt keine Hinweise auf geplante, aber nicht dokumentierte Freigaben.
- ❌ `BLIND201-E002` (medium) — übersehen: Die in der QA-Bewertung festgestellte Audit-Trail-Auswertung des Geräts IT-04 ist durch keinen Nachweis belegt; in der Fallmappe existiert weder ein Audit-Trail-Export noch eine Referenz auf ein solches Dokument.
- ⚠️ Decoy `BLIND201-D003` fälschlich beanstandet: Die Aufzeichnungen erfüllen das ALCOA+-Kriterium der Vollständigkeit nicht. Im BMR-Auszug (BMR-CT-24118, Abschnitt 7.3b) wird ein nachträglicher Eintrag dokumentiert: "Die Uhrzeit zu Schritt 7.3 wurde am 14.03.2026 bei Schichtwechsel nicht in das BMR eingetragen. Ergänzung am 15.03.2026 um 08:40 Uhr durch Sandra Kremp anhand des Prozessleitsystem-Ausdrucks PLS-FS02-20260314, der der Chargendokumentation beiliegt." Dieser nachträgliche Eintrag ohne zeitgleiche Dokumentation verletzt das ALCOA+-Prinzip der Zeitgleichheit und Vollständigkeit.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `BLIND202-E001` (high) — gefunden via evidence_fuzzy (Score 0.788): Die Anforderung verlangt, dass kritische Prozessparameter innerhalb der spezifizierten Grenzen liegen. Im BMR-Auszug (document_02_ipc_protokoll_tablettierung.md) wird dokumentiert, dass der Mittelwert der Tablettenmasse bei IPC-05 mit 431,2 mg die Obergrenze von 428,4 mg überschritten hat. Dies stellt eine klare Überschreitung des spezifizierten Prozessparameters dar, die als Abweichung bewertet wurde. Die Überschreitung ist somit belegt, auch wenn Sofortmaßnahmen ergriffen wurden.
- ✅ `BLIND202-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass kritische Prozessparameter innerhalb der spezifizierten Grenzen liegen. Im BMR-Auszug (document_02_ipc_protokoll_tablettierung.md) wird dokumentiert, dass der Mittelwert der Tablettenmasse bei IPC-05 mit 431,2 mg die Obergrenze von 428,4 mg überschritten hat. Dies stellt eine klare Überschreitung des spezifizierten Prozessparameters dar, die als Abweichung bewertet wurde. Die Überschreitung ist somit belegt, auch wenn Sofortmaßnahmen ergriffen wurden.
- ✅ `BLIND202-E003` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan in document_03_capa_plan.md, Abschnitt 3, listet für jede Maßnahme einen benannten Verantwortlichen und einen konkreten Umsetzungstermin auf. Die Termine sind plausibel und realisierbar (z. B. 30.06.2026, 31.07.2026, 15.07.2026, 20.08.2026).
- ℹ️ 16 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `BLIND203-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Unterlagen enthalten keinen dokumentierten Audit-Trail-Review für die Anlagensteuerung LYO-03 während des Chargenlaufs. Zwar wird in der QA-Bewertung (document_04_qa_bewertung.md, chunk_f94f99064eee4ff29b42ebde919472a7_p1) erwähnt, dass der Audit Trail gesichtet wurde, jedoch fehlt ein konkreter Nachweis (z. B. ein signierter Review-Bericht oder ein Auszug des Audit Trails mit Bewertung). Die bloße Behauptung der Sichtung reicht als Primärevidenz nicht aus.
- ❌ `BLIND203-E001` (high) — übersehen: Die Stellflächentemperatur unterschreitet mit -23.4 °C am 13.03.2026 um 06:00 Uhr die in derselben Aufzeichnung festgelegte Untergrenze von -22,0 °C; diese Grenzwertverletzung ist weder im Abweichungsbericht noch in der Bewertung der Qualitätseinheit erfasst.
- ❌ `BLIND203-E002` (medium) — übersehen: Die Alarmquittierung und Nachregelung um 03:47 Uhr wird im Ereignisprotokoll mit dem Kürzel TMB gezeichnet, im Bearbeitungsvermerk desselben Abschnitts jedoch K. Ohlendorf (KOH) zugeschrieben; die Aufzeichnung ist damit in sich widersprüchlich.
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `BLIND204-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Auswirkungsbewertung der Abweichung ist im Abweichungsbericht (document_01_abweichungsbericht.md), in der Bewertung der Qualitätseinheit (document_04_qa_bewertung.md) und in der Chargen-Impact-Übersicht (document_05_chargen_impact_verteiler.md) dokumentiert. Alle potenziell betroffenen Chargen (RM-2572-A, RM-2573-A, RM-2574-A) sind aufgeführt, und die Auswirkungen auf die Rückverfolgbarkeit und Patientensicherheit sind bewertet. Die Bewertung umfasst auch die ausgelieferten Teilmengen und deren Empfänger.
- ✅ `BLIND204-E002` (high) — gefunden via evidence_substring (Score 1.0): Jede Maßnahme im CAPA-Plan (chunk_6d1ef4a7731e47abb4934aeff823adde_p1) enthält einen benannten Verantwortlichen und einen Umsetzungstermin. Dies erfüllt die Anforderung nach einem benannten Maßnahmenverantwortlichen und einem plausiblen Terminplan.
- ✅ `BLIND204-E003` (medium) — gefunden via evidence_substring (Score 1.0): Im Verpackungsprotokoll (chunk_325042f6f5a54a65b25c10ea193af2bd_p1, Abschnitt 4.6) wird ein Nachtragsvermerk dokumentiert: "Die Zeilen der Inprozesskontrolle vom 16.04.2026, 11:00 Uhr und 13:00 Uhr wurden zum Zeitpunkt der Kontrolle ausgefüllt, jedoch nicht gezeichnet. Der Nachtrag der Zeichnung erfolgte am 17.04.2026 um 07:35 Uhr durch Y. Brahms (YBR); Grund: Abbruch der Dokumentation wegen der Endkontrolle im Palettierbereich." Dies zeigt, dass die Signatur nicht zeitnah zum Vorgang erfolgte, was die Plausibilität und Konsistenz der Signaturdaten infrage stellt. Zudem fehlt eine klare Angabe der Bedeutung der Signatur in den nachgetragenen Einträgen, was gegen die Anforderung verstößt.
- ❌ `BLIND204-E004` (medium) — übersehen: Zwischen der Feststellung der als kritisch eingestuften Abweichung am 16.04.2026 um 14:20 Uhr und der formellen Meldung an die Qualitätseinheit am 18.04.2026 um 08:40 Uhr liegen rund 42 Stunden; die nach SOP QM-DEV-002, Version 8.0, geltende Meldefrist von 24 Stunden ist damit überschritten, ohne dass dies in den Unterlagen behandelt wird.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `BLIND205-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die analytischen Ergebnisse der Wischproben und Spülproben (QC-2026-1188) wurden gegen die internen Akzeptanzkriterien nach SOP-RE-118, Abschnitt 5.6, bewertet. Die QA-Bewertung (QA-BEW-2026-0193) bestätigt die Einhaltung der Spezifikationen: 'Die analytischen Ergebnisse der Reinigungskontrolle nach QC-2026-1188 liegen in der für WSG-04 typischen Größenordnung. Der rechnerische Übertrag auf die Folgecharge unterschreitet den internen Orientierungswert nach SOP-RE-118, Abschnitt 5.7, um mehr als das Zwanzigfache.' Zudem wird im analytischen Protokoll explizit auf die Akzeptanzkriterien Bezug genommen und die Ergebnisse werden einzeln gegen diese geprüft (z. B. 'Einzelwerte, die A-2 überschreiten, führen zur Sperrung der Anlage').
- ✅ `BLIND205-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen sind zurechenbar, lesbar, zeitgleich, original und korrekt sowie vollständig, konsistent, dauerhaft und verfügbar. Dies wird durch folgende Punkte belegt: 1. Alle Dokumente enthalten eindeutige Identifikationsnummern (z. B. Dokument-Nr. QA-BEW-2026-0193, Protokoll-Nr. QC-2026-1188) und sind mit Datum, Uhrzeit sowie verantwortlichen Personen versehen. 2. Die Originalaufzeichnungen sind in den Dokumenten enthalten, z. B. das analytische Protokoll QC-2026-1188 mit Rohdaten und Unterschriften (chunk_2ed97a0402c247bf94276884788a955b_p1). 3. Es gibt keine Hinweise auf nachträgliche Veränderungen; alle Änderungen oder Wiederholungen (z. B. Wiederholprobe R-1188-02) sind dokumentiert und begründet. 4. Die Dokumente sind konsistent und verweisen aufeinander (z. B. Bezug von DEV-2026-0417 auf QC-2026-1188 und CAPA-2026-0117).
- ✅ `BLIND205-E004` (low) — gefunden via evidence_substring (Score 1.0): Die SOP-RE-118 wurde am 01.03.2026 auf Version 4.2 aktualisiert. Im CAPA-Plan (Maßnahme 2) ist eine Schulung der Technik und Schichtleitung auf die geänderte Checkliste F-QM-020 für den 15.07.2026 terminiert. Die Abweichung DEV-2026-0417 trat jedoch bereits am 13.05.2026 auf, und die Reinigung wurde am 12.05.2026 durchgeführt. Es gibt keinen Nachweis, dass das betroffene Personal (z. B. S. Brandhoff, SBR) vor der Durchführung der Reinigung auf die aktualisierte SOP geschult wurde. Der Schulungsnachweis für SBR vom 04.03.2026 bezieht sich auf die alte Version 3.8 der SOP, nicht auf Version 4.2.
- ❌ `BLIND205-E002` (high) — übersehen: Die Umrechnung von 113.190 µg in 11,32 mg ist um eine Zehnerpotenz falsch; der rechnerische Übertrag beträgt 0,45 mg/kg statt 0,045 mg/kg, und die darauf gestützte Aussage der QA-Bewertung zum Abstand vom Orientierungswert ist damit unzutreffend.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 13 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `BLIND206-E001` (critical) — gefunden via evidence_fuzzy (Score 0.589): Die Aufzeichnungen sind vollständig, original und zeitgleich dokumentiert. Die Nachtragszeichnung zu Position 6 im Einwaageprotokoll (BMR-T-26043) ist nach SOP-QM-018, Abschnitt 7.3, begründet und mit Datum/Uhrzeit sowie Unterschriften versehen. Der Audit-Trail-Auszug (ERP-AZ-2026-0644) bestätigt die Unveränderlichkeit der Buchungen und Statuswechsel.
- ✅ `BLIND206-E002` (high) — gefunden via evidence_fuzzy (Score 0.545): Die Aufzeichnungen sind vollständig, original und zeitgleich dokumentiert. Die Nachtragszeichnung zu Position 6 im Einwaageprotokoll (BMR-T-26043) ist nach SOP-QM-018, Abschnitt 7.3, begründet und mit Datum/Uhrzeit sowie Unterschriften versehen. Der Audit-Trail-Auszug (ERP-AZ-2026-0644) bestätigt die Unveränderlichkeit der Buchungen und Statuswechsel.
- ✅ `BLIND206-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen sind vollständig, original und zeitgleich dokumentiert. Die Nachtragszeichnung zu Position 6 im Einwaageprotokoll (BMR-T-26043) ist nach SOP-QM-018, Abschnitt 7.3, begründet und mit Datum/Uhrzeit sowie Unterschriften versehen. Der Audit-Trail-Auszug (ERP-AZ-2026-0644) bestätigt die Unveränderlichkeit der Buchungen und Statuswechsel.
- ❌ `BLIND206-E004` (low) — übersehen: Die im Einwaageprotokoll ausgewiesene Gesamteinwaage von 62,244 kg stimmt nicht mit der Summe der Einzelpositionen von 62,144 kg überein.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 15 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `BLIND207-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung ist erfüllt, da die Aufzeichnungen die ALCOA+-Kriterien (zurechenbar, lesbar, zeitgleich, original, korrekt, vollständig, konsistent, dauerhaft und verfügbar) erfüllen. Der Logbuchauszug (LB-KS04-2026-03) dokumentiert den Ereignisverlauf mit Zeitstempeln, Messwerten und verantwortlichen Personen. Nachträge sind als solche gekennzeichnet und gegengezeichnet. Der Abweichungsbericht (ABW-2026-0184) enthält alle relevanten Informationen, einschließlich der Sofortmaßnahmen, Ursachenanalyse und Klassifizierung, und ist von den verantwortlichen Personen signiert. Die QA-Bewertung (QAB-2026-0071) bestätigt die Vollständigkeit der Unterlagen.
- ✅ `BLIND207-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung ist erfüllt, da die Aufzeichnungen die ALCOA+-Kriterien (zurechenbar, lesbar, zeitgleich, original, korrekt, vollständig, konsistent, dauerhaft und verfügbar) erfüllen. Der Logbuchauszug (LB-KS04-2026-03) dokumentiert den Ereignisverlauf mit Zeitstempeln, Messwerten und verantwortlichen Personen. Nachträge sind als solche gekennzeichnet und gegengezeichnet. Der Abweichungsbericht (ABW-2026-0184) enthält alle relevanten Informationen, einschließlich der Sofortmaßnahmen, Ursachenanalyse und Klassifizierung, und ist von den verantwortlichen Personen signiert. Die QA-Bewertung (QAB-2026-0071) bestätigt die Vollständigkeit der Unterlagen.
- ✅ `BLIND207-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung ist erfüllt, da eine dokumentierte Bewertung der Auswirkung auf die Produktqualität und Patientensicherheit vorliegt. Im Abweichungsbericht (ABW-2026-0184) wird in Abschnitt 6 auf die produktbezogene Bewertung verwiesen, die im Bericht STB-2026-041 dokumentiert ist. Zudem listet der Abweichungsbericht in Abschnitt 2 alle betroffenen Chargen auf, die während der Temperaturexkursion im Klimaschrank KS-04 eingelagert waren. Die QA-Bewertung (QAB-2026-0071) bestätigt in Abschnitt 3 die Bewertung der eingelagerten Chargen und deren Fortführung ohne Auflagen.
- ✅ `BLIND207-E004` (high) — gefunden via evidence_substring (Score 1.0): Die QA-Bewertung QAB-2026-0071 und der Abweichungsbericht ABW-2026-0184 erfassen alle im Klimaschrank KS-04 eingelagerten Chargen der Studie STB-24-017 (R6-2411, R6-2503, R6-2508). Die Bewertung bezieht sich explizit auf 'alle in Klimaschrank KS-04 eingelagerten Chargen der Studie STB-24-017'. Es gibt keine Hinweise auf fehlende Chargen oder Vorgänger-/Folgechargen, die nicht berücksichtigt wurden.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `BLIND208-E001` (medium) — gefunden via evidence_substring (Score 1.0): Jede Maßnahme im CAPA-Plan (CAPA-2026-0117) hat einen benannten Verantwortlichen und einen realistischen Umsetzungstermin. Dies ist in der Maßnahmenliste unter Abschnitt 2 dokumentiert.
- ✅ `BLIND208-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Auswirkungsbewertung der Abweichung auf Produktqualität und Patientensicherheit ist dokumentiert. Die QA-Bewertung (QAB-2026-0098) umfasst die mikrobiologischen Ergebnisse der gesamten Kampagne (kein Wachstum in Klasse A), die Filterintegritätsprüfung und die Risikoakzeptanz mit Auflagen. Alle potenziell betroffenen Chargen (DX-2604, DX-2605, DX-2606) wurden bewertet und freigegeben.
- ✅ `BLIND208-E003` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass eine Charge nicht freigegeben werden darf, solange die Abweichungsbewertung oder erforderliche QA-Freigabe nicht abgeschlossen ist. Im QA-Bewertungs- und Freigabevermerk (document_05_qa_bewertung_freigabe.md, chunk_id: chunk_ab18e8eb7ad04866a4ff7d62ab91ba78_p1) wird die Freigabe der Chargen DX-2604, DX-2605 und DX-2606 am 27.04.2026 dokumentiert. Allerdings ist zu diesem Zeitpunkt die Abweichung ABW-2026-0233 noch nicht abgeschlossen (Abschluss ist laut CAPA-Plan erst nach Umsetzung der Maßnahmen 2 bis 4 aus CAPA-2026-0117 vorgesehen, siehe document_05_qa_bewertung_freigabe.md, Abschnitt 7). Zudem fehlt der Nachweis, dass die Wirksamkeitsprüfung der CAPA-Maßnahmen (Effectiveness Check) vor der Freigabe durchgeführt wurde.
- ✅ `BLIND208-E004` (high) — gefunden via evidence_substring (Score 1.0): Die SOP-MB-042 wurde im Rahmen des Change Controls CC-2025-0210 überarbeitet (document_06_schulungsnachweis.md). Die Schulung der betroffenen Mitarbeiter fand am 27.04.2026 statt, jedoch wurde die Charge DX-2604 bereits am 21.04.2026 abgefüllt, also *vor* der Schulung. Der Eingriff am 21.04.2026 erfolgte somit nach der alten SOP-Version 04, während die aktualisierte Version 05 erst ab dem 15.04.2026 gültig war. Es fehlt der Nachweis, dass die Mitarbeiter vor dem Eingriff wirksam in der neuen SOP-Version geschult wurden. Die Lernerfolgskontrolle allein reicht nicht aus, da sie erst nach der Schulung durchgeführt wurde.
- 🔁 9 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 2 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `BLIND209-E001` (high) — gefunden via evidence_fuzzy (Score 0.426): Die QA-Bewertung bestätigt, dass die Charge V-26-0817 gesperrt bleibt und nicht freigegeben wurde, bis Abweichungsbewertung, Impact Assessment und QA-Freigabe abgeschlossen waren. Die Sperrung erfolgte bereits am 10.03.2026 (Sofortmaßnahme S1), die QA-Bewertung und Freigabe der Dispositionsentscheidung datieren auf den 19.03.2026.
- ❌ `BLIND209-E002` (high) — übersehen: Die im Abweichungsbericht angegebene Leckrate von 2,8 Prozent ist rechnerisch falsch; 14 von 320 Ampullen ergeben 4,4 Prozent und damit eine Überschreitung des in der QA-Bewertung genannten Aktionslimits von 3,0 Prozent, auf das die Entscheidung gegen eine Ausweitung der Prüfung gestützt wird.
- ❌ `BLIND209-E003` (medium) — übersehen: Die auf dem Lieferantenzertifikat gezeichnete Wareneingangsprüfung vom 02.03.2026 liegt zwei Tage vor dem im BMR-Auszug dokumentierten Wareneingang des Loses AMP-9042-B am 04.03.2026.
- ❌ `BLIND209-E004` (critical) — übersehen: Die Charge V-26-0817 wurde am 09.03.2026 mit dem neuen Primärpackmittel abgefüllt, während die QA-Freigabe zur Implementierung des zugehörigen Change Control CC-2026-181 erst am 11.03.2026 erteilt wurde; der Ersteinsatz erfolgte damit vor der formalen Freigabe der Änderung.
- ❌ `BLIND209-E005` (medium) — übersehen: In der Maßnahmenliste des Change Control CC-2026-181 fehlt für Maßnahme 3 (Wirksamkeitsprüfung) der Termin, während für alle übrigen Maßnahmen Termine ausgewiesen sind.
- ℹ️ 15 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `BLIND210-E001` (critical) — gefunden via evidence_fuzzy (Score 0.44): Der CAPA-Plan CAPA-2026-0179 enthält eine definierte und dokumentierte Wirksamkeitsprüfung (Effectiveness Check) für die Maßnahmen K3 und K4. Die Wirksamkeitsprüfung ist mit messbaren Kriterien hinterlegt und als eigener Vorgang EFF-2026-0051 angelegt. Die QA-Bewertung bestätigt, dass der CAPA-Plan angemessen ist und die Wirksamkeitsprüfung durchgeführt wird.
- ✅ `BLIND210-E004` (medium) — gefunden via evidence_fuzzy (Score 0.413): Der CAPA-Plan CAPA-2026-0179 enthält eine definierte und dokumentierte Wirksamkeitsprüfung (Effectiveness Check) für die Maßnahmen K3 und K4. Die Wirksamkeitsprüfung ist mit messbaren Kriterien hinterlegt und als eigener Vorgang EFF-2026-0051 angelegt. Die QA-Bewertung bestätigt, dass der CAPA-Plan angemessen ist und die Wirksamkeitsprüfung durchgeführt wird.
- ❌ `BLIND210-E002` (medium) — übersehen: Im CAPA-Plan CAPA-2026-0179 fehlt für die Korrekturmaßnahme K3 der Termin, während alle übrigen Maßnahmen des Plans terminiert sind.
- ❌ `BLIND210-E003` (high) — übersehen: Die im Abweichungsbericht als betroffen geführte Charge KF-26-3303 fehlt in der Chargen-Impact-Tabelle und im Verteiler der QA-Bewertung QAB-2026-0611; eine dokumentierte Bewertung und Statusentscheidung für diese Charge liegt nicht vor.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
