# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `mixed` | Engine: `requirement`
- Zeitpunkt: 2026-08-23T15:20:07+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Hetzner-Modell: `-`

## Gesamtergebnis

- **Sensitivität:** 24 von 25 versteckten Fehlern gefunden (96%)
- **In Prüfmappe sichtbar:** 24 von 25 versteckten Fehlern (96%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 109 von 180 (61%) — 22 als Treffer gewertet, 87 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 71 von 180 (39%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 18.0 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 174 von 180 Findings mit verifiziertem Zitat (97%)

## Qualitätsmetriken

- Must-detect Recall: `0.96`
- Wiederholungen: `87` (Redundanzrate `0.7982`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `8/6/10`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 164 | 1,125,639 | 257,411 | 1,383,050 |
| openai | 148 | 102,600 | 19,827 | 122,427 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 18 | 4 | 12 | 2/2 | 2/2 | 0/1 | - |
| CASE_02 | completed_with_model_failures | 0 | 15 | 10 | 3 | 2/2 | 2/2 | 0/1 | - |
| CASE_03 | completed | 0 | 22 | 10 | 10 | 2/2 | 2/2 | 0/2 | - |
| CASE_04 | completed | 0 | 20 | 15 | 2 | 3/3 | 3/3 | 0/1 | - |
| CASE_05 | completed_with_model_failures | 0 | 18 | 11 | 5 | 3/3 | 3/3 | 0/1 | - |
| CASE_06 | completed_with_model_failures | 0 | 4 | 0 | 2 | 2/2 | 2/2 | 0/1 | - |
| CASE_07 | completed | 0 | 22 | 7 | 14 | 1/2 | 1/2 | 0/1 | - |
| CASE_08 | completed_with_model_failures | 0 | 21 | 8 | 10 | 3/3 | 3/3 | 0/1 | - |
| CASE_09 | completed_with_model_failures | 0 | 23 | 12 | 9 | 3/3 | 3/3 | 0/1 | - |
| CASE_10 | completed_with_model_failures | 0 | 17 | 10 | 4 | 3/3 | 3/3 | 0/1 | - |

## Modellausfälle

- **ProviderStructuredOutputError** (6×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...n      }\n    ]\n
  - betroffen: CASE_02/assess:6, CASE_02/assess:7, CASE_06/assess:2, CASE_08/assess:0, CASE_09/assess:3, CASE_09/assess:4
- **ProviderStructuredOutputError** (3×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...verity": "high"\n
  - betroffen: CASE_05/assess:7, CASE_06/assess:1, CASE_06/assess:3
- **ProviderStructuredOutputError** (3×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement... "evidence": []\n
  - betroffen: CASE_06/assess:0, CASE_10/assess:5, CASE_10/assess:6
- **ProviderStructuredOutputError** (2×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...ty": "critical"\n
  - betroffen: CASE_05/assess:6, CASE_06/assess:4
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Reinig..._cleaning_sterility"]}]
  - betroffen: CASE_02/extract[doc_2edcd6e0d91f45799fea0d3d854b98c6:felder]:31
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Re-Val...erage_current_state"]}]
  - betroffen: CASE_05/extract[doc_d89663ea9ddf48a59d23a23dbad118d0:felder]:27
- **ProviderStructuredOutputError** (1×): 1 validation error for RequirementGroupOutput
verdicts
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "requirement...rity": "medium"\n
  - betroffen: CASE_06/assess:5
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[{"description": "Finale...endbar" eingebucht."}}]
  - betroffen: CASE_06/extract[doc_0e584a73e5ae4374bbdadc36398625d5:felder]:16
- **ProviderStructuredOutputError** (1×): 1 validation error for StructuredEvidence
events
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "description...stabil."\n    }\n  }\n]
  - betroffen: CASE_09/extract[doc_c57e7c09d28543d380e31ffa698498e1:felder]:33
- **ProviderStructuredOutputError** (1×): 2 validation errors for StructuredEvidence
measurements
  Input should be a valid list [type=list_type, input_value='[\n  {\n    "parameter":...ücken."\n    }\n
  - betroffen: CASE_09/extract[doc_c57e7c09d28543d380e31ffa698498e1:werte]:34

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Charge XYL-2026-004A wurde laut QA-Freigabevermerk am 25.03.2026 freigegeben. Die QA-Prüfung des Abweichungsberichts (DEV-2026-891) erfolgte laut Unterschrift von Dr. Anna Klar am 14.12.2026 – also nach der Chargenfreigabe. Dies bedeutet, dass die Charge freigegeben wurde, bevor die QA-Prüfung der Abweichungsbewertung abgeschlossen war. Dies stellt einen kritischen Verstoß gegen das Prinzip dar, dass keine Freigabe vor abgeschlossener Bewertung erfolgen darf.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2026-891 wurde erfasst und eine initiale Risikobewertung vorgenommen. Eine dokumentierte Auswirkungsbewertung auf Produktqualität und Patientensicherheit mit expliziter Chargenliste (d.h. Prüfung, ob weitere Chargen betroffen sein könnten) fehlt jedoch. Der QA-Freigabevermerk beschränkt sich auf die visuelle Homogenität als Ausschlussgrund, ohne eine strukturierte Impact-Assessment-Dokumentation oder eine Chargenliste vorzulegen. Der Auslöser der Pflicht ist belegt; der geforderte Nachweis fehlt. Der Messwert 34,2 °C für 'Manteltemperatur' liegt außerhalb der deklarierten Grenze (Bereich 40–45).
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Das Freigabe-Zertifikat enthält eine Freigabeentscheidung für Charge CPH-2026-991, jedoch fehlt eine nachvollziehbare Begründung der Dispositionsentscheidung unter Berücksichtigung der im Chargenprotokoll dokumentierten Unregelmäßigkeit (nachträgliche Korrektur der Ausbeute von 96,47 % auf 98,1 % durch den Operator). Die QA-Freigabe behauptet pauschal, die Ausbeute entspreche der Vorgabe, ohne die Korrektur zu adressieren oder eine explizite Verknüpfung mit dem Batch Record herzustellen.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_fuzzy (Score 0.496): Die berechnete Gesamtausbeute im Chargenprotokoll beträgt rechnerisch 96,47 %, liegt damit unterhalb der deklarierten Soll-Ausbeute von 98,0 %–101,0 % und wurde nachträglich ohne vollständige Signatur auf 98,1 % korrigiert. Die Freigabenotiz (document_03) bestätigt hingegen pauschal, die Ausbeute entspreche der spezifizierten Vorgabe, ohne auf die Korrektur oder den fehlenden Wiegebegleitschein einzugehen. Dieser Widerspruch zwischen dem rechnerischen Ergebnis, der Korrektur und der Freigabeaussage ist nicht aufgeklärt.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 3 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Die Unterlagen enthalten einen zeitlichen Widerspruch: Der Peak-Zeitstempel ist 14:15 Uhr, der Eintritt des Mitarbeiters laut elektronischem Logbuch jedoch 14:35 Uhr. Dies deutet möglicherweise auf eine Inkonsistenz im Audit Trail oder einen manuellen Eingriff hin. Ein Berechtigungskonzept oder eine Begründung für etwaige Override-Aktionen ist nicht dokumentiert. Der Sachverhalt ist nicht eindeutig aufgeklärt und bedarf menschlicher Prüfung.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan CAPA-2026-014 beschreibt eine Maßnahme zur Anpassung des Reinigungsverfahrens als Reaktion auf eine Partikelüberschreitung – ein dokumentiertes Qualitätsrisiko. Eine definierte und dokumentierte Wirksamkeitsprüfung (Effectiveness Check) ist im CAPA-Plan nicht enthalten. Der Auslöser (CAPA mit Qualitätsrisikobezug) ist belegt; der geforderte Nachweis fehlt. Im CAPA-Plan fehlt der regulatorisch geforderte Effectiveness Check (Wirksamkeitsprüfung) für 1 Maßnahme(n), z. B. 'Reinigungsverfahren für die Wände des Raums R-202 anpassen zur Vermeidung zukünftiger Partikelüberschreitungen gemäß SOP-QS-REIN-001, Version 2.0'.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-P-2026-092 betrifft eine Temperaturüberschreitung während der Wirbelschicht-Granulation. Ein dokumentiertes Change-Impact-Assessment sowie eine Validierungsbewertung (Prüfung, ob betroffene Validierungen aktualisiert werden müssen) sind in keinem der vorliegenden Dokumente nachgewiesen. Der Auslöser – die Abweichung mit Temperaturüberschreitung – ist belegt; der geforderte Nachweis fehlt vollständig.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan CAPA-DEV-092 definiert eine Re-Training-Maßnahme für Operator J.K., enthält jedoch keinerlei Angaben zu einer Wirksamkeitsprüfung (Effectiveness Check). Es fehlen sowohl die Definition von Erfolgskriterien als auch ein geplanter Nachweis der Wirksamkeit nach Durchführung der Maßnahme. Im CAPA-Plan fehlt der regulatorisch geforderte Effectiveness Check (Wirksamkeitsprüfung) für 1 Maßnahme(n), z. B. 'Re-Training für Operator J.K. bezüglich der Alarmgrenzen an der Anlage WS-03'.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-P-2026-092 betrifft die Charge PAR-2026-H102 und löst die Pflicht zur Erfassung aller potenziell betroffenen Chargen (Vorgänger- und Folgechargen) aus. In keinem der vorliegenden Dokumente findet sich eine Chargenliste oder eine Begründung, warum ausschließlich PAR-2026-H102 betrachtet wurde. Die QS-Bewertung beschränkt sich auf diese eine Charge, ohne Vorgänger- oder Folgechargen zu erwähnen oder auszuschließen.
- 🔁 15 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 2 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Validierungsnote VAL-NOTE-AT-442 referenziert explizit einen Anhang 4, in dem die exakten Beladungsmuster und maximal zulässigen Gesamtgewichte für Glaswaren detailliert aufgeführt sind. Dieser Anhang 4 ist in den vorliegenden Dokumenten nicht enthalten und wurde nicht als Chunk übergeben. Da der Auslöser (die Referenz auf Anhang 4) belegt ist, der Anhang selbst jedoch fehlt, liegt ein Verstoß gegen die Vollständigkeit der Pflichtanhänge vor.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Das Autoklavierungs-Logbuch dokumentiert den Sterilisationszyklus ZYK-STER-992 für die Charge OXA-2026-088 am 11.05.2026 mit Entnahme der Sterilgüter um 09:00 Uhr. Gleichzeitig ergibt sich aus dem Reinraum-Sicherungsbericht ein Widerspruch: Mitarbeiter PNN-8812 (der laut Logbuch ausführende Mitarbeiter P.M.) betrat die Personenschleuse zum Vorbereitungsraum erst um 08:45 Uhr, während laut Logbuch die Beladung bereits um 08:15 Uhr abgeschlossen und der Programmstart um 08:20 Uhr erfolgt war. Diese Diskrepanz begründet eine potenzielle Abweichung (mögliche Falschangabe im Batch Record oder Identitätsverwechslung). Eine dokumentierte Abweichungsbewertung, ein Impact Assessment oder eine QA-Freigabe vor Entnahme der Sterilgüter sind in den Unterlagen nicht nachgewiesen. Konservativ bewertet stellt das Fehlen einer abgeschlossenen Bewertung bei gleichzeitig belegtem Prozessabschluss (Entnahme 09:00 Uhr) einen Verstoß dar.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Das Autoklavierungs-Logbuch dokumentiert den Sterilisationszyklus ZYK-STER-992 für die Charge OXA-2026-088 am 11.05.2026 mit Entnahme der Sterilgüter um 09:00 Uhr. Gleichzeitig ergibt sich aus dem Reinraum-Sicherungsbericht ein Widerspruch: Mitarbeiter PNN-8812 (der laut Logbuch ausführende Mitarbeiter P.M.) betrat die Personenschleuse zum Vorbereitungsraum erst um 08:45 Uhr, während laut Logbuch die Beladung bereits um 08:15 Uhr abgeschlossen und der Programmstart um 08:20 Uhr erfolgt war. Diese Diskrepanz begründet eine potenzielle Abweichung (mögliche Falschangabe im Batch Record oder Identitätsverwechslung). Eine dokumentierte Abweichungsbewertung, ein Impact Assessment oder eine QA-Freigabe vor Entnahme der Sterilgüter sind in den Unterlagen nicht nachgewiesen. Konservativ bewertet stellt das Fehlen einer abgeschlossenen Bewertung bei gleichzeitig belegtem Prozessabschluss (Entnahme 09:00 Uhr) einen Verstoß dar.
- 🔁 11 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Änderungen an Lieferant, Material, Spezifikation oder Methode nicht ohne Begründung als 'no impact' gewertet werden und eine Auswirkungsbewertung auf Qualität und Validierung vorliegt. Die vorliegenden Dokumente zeigen, dass der Lieferant ChemieSynthese GmbH einen Wassergehalt von 13,2 % im CoA ausweist, der die interne Spezifikation (11,5 %–12,8 %) überschreitet. Es ist unklar, ob eine formale Lieferantenbewertung oder eine Impact-Bewertung dieser Materialdiskrepanz durchgeführt wurde. Die QA-Freigabenotiz verweist lediglich auf das Lieferanten-CoA als Konformitätsbeleg, ohne eine eigene Auswirkungsanalyse zu dokumentieren. Da weder eine Lieferantenbewertung noch eine Impact-Bewertung in den Chunks vorliegt, kann weder Erfüllung noch Verstoß abschließend festgestellt werden.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_substring (Score 1.0): Der interne Prüfplan Prüf-Spez-API-04 definiert für Amoxicillin Trihydrat ein Akzeptanzkriterium von 11,5 % bis 12,8 % Wassergehalt. Die hauseigene Re-Analyse ergab 13,2 % – ein klarer Überschreitungsbefund außerhalb der internen Spezifikation. Trotz dieser offenen Abweichung (LAB-DEV-2026-031, Status: In Untersuchung) wurde der Rohstoff durch QA-REL-AMO-01 vom 18.05.2026 final für die Produktion freigegeben, wobei ausschließlich auf das Lieferantenzertifikat verwiesen wird. Die Anforderung, dass eine Verletzung interner Akzeptanzkriterien auch dann als Abweichung zu behandeln ist, wenn das Lieferantenzertifikat Konformität ausweist, wurde damit nicht eingehalten. Der Messwert 13,2 % für 'Wassergehalt' liegt außerhalb der deklarierten Grenze (Bereich 11.5–12.8).
- ℹ️ 2 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.491): Das Herstellprotokoll weist für die Charge MET-2026-C09 einen manuell gesetzten 'Pass'-Status durch den Operator F.B. aus. Die Ausbeute von 92,4 % liegt außerhalb des validierten Toleranzbereichs (95,0 %–102,0 %), und der Abweichungsbericht DEV-MET-09 ist zum selben Datum (02.05.2026) erfasst. Eine abgeschlossene Abweichungsbewertung, ein Impact Assessment oder eine QA-Freigabe sind in den vorliegenden Dokumenten nicht nachgewiesen. Es besteht der begründete Verdacht, dass die Charge vor Abschluss der erforderlichen Bewertungen als 'Pass' markiert wurde.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-IBU-2026-112 erklärt ausdrücklich, dass ein Einfluss auf andere Chargen oder vorangegangene Produktionsschritte 'absolut ausgeschlossen' sei. Das Batch-Record-Excerpt belegt jedoch drei Werkzeugvorfälle an derselben Presse TAB-02 innerhalb von zwei Monaten (IBU-2026-P01, IBU-2026-P02, IBU-2026-P03). Eine Chargenliste mit Begründung der Chargenauswahl, die Vorgänger- und Folgechargen systematisch einschließt oder begründet ausschließt, ist nicht vorhanden. Die pauschale Ausschlussbehauptung ohne Primärevidenz genügt der Anforderung nicht.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): Der Werkzeugbruch und die detektierten Mikrorisse an Stempel Station 5 begründen ein konkretes Kontaminationsrisiko durch metallische Partikel. Eine explizite Reinigungsvalidierung oder ein Sterilisationsprotokoll sind in keinem der vorliegenden Dokumente enthalten. Der Abweichungsbericht schließt einen Einfluss auf andere Chargen pauschal aus, ohne eine Reinigungsvalidierung oder Kontaminationskontrollstrategie zu belegen. Dies ist keine ausreichende Evidenz gemäß Anforderung.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan CAPA-112-IBU beschreibt Maßnahmen zur Eliminierung metallischer Mikrofragmente – ein klares Qualitätsrisiko. Ein definierter und dokumentierter Effectiveness Check (Wirksamkeitsprüfung) ist in keinem der vorliegenden Chunks beschrieben oder referenziert. Die Anforderung, dass CAPA-Maßnahmen mit Qualitätsrisikobezug nur mit dokumentierter Wirksamkeitsprüfung abgeschlossen werden dürfen, ist damit nicht erfüllt. Im CAPA-Plan fehlt der regulatorisch geforderte Effectiveness Check (Wirksamkeitsprüfung) für 1 Maßnahme(n), z. B. 'Automatisches Metallsuchgerät (Inline-Metalldetektor) am Auslauf der Tablettenpresse nachrüsten; Beschaffung, Qualifizierung und Softwareintegration im Steuerungsnetzwerk priorisiert vorantreiben'.
- 🔁 8 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-CEF-77 vermerkt, dass die Aufarbeitung der Charge CEF-BIOR-2026-77 nach der pH-Drift fortgesetzt wurde. Eine begründete Dispositionsentscheidung sowie eine Verknüpfung mit dem Batch Record sind jedoch in keinem der vorliegenden Dokumente dokumentiert. Das Schichtbuch enthält sogar eine irreführende Anmerkung ('Keine besonderen Vorkommnisse'), die dem tatsächlichen Ereignis widerspricht. Der Auslöser der Dispositionspflicht ist belegt, der geforderte Nachweis fehlt.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-CEF-77 zur Charge CEF-BIOR-2026-77 weist einen ungeklärten Root Cause aus. Dennoch wurde die Aufarbeitung der Charge fortgesetzt, ohne dass eine abgeschlossene Abweichungsbewertung oder eine QA-Freigabeentscheidung dokumentiert ist. Zusätzlich ist im Change-Control-Dokument CC-2026-104 das Unterschriftenfeld der Leitung Qualitätskontrolle leer, was auf eine unvollständige QA-Freigabe hindeutet. Eine Freigabe vor abgeschlossener Bewertung ist damit nicht auszuschließen und stellt einen kritischen Befund dar.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Der Abweichungsbericht DEV-CEF-77 zur Charge CEF-BIOR-2026-77 weist einen ungeklärten Root Cause aus. Dennoch wurde die Aufarbeitung der Charge fortgesetzt, ohne dass eine abgeschlossene Abweichungsbewertung oder eine QA-Freigabeentscheidung dokumentiert ist. Zusätzlich ist im Change-Control-Dokument CC-2026-104 das Unterschriftenfeld der Leitung Qualitätskontrolle leer, was auf eine unvollständige QA-Freigabe hindeutet. Eine Freigabe vor abgeschlossener Bewertung ist damit nicht auszuschließen und stellt einen kritischen Befund dar.
- 🔁 12 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Der OOS-Befund ist dokumentiert und löst die Pflicht zur Grundursachenermittlung aus. Der CAPA-Plan beschränkt sich auf ein Re-Testing zur Verifikation eines möglichen Probenahmefehlers, ohne technische Ursachen (Equipment, Kalibrierung, Alarme) dokumentiert auszuschließen. Ein abgeschlossener Untersuchungsbericht mit belegter Grundursache liegt nicht vor. Der Laboranalyst bezeichnet den Befund lediglich als 'vermutlich temporären Ausreißer', ohne dies durch eine Untersuchung zu belegen. Die Maßnahme 'Dreifache Re-Analyse (Re-Testing) aus einer neuen unangebrochenen Rückstell-Karpule derselben Charge durchführen, um einen Probenahmefehler im Labor zu verifizieren' in 'Sofortmaßnahme' hat keinen benannten Verantwortlichen. Im CAPA-Plan fehlt der regulatorisch geforderte Effectiveness Check (Wirksamkeitsprüfung) für 1 Maßnahme(n), z. B. 'Dreifache Re-Analyse (Re-Testing) aus einer neuen unangebrochenen Rückstell-Karpule derselben Charge durchführen, um einen Probenahmefehler im Labor zu verifizieren'.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Die Charge INS-GLA-2025-05 befindet sich bereits seit Juni 2025 vollständig im Handel. Zum Zeitpunkt der QA-Notiz (19.05.2026) ist die Abweichungsbewertung noch nicht abgeschlossen – das Re-Testing läuft noch, und der CAPA-Plan weist keinen benannten Verantwortlichen auf. Die QA-Notiz erklärt die Analytikvorgaben lediglich als 'vorläufig erfüllt', was keine abgeschlossene Bewertung darstellt. Damit wurde die Charge in den Verkehr gebracht, bevor eine vollständige QA-Freigabe und Impact-Bewertung vorlagen. Dies stellt einen kritischen Verstoß dar.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die QA-Notiz (document_03) enthält eine Risikobewertung und erklärt marktregulatorische Maßnahmen für nicht erforderlich, verknüpft diese Entscheidung jedoch nicht mit einem Batch Record und liefert keine formale, begründete Dispositionsentscheidung im GMP-Sinne. Ein Batch Record wird in keinem der Dokumente referenziert oder zitiert.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
