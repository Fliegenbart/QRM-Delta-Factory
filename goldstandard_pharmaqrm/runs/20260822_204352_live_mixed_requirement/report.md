# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `mixed` | Engine: `requirement`
- Zeitpunkt: 2026-08-22T20:43:52+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Hetzner-Modell: `-`

## Gesamtergebnis

- **Sensitivität:** 22 von 25 versteckten Fehlern gefunden (88%)
- **In Prüfmappe sichtbar:** 22 von 25 versteckten Fehlern (88%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 79 von 168 (47%) — 21 als Treffer gewertet, 58 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 89 von 168 (53%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 16.8 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 91 von 168 Findings mit verifiziertem Zitat (54%)

## Qualitätsmetriken

- Must-detect Recall: `0.88`
- Wiederholungen: `58` (Redundanzrate `0.7342`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `11/5/6`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 164 | 1,094,558 | 226,519 | 1,321,077 |
| openai | 112 | 77,440 | 15,052 | 92,492 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 20 | 6 | 12 | 2/2 | 2/2 | 0/1 | - |
| CASE_02 | completed_with_model_failures | 0 | 15 | 9 | 4 | 2/2 | 2/2 | 0/1 | - |
| CASE_03 | completed | 0 | 21 | 7 | 12 | 2/2 | 2/2 | 0/2 | - |
| CASE_04 | completed | 0 | 20 | 13 | 4 | 3/3 | 3/3 | 0/1 | - |
| CASE_05 | completed_with_model_failures | 0 | 12 | 6 | 4 | 3/3 | 3/3 | 0/1 | - |
| CASE_06 | completed_with_model_failures | 0 | 2 | 0 | 1 | 1/2 | 1/2 | 0/1 | - |
| CASE_07 | completed | 0 | 22 | 0 | 22 | 0/2 | 0/2 | 0/1 | - |
| CASE_08 | completed_with_model_failures | 0 | 21 | 4 | 14 | 3/3 | 3/3 | 0/1 | - |
| CASE_09 | completed_with_model_failures | 0 | 18 | 6 | 9 | 3/3 | 3/3 | 0/1 | - |
| CASE_10 | completed_with_model_failures | 0 | 17 | 7 | 7 | 3/3 | 3/3 | 0/1 | - |

## Modellausfälle

- **ProviderStructuredOutputError** (6×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...n      }\n    ]\n
  - betroffen: CASE_02/assess:7, CASE_05/assess:0, CASE_06/assess:2, CASE_08/assess:0, CASE_09/assess:2, CASE_09/assess:3
- **ProviderStructuredOutputError** (5×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...verity": "high"\n
  - betroffen: CASE_05/assess:1, CASE_05/assess:7, CASE_06/assess:1, CASE_06/assess:3, CASE_10/assess:5
- **ProviderStructuredOutputError** (3×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement..._support": null\n
  - betroffen: CASE_02/assess:6, CASE_05/assess:6, CASE_06/assess:7
- **ProviderStructuredOutputError** (2×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement... "evidence": []\n
  - betroffen: CASE_06/assess:0, CASE_06/assess:5
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Visuel...erage_current_state"]}]
  - betroffen: CASE_02/extract[doc_330142b17f45439aba4845416fcc2963:felder]:31
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Re-Val...pact_and_validation"]}]
  - betroffen: CASE_05/extract[doc_8e0024a9db914a3898d6fd00ce45c700:felder]:22
- **ProviderStructuredOutputError** (1×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...ty": "critical"\n
  - betroffen: CASE_06/assess:4
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Finale...e_before_assessment"]}]
  - betroffen: CASE_06/extract[doc_6c21141c9c4e46f8be39be99c2c4e113:felder]:16
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "description...stabil."\n    }\n  }\n]
  - betroffen: CASE_09/extract[doc_295159f988954cb283946097fde44604:felder]:22
- **ProviderStructuredOutputError** (1×): 2 validation errors for StructuredEvidence
measurements
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "parameter":...ücken."\n    }\n
  - betroffen: CASE_09/extract[doc_295159f988954cb283946097fde44604:werte]:23

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Charge XYL-2026-004A wurde laut QA-Freigabevermerk am 25.03.2026 freigegeben. Der Abweichungsbericht DEV-2026-891 wurde zwar am 12.03.2026 erfasst, jedoch erst am 14.12.2026 durch die QA geprüft – also mehr als acht Monate nach der Chargenfreigabe. Dies bedeutet, dass die QA-Prüfung der Abweichung zum Zeitpunkt der Freigabe noch nicht abgeschlossen war. Damit wurde die Charge freigegeben, bevor die vollständige QA-Bewertung der Abweichung vorlag, was einen klaren Verstoß gegen die Anforderung darstellt.
- ✅ `ERR_01_02` (high) — gefunden via evidence_fuzzy (Score 0.437): Der Freigabevermerk QA-RELEASE-XYL-004A gibt eine Dispositionsentscheidung (Freigabe zur Verpackung) und verweist auf die Abweichung DEV-2026-891. Eine explizite Verknüpfung mit dem Batch Record (Chargennummer, Verweis auf das Chargenprotokoll als Dokument) ist im Freigabevermerk selbst nicht dokumentiert. Der Batch Record existiert als separates Dokument, enthält aber seinerseits keine Dispositionsentscheidung. Die Verknüpfung zwischen Freigabeentscheidung und Batch Record ist damit nicht vollständig nachvollziehbar belegt.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Das Freigabe-Zertifikat (document_03) enthält eine Freigabeentscheidung für Charge CPH-2026-991, verknüpft diese jedoch nicht explizit mit dem Batch Record. Eine begründete Dispositionsentscheidung, die auf konkrete Batch-Record-Einträge verweist, fehlt. Erschwerend kommt hinzu, dass im Batch Record (document_02) eine nachträgliche Korrektur der Ausbeute von 96,47 % auf 98,1 % durch den Operator vorgenommen wurde, ohne dass eine QA-Bewertung oder Begründung dieser Korrektur dokumentiert ist. Die Freigabe-Notiz erwähnt lediglich pauschal, dass die Ausbeute der Vorgabe entspricht, ohne auf diese Korrektur einzugehen.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_fuzzy (Score 0.496): Das Chargenprotokoll (document_02) weist einen internen Widerspruch auf: Die rechnerisch korrekte Ausbeute beträgt 96,47 %, liegt damit außerhalb der Soll-Ausbeute von 98,0 %–101,0 %, wurde jedoch nachträglich auf 98,1 % korrigiert. Die Freigabenotiz (document_03) bestätigt, dass 'die Ausbeute der spezifizierten Vorgabe entspricht', ohne auf die Korrektur oder den ursprünglichen Wert einzugehen. Damit besteht ein dokumentierter Widerspruch zwischen dem rechnerischen Ergebnis im Batch Record und der Aussage in der Freigabenotiz, der nicht aufgeklärt wurde.
- 🔁 9 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Das Deviation Report enthält einen zeitlichen Widerspruch: Der Eintritt des Mitarbeiters in Raum R-202 ist laut elektronischem Logbuch um 14:35 Uhr verzeichnet, der Peak-Zeitstempel der Probenahme liegt jedoch bei 14:15 Uhr – also 20 Minuten vor dem dokumentierten Eintritt. Dieser Widerspruch deutet auf eine mögliche Inkonsistenz in den GxP-Systemaufzeichnungen hin, die eine Begründung, Autorisierung und Nachvollziehbarkeit im Audit Trail erfordert. Keine der vorliegenden Unterlagen enthält eine Erklärung, ein Berechtigungskonzept oder eine Begründung für diesen Widerspruch.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan CAPA-2026-014 beschreibt eine Maßnahme zur Anpassung des Reinigungsverfahrens als Reaktion auf eine Partikelgrenzwertüberschreitung – ein klares Qualitätsrisiko. Eine definierte und dokumentierte Wirksamkeitsprüfung (Effectiveness Check) ist im CAPA-Plan weder beschrieben noch referenziert. Der CAPA-Plan enthält lediglich Verantwortlichen und Termin, aber keinen Nachweis oder Plan für einen Effectiveness Check.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-P-2026-092 dokumentiert eine Temperaturüberschreitung auf 44,5°C (laut SCADA) bzw. sogar 48,2°C (laut Batch Record) bei einem Limit von 42,0°C. Die QS-Chargenbewertung enthält lediglich eine pauschale Aussage, dass kein nennenswerter Substanzabbau erwartet wird, ohne eine strukturierte, dokumentierte Auswirkungsbewertung auf Produktqualität und Patientensicherheit vorzulegen. Eine Chargenliste potenziell betroffener Chargen fehlt vollständig. Die bloße Erwartungsaussage ohne stützende Daten oder Methodik erfüllt nicht die Anforderung an eine dokumentierte Impact-Bewertung.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan CAPA-DEV-092 definiert eine Re-Training-Maßnahme für Operator J.K., enthält jedoch keinerlei Angaben zu einer geplanten oder dokumentierten Wirksamkeitsprüfung (Effectiveness Check). Ein Nachweis, dass nach Abschluss der Maßnahme deren Wirksamkeit überprüft wird, fehlt vollständig.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die QS-Freigabenotiz enthält eine Dispositionsentscheidung (Freigabe der Charge), verknüpft diese jedoch nicht explizit mit dem Batch Record. Der Batch-Record-Auszug (document_02) zeigt zudem einen manuellen Eintrag um 13:30 Uhr mit einer Produkttemperatur von 48,2 °C – weit über dem Limit von 42,0 °C – der in der QS-Bewertung nicht berücksichtigt wird. Die Freigabebegründung stützt sich ausschließlich auf die im Abweichungsbericht genannte Maximaltemperatur von 44,5 °C und ignoriert die im Batch Record dokumentierten höheren Messwerte. Eine nachvollziehbare Verknüpfung und Würdigung der Batch-Record-Daten fehlt.
- 🔁 13 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Validierungsnote VAL-NOTE-AT-442 (document_02) referenziert explizit den 'Anhang 4', in dem die exakten Beladungsmuster und maximal zulässigen Gesamtgewichte für Glaswaren detailliert aufgeführt sein sollen. Dieser Anhang 4 ist in den vorliegenden Chunks nicht enthalten und damit nicht nachweislich vorhanden. Da der Auslöser (die Referenz auf Anhang 4) belegt ist und der Anhang selbst fehlt, liegt ein Verstoß gegen die Vollständigkeit der Pflichtanhänge vor.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Unterlagen belegen eine Abweichung (Diskrepanz zwischen Logbucheintrag und elektronischem Schleusensystem bezüglich der Anwesenheit des ausführenden Mitarbeiters). Eine Risikobewertung oder Schweregradeinstufung dieser Abweichung ist in keinem der vorliegenden Dokumente enthalten. Stützende Labordaten fehlen ebenfalls vollständig. Die Anforderung ist damit nicht erfüllt.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Unterlagen belegen eine Abweichung (Diskrepanz zwischen Logbucheintrag und elektronischem Schleusensystem bezüglich der Anwesenheit des ausführenden Mitarbeiters). Eine Risikobewertung oder Schweregradeinstufung dieser Abweichung ist in keinem der vorliegenden Dokumente enthalten. Stützende Labordaten fehlen ebenfalls vollständig. Die Anforderung ist damit nicht erfüllt.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_02` (critical) — gefunden via evidence_substring (Score 1.0): Der interne Prüfplan Prüf-Spez-API-04 definiert für Amoxicillin Trihydrat ein Akzeptanzkriterium von 11,5% bis 12,8% Wassergehalt. Die hauseigene Re-Analyse ergab 13,2% – ein klarer Verstoß gegen die interne Spezifikation. Trotz dieser offenen Abweichung (LAB-DEV-2026-031, Status: In Untersuchung) wurde der Rohstoff durch QA-REL-AMO-01 final für die Produktion freigegeben, wobei die Freigabe ausschließlich auf das Lieferantenzertifikat gestützt wurde. Dies widerspricht der Anforderung, dass eine Verletzung interner Akzeptanzkriterien auch dann als Abweichung zu behandeln ist, wenn ein Lieferantenzertifikat Konformität ausweist.
- ❌ `ERR_06_01` (high) — übersehen: Akzeptanzkriterium der internen Spezifikation wird durch das Lieferanten-Zertifikat verletzt.
- ℹ️ 1 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ❌ `ERR_07_01` (high) — übersehen: Yield-Unterschreitung wird fälschlicherweise als konform deklariert.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 22 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht erklärt den Vorfall als 'isoliertes Einzelereignis' und sieht die Freigabe der Charge IBU-2026-P03 nach einer visuellen Stichprobenprüfung vor. Gleichzeitig zeigt das Logbuch der Anlage (document_02) zwei vorangegangene Werkzeugvorfälle an derselben Presse (14.03.2026 und 18.04.2026), die eine systematische Betrachtung nahelegen. Die Bewertung als 'isoliertes Einzelereignis ohne systematischen Charakter' ist angesichts der Vorgeschichte nicht hinreichend begründet. Ein abgeschlossenes Impact Assessment, das alle relevanten Aspekte berücksichtigt, ist nicht dokumentiert. Die Freigabeentscheidung wird vor Abschluss einer vollständigen Bewertung getroffen.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): Der Abweichungsbericht bewertet den Vorfall als 'isoliertes Einzelereignis' und schließt einen Einfluss auf andere Chargen kategorisch aus, ohne eine strukturierte Chargenliste oder eine Begründung der Chargenauswahl vorzulegen. Das Logbuch (document_02) belegt jedoch zwei vorangegangene Werkzeugvorfälle an derselben Presse (Chargen IBU-2026-P01 und IBU-2026-P02), die als potenziell betroffene Vorgängerchargen hätten bewertet werden müssen. Eine vollständige Erfassung aller potenziell betroffenen Chargen einschließlich Vorgänger- und Folgechargen ist nicht dokumentiert.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan sieht die Nachrüstung eines Inline-Metalldetektors sowie dessen Qualifizierung und Softwareintegration vor. Die terminierte Deadline für den 'Abschluss der gesamten Validierung' ist der 11.05.2026 – also einen Tag nach dem Vorfall vom 10.05.2026. Es ist offensichtlich unrealistisch, dass eine vollständige Beschaffung, Qualifizierung und Softwareintegration innerhalb eines Tages abgeschlossen werden kann. Ein aktueller, den tatsächlichen Equipmentzustand abdeckender Validierungsbericht für den Inline-Metalldetektor liegt nicht vor. Die Charge IBU-2026-P03 soll jedoch bereits freigegeben werden, ohne dass ein valider Nachweis für den aktuellen Prozesszustand (mit Metalldetektor) existiert.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-CEF-77 belegt, dass der pH-Wert in Phase 3 der Fermentation für 6 Stunden die spezifizierte Obergrenze von pH 7,40 überschritt und Spitzenwerte von pH 7,85 erreichte. Dies stellt eine klare Verletzung der internen Akzeptanzkriterien dar. Verschärfend kommt hinzu, dass der handschriftliche Batch Record für denselben Zeitraum vermerkt: 'Keine besonderen Vorkommnisse in der Schicht. Werte stabil.' – was im direkten Widerspruch zum SCADA-Audit-Trail steht, der einen manuellen Eingriff und eine Sollwertänderung von pH 7,20 auf pH 7,70 dokumentiert. Die Abweichung wurde zwar als DEV-CEF-77 erfasst, der Root Cause blieb jedoch ungeklärt, und die Aufarbeitung wurde trotz der Grenzwertverletzung fortgesetzt.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-CEF-77 dokumentiert eine pH-Drift über 6 Stunden mit ungeklärter Ursache (Root Cause unaufgeklärt) in Charge CEF-BIOR-2026-77. Eine Chargenliste mit Vorgänger- und Folgechargen sowie eine Begründung der Chargenauswahl fehlen in sämtlichen vorliegenden Dokumenten vollständig. Der Auslöser für die Pflicht (ungeklärte Abweichung mit potenzieller Auswirkung auf weitere Chargen) ist belegt; der geforderte Nachweis ist nicht vorhanden.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Modelllauf für diese Anforderungsgruppe fehlgeschlagen; die Anforderung bleibt unbeurteilt und gehört zur menschlichen Prüfung.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan benennt als Sofortmaßnahme ein Re-Testing zur Verifikation eines möglichen Probenahmefehlers, ohne dass technische Ursachen (Equipment, Kalibrierung, Alarme) dokumentiert ausgeschlossen wurden. Ein abgeschlossener Untersuchungsbericht mit belegter Grundursache liegt nicht vor. Der Laboranalyst bezeichnet den Befund lediglich als 'vermutlich temporären Ausreißer', ohne Belege. Die Anforderung ist damit nicht erfüllt.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan enthält zwar ein Zieldatum (16.05.2026), jedoch ist das Feld für den Maßnahmenverantwortlichen explizit als '[Kein Eintrag / Offen]' ausgewiesen. Ein benannter Maßnahmenverantwortlicher fehlt damit nachweislich.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die QA-Notiz (document_03) enthält eine Risikobewertung und erklärt marktregulatorische Maßnahmen für nicht erforderlich, verknüpft diese Aussage jedoch weder mit einem Batch Record noch mit einer formalen, begründeten Dispositionsentscheidung. Ein Batch Record wird in keinem der Chunks referenziert oder zitiert. Die Anforderung, die Freigabe- bzw. Dispositionsentscheidung mit dem zugehörigen Batch Record zu verknüpfen, ist damit nicht erfüllt.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
