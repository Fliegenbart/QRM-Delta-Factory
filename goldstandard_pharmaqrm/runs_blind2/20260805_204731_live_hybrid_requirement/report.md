# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid` | Engine: `requirement`
- Zeitpunkt: 2026-08-05T20:47:31+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 21 von 38 versteckten Fehlern gefunden (55%)
- **In Prüfmappe sichtbar:** 21 von 38 versteckten Fehlern (55%)
- **Spezifität (Decoys):** 41 von 42 Decoys korrekt nicht beanstandet (98%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 40 von 142 (28%) — 20 als Treffer gewertet, 20 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 102 von 142 (72%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 14.2 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 60 von 142 Findings mit verifiziertem Zitat (42%)

## Qualitätsmetriken

- Must-detect Recall: `0.5526`
- Wiederholungen: `20` (Redundanzrate `0.5`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `6/11/4`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 71 | 133,643 | 32,966 | 166,609 |
| mistral | 141 | 1,289,004 | 399,186 | 1,688,190 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 20 | 5 | 12 | 3/3 | 3/3 | 0/5 | - |
| CASE_02 | completed_with_model_failures | 0 | 15 | 1 | 13 | 1/3 | 1/3 | 0/5 | - |
| CASE_03 | completed_with_model_failures | 0 | 19 | 0 | 18 | 1/3 | 1/3 | 0/4 | - |
| CASE_04 | completed_with_model_failures | 0 | 11 | 3 | 6 | 2/4 | 2/4 | 0/4 | - |
| CASE_05 | completed | 0 | 15 | 0 | 12 | 3/4 | 3/4 | 0/3 | - |
| CASE_06 | completed_with_model_failures | 0 | 12 | 0 | 12 | 0/4 | 0/4 | 0/4 | - |
| CASE_07 | completed_with_model_failures | 0 | 17 | 2 | 11 | 4/4 | 4/4 | 0/5 | - |
| CASE_08 | completed_with_model_failures | 0 | 13 | 7 | 3 | 4/4 | 4/4 | 0/4 | - |
| CASE_09 | completed_with_model_failures | 0 | 11 | 0 | 10 | 1/5 | 1/5 | 0/4 | - |
| CASE_10 | completed_with_model_failures | 0 | 9 | 2 | 5 | 2/4 | 2/4 | 1/4 | - |

## Modellausfälle

- **ProviderCallError** (8×): mistral provider output was truncated
  - betroffen: CASE_02/extract[doc_bc1eebfc47b947f0a7e7a9501616f778]:21, CASE_03/extract[doc_0e534504767340b8b743a2ef2e8c64c5]:21, CASE_04/extract[doc_fc26ca13030344ae9f1e98fe8d1209b6]:19, CASE_06/extract[doc_b44ff10b486641968565421b296404b1]:14, CASE_07/extract[doc_2ca2d3349a3047c1933cef894a0630b2]:27, CASE_08/extract[doc_630620641ce64076a8f7420f6efd3dda]:18
  - … und 2 weitere
- **ProviderStructuredOutputError** (1×): 4 validation errors for StructuredEvidence
action_items.0.description
  Extra inputs are not permitted [type=extra_forbidden, input_value='Gebinde M-26011 aus W
  - betroffen: CASE_06/extract[doc_c598add21f8e42e59d7075bb2b1d88de]:15
- **ProviderCallError** (1×): mistral provider returned invalid JSON
  - betroffen: CASE_09/assess:2
- **ProviderStructuredOutputError** (1×): 1 validation error for RequirementGroupOutput
verdicts.0.evidence
  Input should be a valid list [type=list_type, input_value=None, input_type=NoneType]
    For
  - betroffen: CASE_10/assess:4

### CASE_01

- ✅ `BLIND201-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen erfüllen das ALCOA+-Kriterium der Vollständigkeit nicht. Im BMR-Auszug (BMR-CT-24118, Abschnitt 7.1 bis 7.6) fehlt die Uhrzeit für Schritt 7.3 (Abschluss Filtration) zum Zeitpunkt der Erfassung. Die nachträgliche Ergänzung am 15.03.2026 (Nachtrag vom 15.03.2026) bestätigt, dass die Originalaufzeichnung unvollständig war. Dies stellt einen Verstoß gegen die Vollständigkeit und zeitgleiche Dokumentation dar.
- ✅ `BLIND201-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Bewertung (document_04_qa_bewertung.md) erwähnt eine Audit-Trail-Auswertung des Integritätstestgeräts IT-04 für den Zeitraum 14.03.2026, 07:00–14:00 Uhr, jedoch fehlt der Nachweis eines dokumentierten Audit-Trail-Reviews. Es wird lediglich behauptet: 'es ergaben sich keine weiteren Auffälligkeiten'. Primärevidenz (z. B. ein signierter Review-Bericht oder ein Audit-Trail-Auszug) ist nicht vorhanden. Ohne diesen Nachweis kann nicht bestätigt werden, dass ein regelhafter, risikobasierter Audit-Trail-Review durchgeführt wurde.
- ✅ `BLIND201-E003` (medium) — gefunden via evidence_fuzzy (Score 0.411): Die Charge CT-24118 wurde erst nach Abschluss der Abweichungsbewertung, des Impact Assessments und der QA-Freigabe gesperrt. Die QA-Bewertung (document_04_qa_bewertung.md, chunk_d1a02fb851844fc29136235ca23e5c6b_p1, Seite 1) bestätigt, dass die Bewertung abgeschlossen und die Charge nicht freigegeben wurde. Der Abweichungsbericht (document_01_abweichungsbericht.md, chunk_bf577b1e9c274b2c8e5e2d3f46ec55a7_p1, Seite 1) dokumentiert den Zeitpunkt der Chargensperrung (14.03.2026, 12:20 Uhr), der nach der Erfassung der Abweichung (14.03.2026, 14:30 Uhr) und vor Abschluss der Bewertung (19.03.2026) liegt.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `BLIND202-E002` (medium) — gefunden via evidence_fuzzy (Score 0.498): Die Anforderung verlangt, dass kritische Prozessparameter innerhalb der spezifizierten Grenzen liegen. Im IPC-Protokoll (chunk_bc1eebfc47b947f0a7e7a9501616f778_p1, Abschnitt 9.3) wurde der Mittelwert der Tablettenmasse bei IPC-05 mit 431,2 mg gemessen, was die Obergrenze von NMT 428,4 mg überschreitet. Dies ist ein Verstoß gegen die Spezifikation, auch wenn der Pressvorgang gestoppt und die betroffene Teilmenge ausgeschleust wurde. Die Überschreitung ist im Abweichungsbericht (chunk_60df1e0c1c1c4d489262f5d58aebb1bb_p1, Abschnitt 3) und in der QA-Bewertung (chunk_c0f39c045c7f49c38bf2578bf066ce0b_p1, Abschnitt 3) bestätigt.
- ❌ `BLIND202-E001` (high) — übersehen: Der bei IPC-04 dokumentierte Maximalwert der Einzelmasse von 442,6 mg überschreitet die im selben Dokument festgelegte Obergrenze von 441,0 mg (Sollwert 420,0 mg, Toleranz 5,0 Prozent), der Prüfpunkt ist gleichwohl mit i.O. bewertet.
- ❌ `BLIND202-E003` (medium) — übersehen: Im CAPA-Plan ist bei Maßnahme 3 das Pflichtfeld Verantwortlicher mit siehe oben statt mit einer namentlich benannten Person belegt; der Verweis ist wegen der unterschiedlichen Verantwortlichen der übrigen Maßnahmen nicht eindeutig auflösbar.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 13 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `BLIND203-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die manuellen Eingriffe (Nachregelung der Vakuumsteuerung nach Alarm PT-01) sind im Batch Manufacturing Record (BMR) und Abweichungsbericht dokumentiert, zeitnah gezeichnet und damit autorisiert. Es gibt keine Hinweise auf unautorisierte oder nicht nachvollziehbare Override-Aktionen. Die Zugriffsrechte sind rollenbasiert (z. B. Schichtleiterin K. Ohlendorf) und im BMR sowie Abweichungsbericht explizit benannt.
- ❌ `BLIND203-E001` (high) — übersehen: Die Stellflächentemperatur unterschreitet mit -23.4 °C am 13.03.2026 um 06:00 Uhr die in derselben Aufzeichnung festgelegte Untergrenze von -22,0 °C; diese Grenzwertverletzung ist weder im Abweichungsbericht noch in der Bewertung der Qualitätseinheit erfasst.
- ❌ `BLIND203-E003` (medium) — übersehen: Die Bewertung der Qualitätseinheit behauptet eine vollständige Sichtung des Audit Trails der Anlage LYO-03, ohne dass ein Auszug, eine Checkliste oder ein sonstiger Nachweis der Sichtung im Paket vorhanden oder in der Bewertungsgrundlage aufgeführt ist.
- ℹ️ 18 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `BLIND204-E002` (high) — gefunden via evidence_substring (Score 1.0): Jede CAPA-Maßnahme im CAPA-Plan (document_03_capa_plan.md) hat einen benannten Verantwortlichen und einen realistischen Umsetzungstermin.
- ✅ `BLIND204-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen erfüllen das ALCOA+-Kriterium der Vollständigkeit nicht. Im Verpackungsprotokoll (Auszug) wird dokumentiert, dass die Inprozesskontrollen vom 16.04.2026 um 11:00 Uhr und 13:00 Uhr zum Zeitpunkt der Kontrolle ausgefüllt, aber nicht gezeichnet wurden. Der Nachtrag der Zeichnung erfolgte erst am 17.04.2026, was gegen die Anforderung zeitgleicher Dokumentation verstößt (document_02_verpackungsprotokoll_auszug.md, Chunk chunk_fc26ca13030344ae9f1e98fe8d1209b6_p1, Seite 1, Abschnitt 4.6: 'Die Zeilen der Inprozesskontrolle vom 16.04.2026, 11:00 Uhr und 13:00 Uhr wurden zum Zeitpunkt der Kontrolle ausgefüllt, jedoch nicht gezeichnet. Der Nachtrag der Zeichnung erfolgte am 17.04.2026 um 07:35 Uhr durch Y. Brahms (YBR); Grund: Abbruch der Dokumentation wegen der Endkontrolle im Palettierbereich.').
- ❌ `BLIND204-E001` (critical) — übersehen: Die Charge RM-2574-A ist im Abweichungsbericht als betroffen und teilweise ausgeliefert ausgewiesen, fehlt aber vollständig in der Chargen-Impact-Übersicht, in der Summenzeile und im Verteiler der informierten Empfänger.
- ❌ `BLIND204-E004` (medium) — übersehen: Zwischen der Feststellung der als kritisch eingestuften Abweichung am 16.04.2026 um 14:20 Uhr und der formellen Meldung an die Qualitätseinheit am 18.04.2026 um 08:40 Uhr liegen rund 42 Stunden; die nach SOP QM-DEV-002, Version 8.0, geltende Meldefrist von 24 Stunden ist damit überschritten, ohne dass dies in den Unterlagen behandelt wird.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `BLIND205-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Auswirkungsbewertung der Abweichung auf Produktqualität und Patientensicherheit ist in der QA-Bewertung (document_05_qa_bewertung.md) dokumentiert. Es werden alle potenziell betroffenen Chargen (C-24118, D-24007, D-24008) bewertet und eine Freigabeentscheidung getroffen. Der rechnerische Übertrag auf die Folgecharge wird explizit bewertet und liegt deutlich unter dem internen Orientierungswert.
- ✅ `BLIND205-E003` (medium) — gefunden via evidence_fuzzy (Score 0.423): Die elektronischen Unterschriften in den Dokumenten enthalten Name, Kürzel, Datum und Bedeutung der Signatur. Die Datumsangaben sind zeitlich plausibel und konsistent mit dem Vorgang. Beispielsweise sind die Unterschriften der QA-Bewertung (21.05.2026) nach der analytischen Freigabe (14.05.2026) und der Erstellung des Abweichungsberichts (14.05.2026) datiert. Es gibt keine in der Zukunft liegenden oder widersprüchlichen Signaturdaten.
- ✅ `BLIND205-E004` (low) — gefunden via evidence_substring (Score 1.0): Die SOP-RE-118 wurde am 01.03.2026 aktualisiert (Version 4.2), und der Vorfall ereignete sich am 13.05.2026. Im CAPA-Plan (CAPA-2026-0117) wird zwar eine Schulung der Technik und Schichtleitung auf die geänderte Checkliste F-QM-020 geplant, jedoch gibt es keinen Nachweis, dass das betroffene Personal (z. B. S. Brandhoff, der die Reinigung durchführte) vor dem Vorfall wirksam auf die aktualisierte SOP-RE-118 geschult wurde. Die Schulung ist erst für den 15.07.2026 terminiert, was nach dem Vorfall liegt.
- ❌ `BLIND205-E002` (high) — übersehen: Die Umrechnung von 113.190 µg in 11,32 mg ist um eine Zehnerpotenz falsch; der rechnerische Übertrag beträgt 0,45 mg/kg statt 0,045 mg/kg, und die darauf gestützte Aussage der QA-Bewertung zum Abstand vom Orientierungswert ist damit unzutreffend.
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ❌ `BLIND206-E001` (critical) — übersehen: Die Lactose-Charge WE-26-0731 wurde am 09.06.2026 eingewogen, obwohl der Freigabestatus laut ERP-Auszug erst am 10.06.2026 um 11:24 Uhr erteilt wurde; damit wurde nicht freigegebenes Ausgangsmaterial verwendet.
- ❌ `BLIND206-E002` (high) — übersehen: Für den 09.06.2026, 06:49 Uhr, ist E. Sandvoss gleichzeitig als Zweitprüfer in der Wägekabine W-104 und als buchender Benutzer am Lagerterminal L-2-14 dokumentiert; die beiden Zeitstempel sind nicht miteinander vereinbar.
- ❌ `BLIND206-E003` (high) — übersehen: In Abschnitt 3.2 des Einwaageprotokolls fehlt für Position 5 das Namenskürzel der Vier-Augen-Prüfung; es ist ausschließlich Datum und Uhrzeit eingetragen, sodass die Zweitkontrolle dieser Einwaage nicht nachweisbar ist.
- ❌ `BLIND206-E004` (low) — übersehen: Die im Einwaageprotokoll ausgewiesene Gesamteinwaage von 62,244 kg stimmt nicht mit der Summe der Einzelpositionen von 62,144 kg überein.
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `BLIND207-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung ist erfüllt, da die Aufzeichnungen die ALCOA+-Kriterien erfüllen. Die Originalaufzeichnungen sind zurechenbar, lesbar, zeitgleich, original und korrekt sowie vollständig, konsistent, dauerhaft und verfügbar. Der Logbuchauszug (LB-KS04-2026-03) enthält den vollständigen Messwertverlauf der Exkursion mit Zeitstempeln und verantwortlichen Personen. Nachträge sind als solche gekennzeichnet und gegengezeichnet. Der Abweichungsbericht und die QA-Bewertung verweisen auf die vollständigen Originaldaten.
- ✅ `BLIND207-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Freigaben und Genehmigungen liegen dokumentiert vor. Die QA-Bewertung (QAB-2026-0071) wurde am 20.03.2026 von Silke Brandhoff (QA Manager) bewertet und von Petra Lindqvist (Leitung Qualitätssicherung) freigegeben. Der CAPA-Plan (CAPA-2026-0092) wurde am 20.03.2026 von Petra Lindqvist genehmigt. Beide Dokumente enthalten die erforderlichen Signaturen mit Datum.
- ✅ `BLIND207-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung ist erfüllt, da eine dokumentierte Bewertung der Auswirkung auf die Produktqualität und Patientensicherheit vorliegt. Im Abweichungsbericht (ABW-2026-0184) wird in Abschnitt 6 auf die produktbezogene Bewertung verwiesen, die im Bericht STB-2026-041 dokumentiert ist. Zudem listet der Abweichungsbericht in Abschnitt 2 alle betroffenen Chargen auf. Die QA-Bewertung (QAB-2026-0071) bestätigt in Abschnitt 3 die Bewertung der eingelagerten Chargen und deren Fortführung ohne Auflage.
- ✅ `BLIND207-E004` (high) — gefunden via evidence_substring (Score 1.0): Die QA-Bewertung (QAB-2026-0071) und der Abweichungsbericht (ABW-2026-0184) erfassen alle im Klimaschrank KS-04 eingelagerten Chargen (R6-2411, R6-2503, R6-2508). Die produktbezogene Bewertung (STB-2026-041) bezieht sich auf diese Chargen. Es gibt keine Hinweise auf fehlende Chargen oder unvollständige Erfassung.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 11 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `BLIND208-E001` (medium) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen zur Abweichung und deren Bewertung erfüllen die ALCOA+-Kriterien. Die Rohdaten der kontinuierlichen Partikelmessung wurden am 21.04.2026 gesichert (Sofortmaßnahme S1 im Abweichungsbericht) und sind als Anlage im Prüfbericht des Umgebungsmonitorings (UM-2026-0451) dokumentiert. Die Audit-Trail-Auswertung des Monitoringsystems EM-Sentinel zeigt keine nachträglichen Änderungen an Messdaten. Alle relevanten Dokumente sind signiert und zeitnah erstellt.
- ✅ `BLIND208-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Auswirkungsbewertung der Abweichung auf Produktqualität und Patientensicherheit ist im QA-Bewertungs- und Freigabevermerk (QAB-2026-0098) dokumentiert. Es werden alle potenziell betroffenen Chargen (DX-2604, DX-2605, DX-2606) aufgeführt und bewertet. Die Bewertung umfasst die mikrobiologischen Ergebnisse, die Eingriffsdokumentation und die Luftführung am betroffenen Punkt. Die Freigabeentscheidung basiert auf dieser Bewertung.
- ✅ `BLIND208-E003` (critical) — gefunden via evidence_substring (Score 1.0): Die Freigabeentscheidung für die Chargen DX-2604, DX-2605 und DX-2606 ist im QA-Bewertungsdokument (document_05_qa_bewertung_freigabe.md, chunk_24b4a43cc3034a37a278aeda10274808_p1) begründet und mit den Batch Records verknüpft (Abschnitt 2 listet die Batch Records auf). Die Dispositionsentscheidung ist somit nachvollziehbar dokumentiert.
- ✅ `BLIND208-E004` (high) — gefunden via evidence_substring (Score 1.0): Die Auswirkungsbewertung der Abweichung auf Produktqualität und Patientensicherheit ist im QA-Bewertungs- und Freigabevermerk (QAB-2026-0098) dokumentiert. Es werden alle potenziell betroffenen Chargen (DX-2604, DX-2605, DX-2606) aufgeführt und bewertet. Die Bewertung umfasst die mikrobiologischen Ergebnisse, die Eingriffsdokumentation und die Luftführung am betroffenen Punkt. Die Freigabeentscheidung basiert auf dieser Bewertung.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 3 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `BLIND209-E004` (critical) — gefunden via evidence_fuzzy (Score 0.591): Die QA-Freigaben und Genehmigungen sind vor Abschluss dokumentiert. Beispielhaft wird die QA-Bewertung (Chunk 'chunk_febb0bacfdf549fa95befa3a18974aeb_p1') zitiert, die die Genehmigung durch die Qualified Person (Dr. Ilja Berensen) am 19.03.2026 bestätigt. Zudem sind die Unterschriften im Abweichungsbericht (Chunk 'chunk_c74e6025b1234aa3968d2faf4428ff5c_p1') und im CAPA-Plan (Chunk 'chunk_d2017b6e51324dfbb88af623db20cacc_p1') vollständig und zeitnah dokumentiert.
- ❌ `BLIND209-E001` (high) — übersehen: Der im BMR-Auszug dokumentierte IPC-Einzelwert von 2,281 ml (Messpunkt 07) überschreitet die in DEV-2026-0447 zitierte Obergrenze von NMT 2.266 ml aus PS-4471-03; die Überschreitung wurde weder im Chargenprotokoll noch in der QA-Bewertung als solche erkannt, die QA-Bewertung bestätigt stattdessen die Einhaltung sämtlicher Grenzen.
- ❌ `BLIND209-E002` (high) — übersehen: Die im Abweichungsbericht angegebene Leckrate von 2,8 Prozent ist rechnerisch falsch; 14 von 320 Ampullen ergeben 4,4 Prozent und damit eine Überschreitung des in der QA-Bewertung genannten Aktionslimits von 3,0 Prozent, auf das die Entscheidung gegen eine Ausweitung der Prüfung gestützt wird.
- ❌ `BLIND209-E003` (medium) — übersehen: Die auf dem Lieferantenzertifikat gezeichnete Wareneingangsprüfung vom 02.03.2026 liegt zwei Tage vor dem im BMR-Auszug dokumentierten Wareneingang des Loses AMP-9042-B am 04.03.2026.
- ❌ `BLIND209-E005` (medium) — übersehen: In der Maßnahmenliste des Change Control CC-2026-181 fehlt für Maßnahme 3 (Wirksamkeitsprüfung) der Termin, während für alle übrigen Maßnahmen Termine ausgewiesen sind.
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `BLIND210-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung ist erfüllt, da die Schulung des betroffenen Personals auf die geänderte SOP-PR-233, Version 06, vor der Ausführung der geänderten Tätigkeit (Herstellung der Chargen KF-26-3301 bis KF-26-3304) durchgeführt und dokumentiert wurde. Der Schulungsnachweis TR-2026-0188 belegt die Durchführung der Schulung mit Lernerfolgskontrolle (Bestehensgrenze 75 %), und alle Teilnehmer haben bestanden. Die Schulung erfolgte vor dem Ersteinsatz der geänderten SOP.
- ✅ `BLIND210-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Auswirkungsbewertung der Abweichung auf Produktqualität und Patientensicherheit ist dokumentiert. Alle potenziell betroffenen Chargen (KF-26-3301 bis KF-26-3304) wurden identifiziert und bewertet. Die QA-Bewertung bestätigt, dass keine Beeinträchtigung der Produktqualität oder Patientensicherheit vorliegt.
- ❌ `BLIND210-E002` (medium) — übersehen: Im CAPA-Plan CAPA-2026-0179 fehlt für die Korrekturmaßnahme K3 der Termin, während alle übrigen Maßnahmen des Plans terminiert sind.
- ❌ `BLIND210-E004` (medium) — übersehen: Die in der QA-Bewertung genannte Genehmigung des CAPA-Plans am 24.04.2026 widerspricht dem CAPA-Plan selbst, der erst am 26.04.2026 erstellt und am 29.04.2026 genehmigt wurde.
- ⚠️ Decoy `BLIND210-D001` fälschlich beanstandet: Die Auswirkungsbewertung der Abweichung auf Produktqualität und Patientensicherheit ist dokumentiert. Alle potenziell betroffenen Chargen (KF-26-3301 bis KF-26-3304) wurden identifiziert und bewertet. Die QA-Bewertung bestätigt, dass keine Beeinträchtigung der Produktqualität oder Patientensicherheit vorliegt.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
