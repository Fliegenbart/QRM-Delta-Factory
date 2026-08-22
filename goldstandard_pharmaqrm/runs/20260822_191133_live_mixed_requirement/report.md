# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `mixed` | Engine: `requirement`
- Zeitpunkt: 2026-08-22T19:11:33+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Hetzner-Modell: `-`

## Gesamtergebnis

- **Sensitivität:** 20 von 25 versteckten Fehlern gefunden (80%)
- **In Prüfmappe sichtbar:** 20 von 25 versteckten Fehlern (80%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 81 von 184 (44%) — 19 als Treffer gewertet, 62 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 103 von 184 (56%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 18.4 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 109 von 184 Findings mit verifiziertem Zitat (59%)

## Qualitätsmetriken

- Must-detect Recall: `0.8`
- Wiederholungen: `62` (Redundanzrate `0.7654`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `9/4/7`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 164 | 1,097,484 | 223,810 | 1,321,294 |
| openai | 124 | 0 | 0 | 0 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed_with_model_failures | 0 | 21 | 6 | 13 | 2/2 | 2/2 | 0/1 | - |
| CASE_02 | completed_with_model_failures | 0 | 16 | 7 | 7 | 2/2 | 2/2 | 0/1 | - |
| CASE_03 | completed_with_model_failures | 0 | 21 | 8 | 11 | 2/2 | 2/2 | 0/2 | - |
| CASE_04 | completed_with_model_failures | 0 | 22 | 11 | 8 | 3/3 | 3/3 | 0/1 | - |
| CASE_05 | completed_with_model_failures | 0 | 18 | 13 | 3 | 3/3 | 3/3 | 0/1 | - |
| CASE_06 | completed_with_model_failures | 0 | 2 | 0 | 1 | 1/2 | 1/2 | 0/1 | - |
| CASE_07 | completed_with_model_failures | 0 | 22 | 0 | 22 | 0/2 | 0/2 | 0/1 | - |
| CASE_08 | completed_with_model_failures | 0 | 22 | 4 | 16 | 2/3 | 2/3 | 0/1 | - |
| CASE_09 | completed_with_model_failures | 0 | 23 | 8 | 13 | 2/3 | 2/3 | 0/1 | - |
| CASE_10 | completed_with_model_failures | 0 | 17 | 5 | 9 | 3/3 | 3/3 | 0/1 | - |

## Modellausfälle

- **ProviderCircuitOpenError** (112×): Circuit breaker is open for openai
  - betroffen: CASE_01/entailment:11, CASE_01/entailment:12, CASE_01/entailment:13, CASE_01/entailment:14, CASE_01/entailment:15, CASE_01/entailment:16
  - … und 106 weitere
- **ProviderCallError** (12×): openai provider call failed with HTTP 400
  - betroffen: CASE_01/entailment:8, CASE_01/entailment:9, CASE_01/entailment:10, CASE_02/entailment:8, CASE_03/entailment:8, CASE_04/entailment:8
  - … und 6 weitere
- **ProviderStructuredOutputError** (6×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...n      }\n    ]\n
  - betroffen: CASE_02/assess:6, CASE_05/assess:7, CASE_06/assess:2, CASE_08/assess:0, CASE_09/assess:0, CASE_09/assess:3
- **ProviderStructuredOutputError** (3×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...ty": "critical"\n
  - betroffen: CASE_02/assess:7, CASE_05/assess:6, CASE_06/assess:4
- **ProviderStructuredOutputError** (3×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement... "evidence": []\n
  - betroffen: CASE_06/assess:0, CASE_10/assess:5, CASE_10/assess:6
- **ProviderStructuredOutputError** (3×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...verity": "high"\n
  - betroffen: CASE_06/assess:1, CASE_06/assess:3, CASE_06/assess:5
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Re-Val...r-121" freigegeben."}}]
  - betroffen: CASE_05/extract[doc_a5291922655f413484018831660fb147:felder]:27
- **ProviderStructuredOutputError** (1×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement..._support": null\n
  - betroffen: CASE_06/assess:7
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Finale...e_before_assessment"]}]
  - betroffen: CASE_06/extract[doc_0814f475a04540b9b73d67312aa0662f:felder]:16
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "description...stabil."\n    }\n  }\n]
  - betroffen: CASE_09/extract[doc_32ba26770d4e479288103a7e0fdf0bc7:felder]:29
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
measurements
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "parameter":...gesetzt"\n    }\n
  - betroffen: CASE_09/extract[doc_32ba26770d4e479288103a7e0fdf0bc7:werte]:30

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Freigabe der Charge XYL-2026-004A datiert vom 25.03.2026. Die Prüfung durch die Qualitätssicherung im Abweichungsbericht trägt die Signatur vom 14.12.2026 – also nach dem Freigabedatum. Dies deutet darauf hin, dass die Charge freigegeben wurde, bevor die QA-Prüfung des Abweichungsberichts abgeschlossen war. Damit ist das Verbot der Freigabe vor abgeschlossener Bewertung verletzt.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass kritische Prozessparameter innerhalb der spezifizierten Grenzen liegen und jede Über- oder Unterschreitung als Abweichung bewertet wird, auch bei visuell unauffälligem Produkt. Das Chargenprotokoll dokumentiert, dass die Manteltemperatur von 10:30 bis 11:00 Uhr bei 34,2 °C lag, während die Herstellanweisung laut Abweichungsbericht 40–45 °C vorschreibt. Die Abweichung wurde zwar als DEV-2026-891 erfasst, jedoch als 'Minor' eingestuft mit der Begründung, ein Einfluss auf die Produktqualität sei ausgeschlossen – obwohl der Batch Record einen signifikanten Viskositätsanstieg (2400 auf 2910 mPa·s) und die Bemerkung 'zähflüssig' zeigt. Die Risikobewertung erscheint unzureichend begründet und die QA-Freigabe stützt sich ausschließlich auf visuelle Homogenität, ohne instrumentelle Nachweise für Stabilität oder Freisetzungskinetik.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 13 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Die Charge CPH-2026-991 wurde durch Dr. Bernd Richter für den Markt freigegeben. Im Chargenprotokoll ist jedoch eine nachträgliche, nicht autorisiert wirkende Korrektur des Ausbeutewerts dokumentiert (von 96.47% auf 98.1% mit Verweis auf einen unvollständigen Wiegebegleitschein). Der ursprüngliche berechnete Wert von 96.47% liegt außerhalb der deklarierten Soll-Ausbeute von 98.0%–101.0%. Eine abgeschlossene Abweichungsbewertung oder ein Impact Assessment zu dieser Diskrepanz und der Korrektur ist in den Unterlagen nicht nachgewiesen. Die Freigabe erfolgte somit ohne nachweislich abgeschlossene Bewertung eines potenziell kritischen Befunds.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_fuzzy (Score 0.496): Das Chargenprotokoll (document_02) weist einen rechnerisch belegten Yield von 96,47 % aus, der unterhalb der deklarierten Soll-Ausbeute von 98,0 %–101,0 % liegt. Dieser Wert wurde nachträglich auf 98,1 % korrigiert. Das Freigabe-Zertifikat (document_03) bestätigt hingegen, dass 'die Ausbeute der spezifizierten Vorgabe entspricht', ohne auf die Korrektur oder den ursprünglichen Wert einzugehen. Die Inkonsistenz zwischen dem rechnerisch ermittelten Wert (96,47 %), dem korrigierten Wert (98,1 %) und der Freigabeaussage ist nicht aufgeklärt und stellt einen dokumentarischen Widerspruch dar.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Eine Grundursachenanalyse ist in keinem der vorliegenden Dokumente dokumentiert. Zusätzlich besteht ein erheblicher Widerspruch in der Zeiterfassung: Der Peak-Zeitstempel ist 14:15 Uhr, der Mitarbeitereintritt laut elektronischem Logbuch jedoch erst 14:35 Uhr – der Mitarbeiter war also zum Zeitpunkt des Peaks noch nicht im Raum. Dieser Widerspruch ist nicht aufgeklärt und schließt eine einfache Zuschreibung als 'Bedienerfehler' aus. Technische Ursachen (z. B. Kalibrierung, Gerätealarm, Datenfehler) wurden nicht dokumentiert ausgeschlossen.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Die Unterlagen belegen eine offene Abweichung (DEV-QS-2026-014) mit laufendem CAPA-Plan (Umsetzungstermin 30.05.2026) für die Charge LPO-2026-11A. Es gibt jedoch keine Aussage darüber, ob die Charge bereits freigegeben wurde oder ob die Abweichungsbewertung und das Impact Assessment abgeschlossen sind. Da weder eine Freigabeentscheidung noch eine abgeschlossene Bewertung dokumentiert sind, kann ein Verstoß nicht ausgeschlossen werden.
- 🔁 8 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 11 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-P-2026-092 wurde im QS-Freigabevermerk bewertet, jedoch fehlt eine dokumentierte, strukturierte Auswirkungsbewertung auf Produktqualität und Patientensicherheit. Die QS-Notiz enthält lediglich eine pauschale Aussage, dass kein nennenswerter Substanzabbau erwartet wird, ohne eine nachvollziehbare Methodik oder Chargenliste potenziell betroffener Chargen. Eine Bewertung weiterer möglicherweise betroffener Chargen (z. B. durch dasselbe defekte Ventil) ist nicht dokumentiert.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan (document_03) definiert eine Re-Training-Maßnahme für Operator J.K., enthält jedoch keinerlei Angaben zu einer Wirksamkeitsprüfung (Effectiveness Check). Weder ein Prüfkriterium noch ein Nachweis oder eine Methode zur Bewertung der Wirksamkeit sind dokumentiert. Der Auslöser (CAPA-Maßnahme mit Qualitätsbezug) ist belegt; der geforderte Nachweis fehlt vollständig.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-P-2026-092 betrifft die Charge PAR-2026-H102. Eine Batch-Impact-Bewertung, die Vorgänger- und Folgechargen einschließt sowie eine Begründung der Chargenauswahl enthält, ist in keinem der vorliegenden Dokumente zu finden. Die QS-Chargenbewertung (document_04) beschränkt sich ausschließlich auf PAR-2026-H102 und nennt weder Vorgänger- noch Folgechargen. Der Auslöser (dokumentierte Abweichung) ist belegt; der geforderte Nachweis fehlt.
- 🔁 11 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Validierungsnote VAL-NOTE-AT-442 referenziert explizit einen 'Anhang 4', in dem die exakten Beladungsmuster und maximal zulässigen Gesamtgewichte für Glaswaren detailliert aufgeführt sind. Dieser Anhang 4 ist in den vorgelegten Unterlagen nicht enthalten. Der Auslöser (Referenz auf einen Pflichtanhang) ist belegt, der Anhang selbst fehlt.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Der Batch Record (Autoklavierungs-Logbuch ZYK-STER-992) für die Charge OXA-2026-088 ist vorhanden, jedoch fehlt jede Dispositionsentscheidung vollständig. Darüber hinaus besteht eine schwerwiegende Diskrepanz: Der im Logbuch als ausführender Mitarbeiter eingetragene PNN-8812 (P.M.) war laut elektronischem Schleusensystem vor 08:45 Uhr nicht im Bereich des Autoklaven anwesend, obwohl die Beladung um 08:15 Uhr und der Programmstart um 08:20 Uhr dokumentiert sind. Zudem weichen die Initialen im Logbuch (P.M.) von denen im Schleusensystem (A.S.) ab. Diese Diskrepanz begründet eine Abweichung, die eine begründete und rückverfolgbare Dispositionsentscheidung erfordert – diese fehlt vollständig.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Der Batch Record (Autoklavierungs-Logbuch ZYK-STER-992) für die Charge OXA-2026-088 ist vorhanden, jedoch fehlt jede Dispositionsentscheidung vollständig. Darüber hinaus besteht eine schwerwiegende Diskrepanz: Der im Logbuch als ausführender Mitarbeiter eingetragene PNN-8812 (P.M.) war laut elektronischem Schleusensystem vor 08:45 Uhr nicht im Bereich des Autoklaven anwesend, obwohl die Beladung um 08:15 Uhr und der Programmstart um 08:20 Uhr dokumentiert sind. Zudem weichen die Initialen im Logbuch (P.M.) von denen im Schleusensystem (A.S.) ab. Diese Diskrepanz begründet eine Abweichung, die eine begründete und rückverfolgbare Dispositionsentscheidung erfordert – diese fehlt vollständig.
- 🔁 13 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 3 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_02` (critical) — gefunden via evidence_substring (Score 1.0): Der interne Prüfplan Prüf-Spez-API-04 definiert für Amoxicillin Trihydrat ein Akzeptanzkriterium von 11,5 % bis 12,8 % Wassergehalt. Das hauseigene QC-Labor ermittelte einen Wassergehalt von 13,2 %, der diesen Grenzwert überschreitet. Trotz dieser offenen Abweichung (LAB-DEV-2026-031, Status: In Untersuchung) wurde der Rohstoff durch die QA-Freigabenotiz QA-REL-AMO-01 final für die Produktion autorisiert, wobei ausschließlich auf das Lieferantenzertifikat verwiesen wird. Die Anforderung, dass eine Verletzung interner Akzeptanzkriterien auch dann als Abweichung zu behandeln ist, wenn ein Lieferantenzertifikat Konformität ausweist, wurde nicht eingehalten: Die Freigabe erfolgte, obwohl die interne Abweichung noch offen war.
- ❌ `ERR_06_01` (high) — übersehen: Akzeptanzkriterium der internen Spezifikation wird durch das Lieferanten-Zertifikat verletzt.
- ℹ️ 1 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ❌ `ERR_07_01` (high) — übersehen: Yield-Unterschreitung wird fälschlicherweise als konform deklariert.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 22 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-IBU-2026-112 erklärt den Vorfall als 'isoliertes Einzelereignis' und kündigt die Freigabe von Charge IBU-2026-P03 nach einer zusätzlichen visuellen Stichprobenprüfung an. Gleichzeitig ist jedoch kein abgeschlossenes Impact Assessment dokumentiert – insbesondere angesichts der Vorgeschichte (zwei vorangegangene Werkzeugvorfälle an derselben Presse im März und April 2026, dokumentiert im Batch-Record-Auszug). Die Behauptung 'isoliertes Einzelereignis ohne systematischen Charakter' ist eine bloße Selbstauskunft ohne Primärevidenz einer abgeschlossenen Bewertung. Eine QA-Freigabeentscheidung mit Unterschrift ist nicht dokumentiert. Die Freigabe vor abgeschlossener Bewertung stellt einen kritischen Verstoß dar.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): Der Abweichungsbericht beschränkt die Bewertung ausschließlich auf Charge IBU-2026-P03 und schließt pauschal jeden Einfluss auf andere Chargen aus. Der Batch-Record-Auszug belegt jedoch zwei vorangegangene Werkzeugvorfälle an derselben Presse TAB-02 (Chargen IBU-2026-P01 und IBU-2026-P02). Eine Bewertung dieser Vorgängerchargen im Rahmen des aktuellen Impact Assessments ist nicht dokumentiert. Die Anforderung, alle potenziell betroffenen Chargen einschließlich Vorgänger- und Folgechargen zu erfassen, ist damit verletzt.
- ❌ `ERR_08_03` (medium) — übersehen: Unrealistisches, nicht plausibles CAPA-Zieldatum ohne adäquate Projektrealisierungszeit.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 16 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-CEF-77 belegt, dass die Aufarbeitung der Charge CEF-BIOR-2026-77 trotz ungeklärter Ursache der pH-Abweichung fortgesetzt wurde. Eine abgeschlossene Abweichungsbewertung (Root Cause unaufgeklärt) liegt nicht vor. Zudem ist das Unterschriftenfeld der Leitung Qualitätskontrolle im Change-Control-Dokument leer, was auf eine unvollständige QA-Freigabe hindeutet. Eine Freigabeentscheidung oder ein Nachweis, dass alle erforderlichen Bewertungen vor Fortführung/Freigabe abgeschlossen waren, ist nicht dokumentiert.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Der SCADA-Audit-Trail dokumentiert eindeutig einen manuellen Eingriff um 14:15 Uhr, bei dem der automatische Regelkreis deaktiviert und der Sollwert auf pH 7,70 angehoben wurde. Im handschriftlichen Batch Record hingegen findet sich die Anmerkung 'Keine besonderen Vorkommnisse in der Schicht. Werte stabil.' – eine direkte Widersprüchlichkeit zur elektronischen Aufzeichnung. Dies verletzt das ALCOA+-Prinzip der Korrektheit und Vollständigkeit: Die Originalaufzeichnung ist inkonsistent, und der schwerwiegende Eingriff wurde in der Papieraufzeichnung verschwiegen.
- ❌ `ERR_09_01` (critical) — übersehen: Intentionale Falschdokumentation im Batch Record im Widerspruch zum SCADA-Audit-Trail.
- 🔁 8 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 13 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Der Stabilitätsbericht stellt einen OOS-Befund bei der Verunreinigung fest und initiiert eine Laborabweichung. Der CAPA-Plan sieht lediglich ein Re-Testing vor, um einen 'Probenahmefehler im Labor zu verifizieren'. Ein abgeschlossener Untersuchungsbericht mit dokumentiertem Ausschluss technischer Ursachen (Equipment, Kalibrierung, Alarme) liegt nicht vor. Die Grundursache ist damit nicht belegt, sondern lediglich vermutet ('vermutlich ein temporärer Ausreißer').
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan enthält explizit keinen benannten Maßnahmenverantwortlichen: Das Feld ist als '[Kein Eintrag / Offen]' ausgewiesen. Ein Pflichtfeld fehlt damit nachweislich. Ein Zieldatum (16.05.2026) ist zwar angegeben, jedoch ist ohne benannten Verantwortlichen die Anforderung nicht vollständig erfüllt.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die QA-Notiz (document_03) enthält eine Risikobewertung und erklärt, dass keine marktregulierenden Maßnahmen erforderlich seien, verknüpft diese Aussage jedoch weder mit einem Batch Record noch mit einer formalen, begründeten Dispositionsentscheidung. Ein Batch Record wird in keinem der Chunks erwähnt oder referenziert. Die Anforderung, die Freigabe- bzw. Dispositionsentscheidung mit den zugehörigen Batch Records zu verknüpfen, ist damit nicht erfüllt.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
