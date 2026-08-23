# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `mixed` | Engine: `requirement`
- Zeitpunkt: 2026-08-22T22:16:20+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Hetzner-Modell: `-`

## Gesamtergebnis

- **Sensitivität:** 22 von 25 versteckten Fehlern gefunden (88%)
- **In Prüfmappe sichtbar:** 22 von 25 versteckten Fehlern (88%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 77 von 180 (43%) — 21 als Treffer gewertet, 56 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 103 von 180 (57%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 18.0 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 103 von 180 Findings mit verifiziertem Zitat (57%)

## Qualitätsmetriken

- Must-detect Recall: `0.88`
- Wiederholungen: `56` (Redundanzrate `0.7273`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `9/5/8`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 164 | 1,086,660 | 238,555 | 1,325,215 |
| openai | 119 | 81,378 | 15,728 | 97,106 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 21 | 3 | 16 | 2/2 | 2/2 | 0/1 | - |
| CASE_02 | completed_with_model_failures | 0 | 15 | 10 | 3 | 2/2 | 2/2 | 0/1 | - |
| CASE_03 | completed | 0 | 22 | 4 | 16 | 2/2 | 2/2 | 0/2 | - |
| CASE_04 | completed | 0 | 20 | 13 | 4 | 3/3 | 3/3 | 0/1 | - |
| CASE_05 | completed_with_model_failures | 0 | 17 | 10 | 5 | 3/3 | 3/3 | 0/1 | - |
| CASE_06 | completed_with_model_failures | 0 | 2 | 0 | 1 | 1/2 | 1/2 | 0/1 | - |
| CASE_07 | completed | 0 | 22 | 0 | 22 | 0/2 | 0/2 | 0/1 | - |
| CASE_08 | completed | 0 | 21 | 3 | 15 | 3/3 | 3/3 | 0/1 | - |
| CASE_09 | completed_with_model_failures | 0 | 23 | 6 | 14 | 3/3 | 3/3 | 0/1 | - |
| CASE_10 | completed_with_model_failures | 0 | 17 | 7 | 7 | 3/3 | 3/3 | 0/1 | - |

## Modellausfälle

- **ProviderStructuredOutputError** (7×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...n      }\n    ]\n
  - betroffen: CASE_02/assess:6, CASE_05/assess:6, CASE_05/assess:7, CASE_06/assess:2, CASE_06/assess:3, CASE_06/assess:5
  - … und 1 weitere
- **ProviderStructuredOutputError** (4×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...ty": "critical"\n
  - betroffen: CASE_02/assess:7, CASE_06/assess:4, CASE_06/assess:7, CASE_10/assess:7
- **ProviderStructuredOutputError** (3×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...verity": "high"\n
  - betroffen: CASE_05/assess:1, CASE_06/assess:1, CASE_09/assess:3
- **ProviderStructuredOutputError** (3×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement... "evidence": []\n
  - betroffen: CASE_06/assess:0, CASE_10/assess:5, CASE_10/assess:6
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Visuel...erage_current_state"]}]
  - betroffen: CASE_02/extract[doc_4ca720aa301e42eba525b39d690c0580:felder]:29
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Re-Val...pact_and_validation"]}]
  - betroffen: CASE_05/extract[doc_d51e20526e8b4d549f3a34c2b3a97532:felder]:23
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Freiga...h_disposition_trace"]}]
  - betroffen: CASE_06/extract[doc_f530e2646abd45a5990d43eebafdca52:felder]:16
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "description...stabil."\n    }\n  }\n]
  - betroffen: CASE_09/extract[doc_4faa5fad08ed465ead2fa192ac48ea79:felder]:32
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
measurements
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "parameter":...ücken."\n    }\n 
  - betroffen: CASE_09/extract[doc_4faa5fad08ed465ead2fa192ac48ea79:werte]:33

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Charge XYL-2026-004A wurde am 25.03.2026 freigegeben (QA-RELEASE-XYL-004A). Der Abweichungsbericht DEV-2026-891 wurde zwar am 12.03.2026 erfasst, die QA-Prüfung durch Dr. Anna Klar ist jedoch mit dem Datum 14.12.2026 signiert – also nach der Chargenfreigabe vom 25.03.2026. Dies bedeutet, dass die Charge freigegeben wurde, bevor die QA-Prüfung des Abweichungsberichts abgeschlossen war. Dies stellt einen kritischen Verstoß gegen das Prinzip dar, dass keine Freigabe vor abgeschlossener Bewertung erfolgen darf.
- ✅ `ERR_01_02` (high) — gefunden via evidence_fuzzy (Score 0.437): Die Qualitätssicherungs-Freigabe (QA-RELEASE-XYL-004A) enthält eine Dispositionsentscheidung (Freigabe zur Verpackung), verknüpft diese jedoch nicht explizit mit dem Chargenprotokoll (Batch Record). Eine formale Verknüpfung oder Referenz auf den Batch Record fehlt im Freigabevermerk. Die Begründung stützt sich ausschließlich auf visuelle Homogenität, ohne Verweis auf konkrete Batch-Record-Einträge oder Messwerte. Damit ist die geforderte Verknüpfung mit dem Batch Record nicht nachvollziehbar dokumentiert.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 16 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Im Batch Record findet sich eine nachträgliche Korrektur der Ausbeute von 96,47 % auf 98,1 % mit der Begründung, der Wiegebegleitschein sei unvollständig gewesen. Diese Korrektur stellt eine Abweichung dar, die einer dokumentierten Bewertung bedarf. Das Freigabezertifikat vom 10.04.2026 erwähnt diese Korrektur und die damit verbundene Abweichungsbewertung mit keinem Wort. Es ist nicht belegt, dass eine abgeschlossene Abweichungsbewertung oder ein Impact Assessment vor der Freigabe vorlag. Die Charge wurde dennoch freigegeben, was einen Verstoß gegen das Verbot der Freigabe vor abgeschlossener Bewertung darstellt.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_fuzzy (Score 0.496): Die ursprünglich berechnete Ausbeute von 96,47 % liegt unterhalb der Spezifikationsgrenze von 98,0 %. Dieser Befund hätte eine formelle Risikobewertung und Schweregradeinstufung erfordert. Stattdessen wurde der Wert korrigiert und die Charge ohne dokumentierte Risikobewertung oder stützende Labordaten freigegeben. Die Qualitätsfreigabe enthält lediglich die pauschale Aussage, die Ausbeute entspreche der Vorgabe, ohne auf die Abweichung oder deren Bewertung einzugehen. Physikalisch-chemische oder labortechnische Daten zur Stützung der Einstufung als geringfügig fehlen vollständig.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 3 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Unterlagen enthalten keinen Hinweis auf manuelle Override- oder Admin-Eingriffe in GxP-Systeme. Es gibt jedoch eine zeitliche Inkonsistenz im Deviation Report: Der Eintritt des Mitarbeiters in Raum R-202 ist um 14:35 Uhr protokolliert, der Peak-Zeitstempel liegt jedoch bei 14:15 Uhr – also 20 Minuten vor dem Eintritt. Diese Diskrepanz könnte auf eine Datenmanipulation, einen Systemfehler oder einen Eingabefehler hinweisen, was eine Prüfung der Zugriffskontrolle und des Audit Trails erfordern würde. Da keine weiteren Informationen vorliegen, ist eine abschließende Beurteilung nicht möglich.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan (document_03) referenziert explizit die SOP-QS-REIN-001, Version 2.0 (gültig vom 12.01.2018) als übergeordnete Richtlinie für die Umsetzung der Maßnahme. Diese SOP ist in den vorliegenden Dokumenten nicht enthalten und kann daher nicht auf Aktualität oder Vorhandensein geprüft werden. Das Fehlen dieses referenzierten Pflichtanhangs ist ein Befund.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 16 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Die Qualitätsbewertung in document_04 enthält lediglich eine pauschale Aussage, dass kein nennenswerter Substanzabbau erwartet wird, ohne eine strukturierte Auswirkungsbewertung auf Produktqualität und Patientensicherheit zu dokumentieren. Eine Chargenliste potenziell betroffener Chargen fehlt vollständig. Der Auslöser der Pflicht – die dokumentierte Temperaturüberschreitung – ist belegt.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan (CAPA-DEV-092) definiert als Maßnahme ein Re-Training für Operator J.K., enthält jedoch keinerlei Angaben zu einer geplanten oder dokumentierten Wirksamkeitsprüfung (Effectiveness Check). Ein Nachweis, dass nach Abschluss der Maßnahme deren Wirksamkeit überprüft wird, fehlt vollständig.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-P-2026-092 betrifft die Charge PAR-2026-H102. Eine Batch-Impact-Bewertung, die Vorgänger- und Folgechargen einschließt sowie eine Begründung der Chargenauswahl enthält, ist in keinem der vorliegenden Dokumente zu finden. Die QS-Chargenbewertung (document_04) beschränkt sich ausschließlich auf PAR-2026-H102 und nennt weder Vorgänger- noch Folgechargen.
- 🔁 13 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Validierungsnotiz VAL-NOTE-AT-442 referenziert explizit einen Anhang 4, der die exakten Beladungsmuster und maximal zulässigen Gesamtgewichte für Glaswaren enthält. Dieser Anhang 4 ist in den vorliegenden Dokumenten nicht enthalten und wurde nicht bereitgestellt. Da der Auslöser (die Referenz auf Anhang 4) belegt ist, der Anhang selbst jedoch fehlt, liegt ein Verstoß gegen die Vollständigkeit der Pflichtanhänge vor.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Dokumente enthalten weder eine Freigabeentscheidung noch eine abgeschlossene Abweichungsbewertung oder ein Impact Assessment für die Charge OXA-2026-088. Es kann daher weder bestätigt noch widerlegt werden, ob eine vorzeitige Freigabe stattgefunden hat. Angesichts des belegten Widerspruchs zwischen Personalnummer PNN-8812 und den im elektronischen Schleusensystem hinterlegten Initialen (A.S. statt P.M.) sowie dem Anwesenheitszeitpunkt besteht ein erhebliches ungeklärtes Qualitätsrisiko, das eine menschliche Prüfung erfordert.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Dokumente enthalten weder eine Freigabeentscheidung noch eine abgeschlossene Abweichungsbewertung oder ein Impact Assessment für die Charge OXA-2026-088. Es kann daher weder bestätigt noch widerlegt werden, ob eine vorzeitige Freigabe stattgefunden hat. Angesichts des belegten Widerspruchs zwischen Personalnummer PNN-8812 und den im elektronischen Schleusensystem hinterlegten Initialen (A.S. statt P.M.) sowie dem Anwesenheitszeitpunkt besteht ein erhebliches ungeklärtes Qualitätsrisiko, das eine menschliche Prüfung erfordert.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_02` (critical) — gefunden via evidence_substring (Score 1.0): Der interne Prüfplan Prüf-Spez-API-04 definiert für Amoxicillin Trihydrat ein Akzeptanzkriterium von 11,5 % bis 12,8 % Wassergehalt. Das hauseigene QC-Labor ermittelte einen Wassergehalt von 13,2 %, der diesen Grenzwert überschreitet. Trotz dieser offenen Abweichung (LAB-DEV-2026-031, Status: In Untersuchung) wurde der Rohstoff durch die QA-Freigabenotiz QA-REL-AMO-01 final für die Produktion autorisiert, wobei ausschließlich auf das Lieferantenzertifikat verwiesen wird. Dies stellt einen klaren Verstoß gegen die Anforderung dar, interne Akzeptanzkriterien vorrangig zu behandeln und eine Verletzung als Abweichung zu werten – auch wenn das Lieferantenzertifikat Konformität ausweist.
- ❌ `ERR_06_01` (high) — übersehen: Akzeptanzkriterium der internen Spezifikation wird durch das Lieferanten-Zertifikat verletzt.
- ℹ️ 1 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ❌ `ERR_07_01` (high) — übersehen: Yield-Unterschreitung wird fälschlicherweise als konform deklariert.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 22 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht stuft das Ereignis als 'isoliertes Einzelereignis ohne systematischen Charakter' ein. Diese Einstufung erfolgt ohne belastbare physikalisch-chemische oder labortechnische Daten. Das Chargenprotokoll belegt jedoch, dass es sich um das dritte gleichartige Werkzeugereignis an derselben Presse innerhalb von zwei Monaten handelt, was der Einstufung als Einzelereignis widerspricht. Stützende Labordaten zur Risikobewertung (z. B. Metallkontaminationsanalyse, Härteprüfung der Tabletten) fehlen vollständig. Eine Einstufung als geringfügig ohne solche Daten ist gemäß Anforderung unzulässig.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): Der Abweichungsbericht DEV-IBU-2026-112 beschränkt die Bewertung ausschließlich auf die aktuelle Charge IBU-2026-P03 und schließt einen Einfluss auf andere Chargen kategorisch aus. Das Logbuch der Anlage TAB-02 (document_02) belegt jedoch gleichartige Werkzeugschäden an den Vorgängerchargen IBU-2026-P01 (14.03.2026) und IBU-2026-P02 (18.04.2026). Eine Chargenliste mit Begründung der Chargenauswahl, die auch Vorgänger- und Folgechargen einschließt, fehlt vollständig. Die pauschale Ausschlussaussage im Abweichungsbericht ist angesichts der dokumentierten Wiederholungsereignisse nicht ausreichend begründet.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan CAPA-112-IBU sieht die Nachrüstung eines Inline-Metalldetektors sowie dessen Qualifizierung und Softwareintegration vor. Die terminierte Deadline für den 'Abschluss der gesamten Validierung' ist der 11.05.2026 – also einen Tag nach dem Vorfall vom 10.05.2026. Es ist offensichtlich, dass eine vollständige Beschaffung, Qualifizierung und Softwareintegration innerhalb eines Tages nicht realistisch durchführbar ist. Ein aktueller Validierungsbericht für das neue Equipment liegt nicht vor, und eine Übertragbarkeitsbegründung fehlt vollständig. Die Charge IBU-2026-P03 soll jedoch bereits freigegeben werden, ohne dass der validierte Zustand des geänderten Prozesses belegt ist.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 15 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-CEF-77 dokumentiert, dass der pH-Wert in Phase 3 der Fermentation Spitzenwerte von pH 7,85 erreichte, während die spezifizierte Obergrenze bei pH 7,40 liegt – eine klare Überschreitung um 0,45 pH-Einheiten über 6 Stunden. Zusätzlich zeigt der SCADA-Audit-Trail, dass ein Operator den Sollwert manuell von pH 7,20 auf pH 7,70 hochsetzte, was ebenfalls die Spezifikationsgrenze von pH 7,40 überschreitet. Trotz dieser Grenzwertverletzungen wurde die Aufarbeitung fortgesetzt. Der handschriftliche Batch Record vermerkt zudem 'Keine besonderen Vorkommnisse in der Schicht. Werte stabil.' – eine Aussage, die dem SCADA-Audit-Trail direkt widerspricht und auf eine unvollständige oder fehlerhafte Dokumentation hindeutet.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-CEF-77 dokumentiert eine pH-Drift bis pH 7,85 bei einer spezifizierten Obergrenze von pH 7,40 sowie eine ungeklärte Root Cause. Dennoch wurde die Aufarbeitung der Charge CEF-BIOR-2026-77 fortgesetzt, ohne dass eine abgeschlossene Abweichungsbewertung oder QA-Freigabeentscheidung belegt ist. Zusätzlich ist im Change-Control-Antrag CC-2026-104 das Unterschriftenfeld der Leitung Qualitätskontrolle leer, was eine fehlende QA-Freigabe belegt. Die Fortführung der Aufarbeitung vor Abschluss der Bewertung stellt einen kritischen Verstoß dar.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Der handschriftliche Batch Record enthält den Eintrag 'Keine besonderen Vorkommnisse in der Schicht. Werte stabil.' – obwohl im selben Zeitraum laut SCADA-Audit-Trail ein manueller Override des pH-Regelkreises stattfand und der pH-Wert die Spezifikationsgrenze erheblich überschritt. Diese Diskrepanz zwischen elektronischem Audit-Trail und handschriftlicher Aufzeichnung stellt einen schwerwiegenden Verstoß gegen das ALCOA+-Prinzip (korrekt, vollständig, konsistent) dar.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Eine abgeschlossene Grundursachenanalyse ist in keinem der Dokumente vorhanden. Der Laboranalyst bezeichnet den Befund als 'vermutlich temporären Ausreißer', ohne technische Ursachen (Equipment, Kalibrierung, Probenahme) dokumentiert ausgeschlossen zu haben. Der CAPA-Plan sieht lediglich ein Re-Testing vor, um einen Probenahmefehler zu verifizieren – eine vollständige Untersuchung mit Ausschluss technischer Ursachen fehlt.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan enthält zwar ein Zieldatum (16.05.2026), jedoch ist das Feld für den Maßnahmenverantwortlichen ausdrücklich als '[Kein Eintrag / Offen]' gekennzeichnet. Ein benannter Maßnahmenverantwortlicher fehlt damit vollständig. Dies ist ein dokumentierter Verstoß gegen die Anforderung.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die QA-Notiz (document_03) enthält eine Risikobewertung und erklärt, dass keine marktregulierenden Maßnahmen erforderlich seien, verknüpft diese Aussage jedoch weder mit einem Batch Record noch mit einer formalen, begründeten Dispositionsentscheidung. Ein Batch Record wird in keinem der Dokumente referenziert oder zitiert. Die Anforderung, die Freigabe- bzw. Dispositionsentscheidung mit den zugehörigen Batch Records zu verknüpfen, ist damit nicht erfüllt.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
