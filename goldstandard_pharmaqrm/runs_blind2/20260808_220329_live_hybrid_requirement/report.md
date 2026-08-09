# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid` | Engine: `requirement`
- Zeitpunkt: 2026-08-08T22:03:29+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 30 von 38 versteckten Fehlern gefunden (79%)
- **In Prüfmappe sichtbar:** 29 von 38 versteckten Fehlern (76%)
- **Spezifität (Decoys):** 41 von 42 Decoys korrekt nicht beanstandet (98%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 55 von 155 (35%) — 29 als Treffer gewertet, 26 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 100 von 155 (65%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 15.5 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 64 von 155 Findings mit verifiziertem Zitat (41%)

## Qualitätsmetriken

- Must-detect Recall: `0.7895`
- Wiederholungen: `26` (Redundanzrate `0.4727`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `13/11/6`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 76 | 138,496 | 34,053 | 172,549 |
| mistral | 202 | 1,568,835 | 410,660 | 1,979,495 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 18 | 4 | 11 | 3/3 | 3/3 | 1/5 | - |
| CASE_02 | completed_with_model_failures | 0 | 16 | 0 | 14 | 2/3 | 2/3 | 0/5 | - |
| CASE_03 | completed | 0 | 12 | 1 | 9 | 2/3 | 2/3 | 0/4 | - |
| CASE_04 | completed_with_model_failures | 0 | 15 | 1 | 10 | 4/4 | 4/4 | 0/4 | - |
| CASE_05 | completed | 0 | 18 | 5 | 9 | 4/4 | 4/4 | 0/3 | - |
| CASE_06 | completed | 0 | 14 | 0 | 12 | 3/4 | 2/4 | 0/4 | - |
| CASE_07 | completed_with_model_failures | 0 | 17 | 5 | 8 | 4/4 | 4/4 | 0/5 | - |
| CASE_08 | completed | 0 | 17 | 9 | 4 | 4/4 | 4/4 | 0/4 | - |
| CASE_09 | completed_with_model_failures | 0 | 16 | 1 | 13 | 2/5 | 2/5 | 0/4 | - |
| CASE_10 | completed_with_model_failures | 0 | 12 | 0 | 10 | 2/4 | 2/4 | 0/4 | - |

## Modellausfälle

- **ProviderCallError** (6×): mistral provider output was truncated
  - betroffen: CASE_02/extract[doc_c0e8e6d8ec98406092d476653c047945:werte]:24, CASE_04/extract[doc_5d97cd759bbf4bc497b6cf84b67bad84:felder]:29, CASE_07/extract[doc_271f781b313c4df88b07988a69fc5368:werte]:27, CASE_09/extract[doc_8359283868bb40b4b7a976cdb6e6d139:werte]:32, CASE_10/extract[doc_0bfb7c3086c446ed84aee10b995eb524:felder]:25, CASE_10/extract[doc_0bfb7c3086c446ed84aee10b995eb524:werte]:26

### CASE_01

- ✅ `BLIND201-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt vollständige, zeitgleich erfasste Originalaufzeichnungen. Im BMR-Auszug (chunk_c6d6a7c7b5ff4e43b6144b8ca9cf4194_p1) fehlt die Uhrzeit zu Schritt 7.3 (Filtrationsende) im Originaleintrag und wurde erst am Folgetag nachgetragen: 'Nachtrag vom 15.03.2026: Die Uhrzeit zu Schritt 7.3 wurde am 14.03.2026 bei Schichtwechsel nicht in das BMR eingetragen. Ergänzung am 15.03.2026 um 08:40 Uhr durch Sandra Kremp...'. Dies verstößt gegen die ALCOA+-Prinzipien der Zeitgleichheit und Vollständigkeit.
- ✅ `BLIND201-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Bewertung QAB-2026-0142 erwähnt in Abschnitt 2 eine durchgeführte Audit-Trail-Auswertung des Integritätstestgeräts IT-04 für den relevanten Zeitraum (14.03.2026, 07:00–14:00 Uhr) ohne Auffälligkeiten. Es fehlt jedoch ein dokumentierter Audit-Trail-Review mit Unterschrift, Datum und konkreten Prüfergebnissen (z. B. Auszug des Audit Trails oder Checkliste). Die bloße Behauptung 'keine Auffälligkeiten' genügt nicht als Primärevidenz für einen regelhaften, risikobasierten Review.
- ✅ `BLIND201-E003` (medium) — gefunden via evidence_fuzzy (Score 0.411): Die Auswirkungsbewertung der Abweichung ist dokumentiert. Im CAPA-Plan (CAPA-2026-0061, Abschnitt 5) wird eine Auswertung der Testlaufhistorie des Geräts IT-04 für den Zeitraum 01.01.2026 bis 14.03.2026 durchgeführt, um die Auswirkung auf andere Chargen zu prüfen. Zudem wird im QA-Bewertungsdokument (QAB-2026-0142, Abschnitt 3 und 5) die Sterilität der Charge CT-24118 als nicht belegt bewertet und die Charge zur Vernichtung freigegeben. Dies umfasst die Bewertung der Auswirkung auf Produktqualität und Patientensicherheit sowie die Identifikation betroffener Chargen.
- ⚠️ Decoy `BLIND201-D003` fälschlich beanstandet: Die Signaturdaten im BMR-Auszug (Schritt 7.3) wurden nachträglich am 15.03.2026 ergänzt, da die Uhrzeit bei Schichtwechsel nicht eingetragen wurde. Dies stellt eine zeitliche Inkonsistenz dar, da die Signatur nicht zeitnah zum Vorgang erfolgte. Zudem fehlt im BMR-Auszug die Unterschrift der ausführenden Person für Schritt 7.4 (Post-Use-Integritätstest).
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 11 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `BLIND202-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Inprozesskontrolle der Tablettenmasse wurde gegen die interne Spezifikation bewertet. Der Mittelwert der Tablettenmasse lag an einem Prüfpunkt (IPC-05) mit 431,2 mg oberhalb der festgelegten Obergrenze von NMT 428,4 mg, was als Abweichung behandelt wurde (DEV-2026-0093). Die Spezifikationen und die Bewertung der Messwerte sind im BMR-Auszug (Abschnitt 9.2 und 9.3) dokumentiert und wurden im Abweichungsbericht (Abschnitt 3) sowie in der QA-Bewertung (Abschnitt 3) bestätigt.
- ✅ `BLIND202-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass kritische Prozessparameter innerhalb der spezifizierten Grenzen liegen. Im BMR-Auszug (document_02_ipc_protokoll_tablettierung.md, Abschnitt 9.3) wird dokumentiert, dass der Mittelwert der Tablettenmasse bei IPC-05 mit 431,2 mg oberhalb der Obergrenze von NMT 428,4 mg lag. Dies stellt eine Überschreitung der spezifizierten Grenze dar. Obwohl die betroffene Teilmenge ausgeschleust wurde, ist die Überschreitung selbst ein Verstoß gegen die Anforderung, da kritische Prozessparameter nicht eingehalten wurden.
- ❌ `BLIND202-E003` (medium) — übersehen: Im CAPA-Plan ist bei Maßnahme 3 das Pflichtfeld Verantwortlicher mit siehe oben statt mit einer namentlich benannten Person belegt; der Verweis ist wegen der unterschiedlichen Verantwortlichen der übrigen Maßnahmen nicht eindeutig auflösbar.
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `BLIND203-E001` (high) — gefunden via evidence_substring (Score 1.0): Der Kammerdruck während der Primärtrocknung überschritt die spezifizierte Obergrenze von NMT 100 µbar (Sollwert: 70 µbar) mit einem Maximalwert von 142 µbar für 48 Minuten. Dies ist eine klare Überschreitung der Prozessparameter-Grenzen, auch wenn die Produktqualität visuell unauffällig erscheint.
- ✅ `BLIND203-E003` (medium) — gefunden via evidence_fuzzy (Score 0.407): Die Anforderung verlangt einen regelmaessigen, risikobasierten Audit-Trail-Review, der sicherheits- oder qualitaetsrelevante Eintraege nicht ausschliesst. Im Abweichungsbericht (DEV-2026-0088) wird zwar der Audit Trail der Anlagensteuerung LYO-03 gesichtet (document_04_qa_bewertung.md, chunk_6c7260b54b8f460da2592f75622ac570_p1, Seite 1: 'Der Audit Trail der Anlagensteuerung LYO-03 wurde fuer den gesamten Chargenlauf gesichtet; ueber die in DEV-2026-0088 beschriebenen Eingriffe hinaus wurden keine weiteren manuellen Eingriffe an den Zyklusparametern festgestellt.'). Dies belegt jedoch nur eine einmalige Sichtung im Rahmen der Abweichungsbewertung, nicht jedoch einen regelmaessigen, risikobasierten Review. Es fehlt ein dokumentierter Nachweis, dass der Audit-Trail-Review regelmaessig und unabhaengig von Abweichungen durchgefuehrt wird.
- ❌ `BLIND203-E002` (medium) — übersehen: Die Alarmquittierung und Nachregelung um 03:47 Uhr wird im Ereignisprotokoll mit dem Kürzel TMB gezeichnet, im Bearbeitungsvermerk desselben Abschnitts jedoch K. Ohlendorf (KOH) zugeschrieben; die Aufzeichnung ist damit in sich widersprüchlich.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `BLIND204-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Chargen-Impact-Übersicht listet alle betroffenen Chargen (RM-2572-A, RM-2573-A, RM-2574-A) auf und bestätigt, dass keine weiteren Chargen (inkl. Vorgänger- oder Folgechargen) betroffen sind. Die Auswahl ist somit vollständig und nachvollziehbar.
- ✅ `BLIND204-E002` (high) — gefunden via evidence_substring (Score 1.0): Jede CAPA-Maßnahme hat einen benannten Verantwortlichen und einen realistischen Umsetzungstermin. Dies ist in der Maßnahmenliste des CAPA-Plans dokumentiert.
- ✅ `BLIND204-E003` (medium) — gefunden via evidence_substring (Score 1.0): Im Verpackungsprotokoll (document_02_verpackungsprotokoll_auszug.md, chunk_5d97cd759bbf4bc497b6cf84b67bad84_p1, Seite 1) wird ein Nachtragsvermerk dokumentiert: "Die Zeilen der Inprozesskontrolle vom 16.04.2026, 11:00 Uhr und 13:00 Uhr wurden zum Zeitpunkt der Kontrolle ausgefüllt, jedoch nicht gezeichnet. Der Nachtrag der Zeichnung erfolgte am 17.04.2026 um 07:35 Uhr durch Y. Brahms (YBR)." Dies belegt, dass Signaturen nicht zeitnah und plausibel zum Vorgang geleistet wurden, was gegen die Anforderung verstößt.
- ✅ `BLIND204-E004` (medium) — gefunden via evidence_fuzzy (Score 0.548): Die Dispositionsentscheidung jeder betroffenen Charge ist in der QA-Bewertung dokumentiert und mit den Batch Records (Verpackungsprotokoll) verknüpft. Die Sperrung und geplante Umverpackung sind begründet und nachvollziehbar.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `BLIND205-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die betroffenen Chargen sind vollständig erfasst: Vorprodukt Cetralvin 50 mg (C-24118), Folgeprodukt Dolvexan 10 mg (D-24007 und D-24008). Dies wird im Abweichungsbericht (DEV-2026-0417, Abschnitt 4) und in der QA-Bewertung (QA-BEW-2026-0193, Abschnitt 4) dokumentiert.
- ✅ `BLIND205-E002` (high) — gefunden via evidence_substring (Score 1.0): Umrechnung widersprüchlich: 113.190 µg entspricht 113,19 mg, angegeben ist 11,32 mg.
- ✅ `BLIND205-E003` (medium) — gefunden via evidence_substring (Score 1.0): Alle in den Vorgängen referenzierten Pflichtanhänge sind vorhanden. Der Abweichungsbericht (document_01_abweichungsbericht.md) listet die beigefügten Nachweise auf, darunter das analytische Protokoll (QC-2026-1188), den SOP-Auszug (SOP-RE-118), den CAPA-Plan (CAPA-2026-0117) und die QA-Bewertung (QA-BEW-2026-0193). Diese Dokumente sind als separate Chunks im Input enthalten.
- ✅ `BLIND205-E004` (low) — gefunden via evidence_substring (Score 1.0): Die SOP-RE-118 wurde am 01.03.2026 von Version 3.8 auf 4.2 aktualisiert. Der CAPA-Plan (CAPA-2026-0117) sieht eine Schulung der Technik und Schichtleitung auf die geänderte Checkliste (F-QM-020) bis zum 15.07.2026 vor. Die Abweichung DEV-2026-0417 trat jedoch bereits am 13.05.2026 auf, und die Reinigung wurde am 12.05.2026 nach der *alten* SOP-Version 3.8 durchgeführt. Es gibt keinen Nachweis, dass das Personal vor dem 12.05.2026 auf die aktualisierte SOP 4.2 geschult wurde. Die Pflicht zur wirksamen Schulung vor Ausführung der geänderten Tätigkeit ist somit verletzt.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `BLIND206-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die elektronischen Unterschriften enthalten Name, Datum, Zeit (sofern relevant) und Bedeutung. Die Datums- und Zeitangaben sind plausibel und konsistent mit dem Vorgang. Beispielsweise ist die QA-Freigabe durch Dr. Kai Lühmann am 16.06.2026 datiert, was nach der Erstellung des Abweichungsberichts (09.06.2026) und des CAPA-Plans (12.06.2026) liegt. Die Nachtragszeichnung im BMR (14:10 Uhr) ist ebenfalls zeitlich plausibel.
- ✅ `BLIND206-E002` (high) — gefunden via evidence_fuzzy (Score 0.545): Die Aufzeichnungen erfüllen die ALCOA+-Kriterien: Sie sind zurechenbar (signierte Dokumente), lesbar, zeitgleich (zeitnahe Dokumentation), original (keine nachträglichen Änderungen ohne Begründung), korrekt, vollständig, konsistent, dauerhaft und verfügbar. Beispielhaft sind das Einwaageprotokoll (BMR-T-26043) und der Abweichungsbericht (DEV-2026-0288) mit allen erforderlichen Unterschriften und Nachträgen versehen.
- ✅ `BLIND206-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen erfüllen die ALCOA+-Kriterien: Sie sind zurechenbar (signierte Dokumente), lesbar, zeitgleich (zeitnahe Dokumentation), original (keine nachträglichen Änderungen ohne Begründung), korrekt, vollständig, konsistent, dauerhaft und verfügbar. Beispielhaft sind das Einwaageprotokoll (BMR-T-26043) und der Abweichungsbericht (DEV-2026-0288) mit allen erforderlichen Unterschriften und Nachträgen versehen.
- ❌ `BLIND206-E004` (low) — übersehen: Die im Einwaageprotokoll ausgewiesene Gesamteinwaage von 62,244 kg stimmt nicht mit der Summe der Einzelpositionen von 62,144 kg überein.
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `BLIND207-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung ist erfüllt, da die Einstufung der Abweichung als geringfügig (Kategorie 3) durch eine nachvollziehbare Risikobewertung belegt ist. Der Abweichungsbericht (ABW-2026-0184) verweist in Abschnitt 7 auf die Kriterien der SOP-QC-118, Version 06, Abschnitt 4.3, die für Kurzzeitexkursionen gelten. Die QA-Bewertung (QAB-2026-0071) bestätigt in Abschnitt 4 die Klassifizierung und verweist auf die Einhaltung der Toleranzkriterien. Zudem liegt eine produktbezogene Bewertung (STB-2026-041) vor, die die Auswirkungen auf die Studie bewertet.
- ✅ `BLIND207-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Freigaben und Genehmigungen sind vor Abschluss dokumentiert. Die QA-Bewertung (document_05_qa_bewertung.md) enthält die signierte Freigabe durch die Leitung Qualitätsicherung (Petra Lindqvist) mit Datum 20.03.2026. Der CAPA-Plan (document_04_capa_plan.md) ist ebenfalls durch die QA genehmigt und dokumentiert.
- ✅ `BLIND207-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung ist erfüllt, da eine dokumentierte Bewertung der Auswirkung auf die Produktqualität und Patientensicherheit vorliegt. Im Abweichungsbericht (ABW-2026-0184) wird in Abschnitt 6 auf die produktbezogene Bewertung verwiesen, die im Bericht STB-2026-041 dokumentiert ist. Zudem listet der Abweichungsbericht in Abschnitt 2 alle betroffenen Chargen auf, die während der Temperaturexkursion im Klimaschrank KS-04 eingelagert waren. Die QA-Bewertung (QAB-2026-0071) bestätigt in Abschnitt 3 die Bewertung der eingelagerten Chargen und deren Fortführung ohne Auflage.
- ✅ `BLIND207-E004` (high) — gefunden via evidence_substring (Score 1.0): Die produktbezogene Bewertung (STB-2026-041) und die QA-Bewertung (QAB-2026-0071) erfassen alle im Klimaschrank KS-04 eingelagerten Chargen der Studie STB-24-017 (R6-2411, R6-2503, R6-2508). Es gibt keine Hinweise auf weitere betroffene Chargen oder fehlende Bewertungen.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `BLIND208-E001` (medium) — gefunden via evidence_substring (Score 1.0): Jede Maßnahme im CAPA-Plan (CAPA-2026-0117) hat einen benannten Verantwortlichen und einen realistischen Umsetzungstermin. Beispielhaft sind die Maßnahmen 1 bis 4 mit Verantwortlichen und Terminen aufgeführt.
- ✅ `BLIND208-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Signaturdaten in den Dokumenten enthalten Name, Datum und Zeit der Signatur sowie deren Bedeutung. Die zeitliche Plausibilität und Konsistenz mit dem Vorgang ist gegeben. Beispielhaft sind die Signaturen im Abweichungsbericht ABW-2026-0233: 'Erstellt | Yannick Trautwein (YT), Leiter Sterilabfüllung | Y. Trautwein | 22.04.2026' und im QA-Bewertungs- und Freigabevermerk QAB-2026-0098: 'Freigabe erteilt | Dr. Cornelia Haffner, Qualified Person | C. Haffner | 27.04.2026'. Die Daten sind zeitlich plausibel und widerspruchsfrei.
- ✅ `BLIND208-E003` (critical) — gefunden via evidence_substring (Score 1.0): Die Freigabeentscheidung für die Chargen DX-2604, DX-2605 und DX-2606 ist im QA-Bewertungsdokument (QAB-2026-0098) explizit begründet und mit den Batch Records verknüpft. Die Entscheidung verweist auf die Batch Records BR-DX-2604, BR-DX-2605 und BR-DX-2606.
- ✅ `BLIND208-E004` (high) — gefunden via evidence_fuzzy (Score 0.564): Die Anforderung verlangt, dass eine Charge nicht freigegeben werden darf, solange Abweichungsbewertung, Impact Assessment oder erforderliche QA-Freigabe nicht abgeschlossen sind. Im QA-Bewertungsdokument (document_05_qa_bewertung_freigabe) wird die Freigabe der Chargen DX-2604, DX-2605 und DX-2606 am 27.04.2026 dokumentiert. Allerdings ist der CAPA-Plan (document_04_capa_plan) zum Zeitpunkt der Freigabe noch nicht abgeschlossen, und die Wirksamkeitsprüfung der CAPA-Maßnahmen ist für den 30.06.2026 geplant. Zudem fehlt der Nachweis, dass die Abweichungsbewertung vollständig abgeschlossen war, da der CAPA-Plan und die Wirksamkeitsprüfung noch ausstehen.
- 🔁 9 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `BLIND209-E002` (high) — gefunden via evidence_substring (Score 1.0): Angegebener Anteil 2,8 % widerspricht der genannten Grundlage 14 von 320 (rechnerisch 4,4 %).
- ✅ `BLIND209-E004` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass QA-Freigaben und Genehmigungen vor Abschluss dokumentiert vorliegen. Im QA-Bewertungsdokument (QAB-2026-0447) ist die Genehmigung durch die Qualified Person (QP) und den Head of Quality mit Datum und Unterschrift dokumentiert. Zudem sind die Freigaben im Abweichungsbericht, CAPA-Plan und Change-Control-Vorgang durch QA signiert:
- QA-Bewertung: Genehmigt durch Dr. Ilja Berensen (IB) am 19.03.2026.
- Abweichungsbericht: Geprüft durch QA Compliance (Dr. Marlene Aschbacher, MA) am 18.03.2026.
- CAPA-Plan: Genehmigt durch Head of Quality (Dr. Ilja Berensen, IB) am 19.03.2026.
- Change-Control: Freigabe zur Implementierung durch QA (Dr. M. Aschbacher, MA) am 11.03.2026.

Alle Freigaben sind somit vor Abschluss der jeweiligen Vorgänge dokumentiert.
- ❌ `BLIND209-E001` (high) — übersehen: Der im BMR-Auszug dokumentierte IPC-Einzelwert von 2,281 ml (Messpunkt 07) überschreitet die in DEV-2026-0447 zitierte Obergrenze von NMT 2.266 ml aus PS-4471-03; die Überschreitung wurde weder im Chargenprotokoll noch in der QA-Bewertung als solche erkannt, die QA-Bewertung bestätigt stattdessen die Einhaltung sämtlicher Grenzen.
- ❌ `BLIND209-E003` (medium) — übersehen: Die auf dem Lieferantenzertifikat gezeichnete Wareneingangsprüfung vom 02.03.2026 liegt zwei Tage vor dem im BMR-Auszug dokumentierten Wareneingang des Loses AMP-9042-B am 04.03.2026.
- ❌ `BLIND209-E005` (medium) — übersehen: In der Maßnahmenliste des Change Control CC-2026-181 fehlt für Maßnahme 3 (Wirksamkeitsprüfung) der Termin, während für alle übrigen Maßnahmen Termine ausgewiesen sind.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 13 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `BLIND210-E001` (critical) — gefunden via evidence_fuzzy (Score 0.44): Die Schulung des betroffenen Personals auf die geänderte SOP-PR-233 (Version 06) ist durch den Schulungsnachweis TR-2026-0188 belegt. Die Schulung umfasste eine Lernerfolgskontrolle mit Bestehensgrenze, und alle Teilnehmer haben den Test bestanden. Die Schulung erfolgte vor dem Ersteinsatz der geänderten SOP.
- ✅ `BLIND210-E003` (high) — gefunden via evidence_substring (Score 1.0): Die QA-Bewertung (document_06_qa_bewertung.md, chunk_8aa3824ea9884100aebc10f8135b3cd3_p1, page 1) listet nur die Chargen KF-26-3301, KF-26-3302 und KF-26-3304 auf, nicht jedoch KF-26-3303. Der Abweichungsbericht (document_01_abweichungsbericht.md, chunk_1bdd678e13c04e008ff8a11ebf893395_p1, page 1) nennt jedoch alle vier Chargen (KF-26-3301 bis KF-26-3304) als betroffen. Die Charge KF-26-3303 fehlt in der QA-Bewertung, obwohl sie im Abweichungsbericht als betroffen aufgeführt ist. Dies stellt einen Verstoß dar, da nicht alle betroffenen Chargen in der Bewertung erfasst wurden.
- ❌ `BLIND210-E002` (medium) — übersehen: Im CAPA-Plan CAPA-2026-0179 fehlt für die Korrekturmaßnahme K3 der Termin, während alle übrigen Maßnahmen des Plans terminiert sind.
- ❌ `BLIND210-E004` (medium) — übersehen: Die in der QA-Bewertung genannte Genehmigung des CAPA-Plans am 24.04.2026 widerspricht dem CAPA-Plan selbst, der erst am 26.04.2026 erstellt und am 29.04.2026 genehmigt wurde.
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
