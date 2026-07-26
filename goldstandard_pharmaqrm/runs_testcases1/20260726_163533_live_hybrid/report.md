# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-07-26T16:35:33+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 41 von 41 versteckten Fehlern gefunden (100%)
- **In Prüfmappe sichtbar:** 40 von 41 versteckten Fehlern (98%)
- **Spezifität (Decoys):** 20 von 20 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 232 von 275 (84%) — 34 als Treffer gewertet, 198 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 43 von 275 (16%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 27.5 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 228 von 275 Findings mit verifiziertem Zitat (83%)

## Qualitätsmetriken

- Must-detect Recall: `1.0`
- Wiederholungen: `198` (Redundanzrate `0.8534`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `15/7/19`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 10 | 251,135 | 60,607 | 311,742 |
| mistral | 70 | 1,401,108 | 226,667 | 1,627,775 |
| openai | 10 | 190,707 | 30,533 | 221,240 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| case_01 | completed | 21 | 24 | 12 | 8 | 4/4 | 4/4 | 0/2 | human_review_required |
| case_02 | completed | 17 | 23 | 15 | 4 | 4/4 | 4/4 | 0/2 | human_review_required |
| case_03 | completed | 16 | 27 | 13 | 10 | 4/4 | 4/4 | 0/2 | human_review_required |
| case_04 | completed | 15 | 27 | 19 | 4 | 4/4 | 3/4 | 0/2 | human_review_required |
| case_05 | completed | 12 | 25 | 21 | 1 | 4/4 | 4/4 | 0/2 | human_review_required |
| case_06 | completed | 14 | 33 | 22 | 8 | 3/3 | 3/3 | 0/2 | human_review_required |
| case_07 | completed | 15 | 28 | 20 | 4 | 4/4 | 4/4 | 0/2 | human_review_required |
| case_08 | completed | 26 | 28 | 24 | 2 | 5/5 | 5/5 | 0/2 | human_review_required |
| case_09 | completed | 12 | 32 | 27 | 2 | 4/4 | 4/4 | 0/2 | human_review_required |
| case_10 | completed | 13 | 28 | 25 | 0 | 5/5 | 5/5 | 0/2 | human_review_required |

### case_01

- ✅ `CASE01-E001` (medium) — gefunden via evidence_substring (Score 1.0): Die Signaturdaten im Deviation Report DEV-2603-041 (Erstellung, QA-Erstbewertung, Abteilungsleitung Produktion) sind nicht durch einen Audit Trail belegt. Es fehlt der Nachweis, dass die Signaturen zeitlich plausibel und ohne manuelle Overrides erfolgten.
- ✅ `CASE01-E002` (medium) — gefunden via evidence_substring (Score 1.0): Im Deviation Report DEV-2603-041 und zugehörigen Dokumenten (CAPA-Plan, QA Approval Note, Batch Record) fehlt der Nachweis eines durchgeführten Audit-Trail-Reviews für die elektronischen Aufzeichnungen der Abweichung und der Prozessparameter während der Siebung. Dies betrifft die kritischen Zeitstempel und manuellen Eingriffe (z.B. Korrektur der internen Probennummer).
- ✅ `CASE01-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Ist-Ausbeute nach Trocknung für Charge QRM-AVR-2603-017 beträgt 91,2 % und liegt damit unterhalb der Soll-Ausbeute von 95,0–101,0 %. Der BMR-Eintrag bewertet dies als 'Keine weitere Bewertung erforderlich, da Verwiegung vollständig plausibel dokumentiert ist', ohne eine formale Abweichungsbewertung oder OOS-Untersuchung zu dokumentieren. Die QA-Note QA-N-2603-044 verweist auf eine noch ausstehende Ausbeutebewertung, ohne dass ein abgeschlossener Bewertungsbericht vorliegt. Dies stellt ein Risiko gemäß req_dev_oos_before_disposition und req_batch_no_release_before_assessment dar.
- ✅ `CASE01-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA CAPA-2603-022 enthält Maßnahmen ohne benannten Verantwortlichen (Maßnahme 1: Sichtkontrolle des Siebeinsatzes S-18). Dies verstößt gegen die Anforderung, dass jede CAPA-Maßnahme einen benannten Verantwortlichen haben muss.
- 🔁 12 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### case_02

- ✅ `CASE02-E001` (medium) — gefunden via evidence_substring (Score 1.0): Das Datum der Feststellung im Deviation Report DEV-2604-058 ist mit '2026-04-31' angegeben, was ein ungültiges Datum darstellt. Dies widerspricht den Anforderungen an die Plausibilität von Datumsangaben in elektronischen Aufzeichnungen (21 CFR Part 11 11.50).
- ✅ `CASE02-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2604-058 wurde als 'minor' eingestuft, jedoch fehlt eine nachvollziehbare Risikobewertung, die diese Einstufung stützt. Insbesondere wird die Überschreitung des Action Limits für nichtviable Partikel in der Klasse-A-Zone (1.240 Partikel ≥0,5 µm/m³ bei Action Limit 550) nicht ausreichend begründet. Die Begründung 'keine sichtbare Produktberührung und anschließend unauffällige Sichtkontrolle' ist nicht ausreichend, um ein Sterilitätsrisiko auszuschließen.
- ✅ `CASE02-E003` (high) — gefunden via evidence_substring (Score 1.0): Das Füllvolumen-IPC der Stichprobe 12 (15:30 Uhr) lag mit 4,82 mL außerhalb des Akzeptanzkriteriums (4,90–5,10 mL), wurde jedoch nicht als Abweichung bewertet oder dokumentiert. Die Abfüllung wurde fortgesetzt, ohne dass eine Bewertung oder Dispositionsentscheidung im Batch Record oder in der QA-Note dokumentiert ist.
- ✅ `CASE02-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme CAPA-2604-037 wurde ohne dokumentierte Wirksamkeitsprüfung (Effectiveness Check) abgeschlossen. Gemäß ICH Q10 3.2.2 ist eine Wirksamkeitsprüfung für CAPA-Maßnahmen mit Qualitätsrisikobezug zwingend erforderlich.
- 🔁 15 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### case_03

- ✅ `CASE03-E001` (high) — gefunden via evidence_substring (Score 1.0): Im Reinigungsprotokoll (CR-2603-014) wurde ein korrigierter Restproteinwert für Swab B2 (ursprünglich 18 µg, korrigiert auf 8 µg) ohne Angabe von Änderungsgrund, Änderungsdatum oder Initialen dokumentiert. Dies widerspricht den Anforderungen an Datenintegrität (ALCOA+) und elektronische Aufzeichnungen gemäß req_di_alcoa_completeness und req_di_signature_plausibility.
- ✅ `CASE03-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Root Cause Analysis (RCA-2603-031) benennt als Ursache 'kurzzeitige Unaufmerksamkeit bei Sprühposition B', ohne technische Ursachen (z. B. Equipment, Kalibrierung, Alarme) dokumentiert auszuschließen. Dies widerspricht der Anforderung einer belegten Grundursache.
- ✅ `CASE03-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Root Cause Analysis (RCA-2603-031) und die CAPA-Maßnahmen (CAPA-2603-029) enthalten widersprüchliche Angaben zur Verantwortlichkeit und zum Termin der Maßnahmen. Dies widerspricht der Anforderung an Konsistenz über alle Dokumente eines Vorgangs gemäß req_doc_cross_consistency.
- ✅ `CASE03-E004` (medium) — gefunden via evidence_substring (Score 1.0): In keinem der vorliegenden Dokumente (CR-2603-014, RCA-2603-031, CAPA-2603-029, QA-N-2603-051) findet sich ein dokumentiertes Batch-Impact-Assessment, das alle potenziell betroffenen Chargen – insbesondere die Vorcharge QRM-CAN-2603-028 sowie Folgechargen auf MB-11 – erfasst und bewertet. Die QA-Freigabenotiz QA-N-2603-051 verweist lediglich auf 'Restproteinbewertung gemäß Anhang 3', ohne eine vollständige Chargenliste oder Begründung der Chargenauswahl zu enthalten. Dies verletzt req_batch_affected_completeness.
- 🔁 13 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### case_04

- ✅ `CASE04-E001` (high) — gefunden via evidence_substring (Score 1.0): Im Batch Manufacturing Record (BMR-SEL-2604-112-C) wird eine Raumtemperatur von 31.2 °C im Kompressionsraum KR-2 dokumentiert, was die spezifizierte Grenze von 18.0–25.0 °C überschreitet. Diese Abweichung wurde zwar quittiert, jedoch fehlt eine dokumentierte Bewertung der Auswirkung auf die Produktqualität der Charge QRM-SEL-2604-112.
- ✅ `CASE04-E002` (medium) — gefunden via evidence_substring (Score 1.0): Während der technischen Unterbrechung der Tablettenpresse TP-402 (Deviation DEV-2604-071) wurde die Materialabdeckung geöffnet. Es fehlt eine dokumentierte Bewertung des Risikos einer Kreuzkontamination oder mikrobiellen Belastung im Rahmen der Cleaning Validation.
- ✅ `CASE04-E003` (medium) — gefunden via evidence_substring (Score 1.0): Der Deviation Report DEV-2604-071 beschreibt ein ungewöhnliches Geräusch am Hauptmotor der Presse TP-402, das zu einem Motorwechsel führte. Im Dokumentenpaket findet sich kein Untersuchungsbericht, der die technische Grundursache des Motorversagens dokumentiert oder alternative Ursachen (z.B. Kalibrierung, Wartungsrückstand, Betriebsstunden) ausschließt. Die CAPA-Maßnahmen adressieren nur Schulung und künftige Sichtprüfung, nicht die Ursache des Motorausfalls selbst. Gemäß req_dev_root_cause ist eine belegte Grundursache Pflicht.
- ✅ `CASE04-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die betroffene Charge QRM-SEL-2604-112 wird in der Quality Approval Note (QA-N-2604-083) für die Freigabe empfohlen, jedoch fehlt eine explizite und dokumentierte Dispositionsentscheidung mit klarer Rationale für die Charge QRM-SEL-2604-112. Die Freigabeempfehlung bezieht sich auf eine andere Charge (QRM-SEL-2604-121), was zu einer unklaren Chargenbetroffenheit führt.
- 🔁 19 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### case_05

- ✅ `CASE05-E001` (high) — gefunden via evidence_substring (Score 1.0): Die betroffene Charge QRM-NIV-2604-033 wird in der Quality Approval Note (QA-N-2604-094) zur Freigabe vorgeschlagen, obwohl die Dispositionsentscheidung nicht explizit mit der internen Spezifikation für den Parameter 'Gehalt Hauptkomponente' (98.0 - 102.0 %) abgeglichen wurde. Das Supplier CoA weist 96.8 % aus, was unter der internen Spezifikation liegt, und das interne QC-Ergebnis von 96.9 % bestätigt diese Abweichung.
- ✅ `CASE05-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme im Zusammenhang mit der Abweichung DEV-2604-063 (Gehalt Hauptkomponente außerhalb interner Spezifikation) wurde dokumentiert, jedoch fehlt ein expliziter Nachweis für den Effectiveness Check gemäß ICH Q10 3.2.2. Die Quality Approval Note (QA-N-2604-094) erwähnt keine Wirksamkeitsprüfung der CAPA-Maßnahme.
- ✅ `CASE05-E003` (high) — gefunden via evidence_substring (Score 1.0): Die betroffene Charge QRM-NIV-2604-031 wurde am 2026-04-12 freigegeben, obwohl im Material Deviation Report (DEV-2604-063) keine explizite Dispositionsentscheidung oder Impact-Bewertung für diese Charge dokumentiert ist. Die Abweichung des Gehalts Hauptkomponente betrifft auch diese Charge.
- ✅ `CASE05-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme im Zusammenhang mit der Abweichung DEV-2604-063 (Gehalt Hauptkomponente außerhalb interner Spezifikation) wurde dokumentiert, jedoch fehlt ein expliziter Nachweis für den Effectiveness Check gemäß ICH Q10 3.2.2. Die Quality Approval Note (QA-N-2604-094) erwähnt keine Wirksamkeitsprüfung der CAPA-Maßnahme.
- 🔁 21 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 1 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### case_06

- ✅ `CASE06-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ORX-2604-009 weist einen erhöhten Differenzdruck-Peak während der Sterilfiltration auf (3.6 bar bei validiertem Limit ≤3.2 bar), jedoch fehlt eine dokumentierte Bewertung der Auswirkung auf die Produktqualität und Patientensicherheit im Deviation Report DEV-2604-077.
- ✅ `CASE06-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ORX-2604-009 wurde nach dem Pumpenwechsel (Pumpe P-77 durch P77-LFP200-04) hergestellt, jedoch fehlt eine dokumentierte technische Vergleichsbewertung oder Change Control zur Sicherstellung der Eignung des neuen Pumpentyps für den validierten Prozess.
- ✅ `CASE06-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme 'CAPA-2604-052' benennt zwar Verantwortliche und Termine, jedoch fehlt ein expliziter Nachweis der Wirksamkeitsprüfung (Effectiveness Check) im CAPA-Plan. Die Wirksamkeitsprüfung ist gemäß ICH Q10 3.2.2 für CAPA-Maßnahmen mit Qualitätsrisikobezug verpflichtend.
- 🔁 22 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### case_07

- ✅ `CASE07-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Auswirkungsbewertung der Abweichung DEV-2604-081 auf Produktqualität und Patientensicherheit ist nicht ausreichend dokumentiert. Es fehlt eine explizite Bewertung der betroffenen Charge QRM-LUM-2604-080 und eine klare Dispositionsentscheidung.
- ✅ `CASE07-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme Nr. 1 (Schulung aller Mitarbeitenden der Schicht S2 auf erweiterte Abfallbehälterkontrolle) ist als 'abgeschlossen' markiert, aber es fehlt ein konkreter Nachweis der Wirksamkeit der Schulung. Der Training Record (TR-2604-079) dokumentiert zwar die Teilnahme, jedoch nicht die Wirksamkeit der Schulung.
- ✅ `CASE07-E003` (medium) — gefunden via evidence_substring (Score 1.0): Der Deviation Report DEV-2604-081 bewertet das Ereignis als 'erstmaliges Ereignis auf Linie PK-3' (Deviation Report), während die Quality Approval Note QA-N-2604-102 einen ähnlichen Etikettenfund (DEV-2601-019) in der Deviation History der letzten sechs Monate erwähnt. Dies stellt einen Widerspruch in der Bewertung der Erstmaligkeit des Ereignisses dar.
- ✅ `CASE07-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die betroffene Charge QRM-LUM-2604-080 wird im Deviation Report DEV-2604-081 und Packaging Record PKR-LUM-2604-080 erwähnt, jedoch fehlt eine dokumentierte Dispositionsentscheidung mit klarer Begründung der Chargenfreigabe oder -sperrung. Die Quality Approval Note QA-N-2604-102 empfiehlt die Freigabe der Charge QRM-LUM-2604-088, erwähnt jedoch nicht explizit die betroffene Charge QRM-LUM-2604-080.
- 🔁 20 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### case_08

- ✅ `CASE08-E001` (critical) — gefunden via evidence_substring (Score 1.0): Der Audit-Trail-Review für den Feuchtesensor RH-D17 im Zeitraum 2026-03-28 bis 2026-04-16 ist nicht dokumentiert, obwohl ein Driftverdacht vorlag und der Sensor für die kritische Charge QRM-MER-2604-052 verwendet wurde. Es fehlt der Nachweis, dass sicherheits- oder qualitätsrelevante Einträge geprüft und nicht ausgeschlossen wurden.
- ✅ `CASE08-E002` (high) — gefunden via evidence_substring (Score 1.0): Der Audit-Trail-Review für den Feuchtesensor RH-D17 im Zeitraum 2026-03-28 bis 2026-04-16 ist nicht dokumentiert, obwohl ein Driftverdacht vorlag und der Sensor für die kritische Charge QRM-MER-2604-052 verwendet wurde. Es fehlt der Nachweis, dass sicherheits- oder qualitätsrelevante Einträge geprüft und nicht ausgeschlossen wurden.
- ✅ `CASE08-E003` (critical) — gefunden via evidence_substring (Score 1.0): Der Audit-Trail-Review für den Feuchtesensor RH-D17 im Zeitraum 2026-03-28 bis 2026-04-16 ist nicht dokumentiert, obwohl ein Driftverdacht vorlag und der Sensor für die kritische Charge QRM-MER-2604-052 verwendet wurde. Es fehlt der Nachweis, dass sicherheits- oder qualitätsrelevante Einträge geprüft und nicht ausgeschlossen wurden.
- ✅ `CASE08-E004` (critical) — gefunden via evidence_substring (Score 1.0): Die CAPA-Wirksamkeitsprüfung ist für die Charge QRM-MER-2604-052 bis zum 2026-05-05 geplant, jedoch fehlt ein dokumentierter Effectiveness Check zur Bestätigung der Wirksamkeit der durchgeführten Maßnahmen. Ohne diesen Nachweis ist unklar, ob die CAPA-Maßnahmen tatsächlich die Ursache des Feuchtesensor-Drifts beheben und zukünftige Abweichungen verhindern.
- ✅ `CASE08-E005` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Wirksamkeitsprüfung ist für die Charge QRM-MER-2604-052 bis zum 2026-05-05 geplant, jedoch fehlt ein dokumentierter Effectiveness Check zur Bestätigung der Wirksamkeit der durchgeführten Maßnahmen. Ohne diesen Nachweis ist unklar, ob die CAPA-Maßnahmen tatsächlich die Ursache des Feuchtesensor-Drifts beheben und zukünftige Abweichungen verhindern.
- 🔁 24 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 2 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### case_09

- ✅ `CASE09-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Reinigungsvalidierungsnote (VAL-CLN-FB22 Rev.05) schreibt eine maximale Dirty Hold Time von 24 Stunden vor. Die Charge QRM-TER-2603-067 wurde jedoch erst am 2026-03-12 um 08:15 gereinigt, obwohl die Abfüllung bereits am 2026-03-10 um 22:40 endete. Dies führt zu einer Dirty Hold Time von ~33,5 Stunden, was die validierte Grenze überschreitet. Eine Bewertung der Auswirkung auf die Produktqualität oder eine dokumentierte Dispositionsentscheidung fehlt.
- ✅ `CASE09-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Reinigungsvalidierungsnote (VAL-CLN-FB22 Rev.05) schreibt eine validierte Detergentkonzentration von 1.0 % ±0.1 % vor. Im Reinigungsrecord (CR-2603-041) wurde jedoch eine Konzentration von 0.5 % Cleansol-M dokumentiert, ohne dass eine Change-Control-Bewertung oder Brückenvalidierung vorliegt.
- ✅ `CASE09-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-TER-2603-067 weist eine technische Abweichung (Sprühdüse N-4 nicht vollständig eingerastet) auf, die zu einer abweichenden Sprühverteilung führte. Die Root Cause wurde als Bedienerfehler identifiziert, jedoch fehlt der dokumentierte Ausschluss technischer Ursachen (z. B. Equipment, Kalibrierung, Alarme). Eine vollständige Impact-Bewertung für die betroffene Charge ist nicht nachweisbar.
- ✅ `CASE09-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-TER-2603-067 weist eine technische Abweichung (Sprühdüse N-4 nicht vollständig eingerastet) auf, die zu einer abweichenden Sprühverteilung führte. Die Root Cause wurde als Bedienerfehler identifiziert, jedoch fehlt der dokumentierte Ausschluss technischer Ursachen (z. B. Equipment, Kalibrierung, Alarme). Eine vollständige Impact-Bewertung für die betroffene Charge ist nicht nachweisbar.
- 🔁 27 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 2 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### case_10

- ✅ `CASE10-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ZEP-2604-014 wurde zur Freigabe empfohlen, obwohl die APS-Bridging-Bewertung für die erhöhte Füllgeschwindigkeit (165 Vials/min) und den neuen Stopfentrichter SB-9 noch aussteht und keine QA-Freigabe für die Implementierung vorliegt. Dies stellt ein wesentliches Compliance-Risiko dar, da die Prozessänderungen nicht validiert sind.
- ✅ `CASE10-E002` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ZEP-2604-014 wurde zur Freigabe empfohlen, obwohl die APS-Bridging-Bewertung für die erhöhte Füllgeschwindigkeit (165 Vials/min) und den neuen Stopfentrichter SB-9 noch aussteht und keine QA-Freigabe für die Implementierung vorliegt. Dies stellt ein wesentliches Compliance-Risiko dar, da die Prozessänderungen nicht validiert sind.
- ✅ `CASE10-E003` (high) — gefunden via evidence_substring (Score 1.0): Die QA-Freigabeentscheidung für Charge QRM-ZEP-2604-014 (Datum: 2026-04-26) erfolgt ohne dokumentierten Nachweis eines durchgeführten Audit-Trail-Reviews für die elektronischen Daten der aseptischen Abfüllung und des Environmental Monitoring (EM). Dies widerspricht der Anforderung nach regelmaessiger und risikobasierter Prüfung von GxP-relevanten elektronischen Daten mit Audit Trail.
- ✅ `CASE10-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Freigabeentscheidung für Charge QRM-ZEP-2604-014 (Datum: 2026-04-26) erfolgt ohne dokumentierten Nachweis eines durchgeführten Audit-Trail-Reviews für die elektronischen Daten der aseptischen Abfüllung und des Environmental Monitoring (EM). Dies widerspricht der Anforderung nach regelmaessiger und risikobasierter Prüfung von GxP-relevanten elektronischen Daten mit Audit Trail.
- ✅ `CASE10-E005` (high) — gefunden via evidence_substring (Score 1.0): Die EM-Abweichung DEV-2604-074 (2 KBE in Klasse A, Stopfentrichter SB-9) wurde als 'low' eingestuft, ohne dass eine detaillierte Risikobewertung oder eine Bewertung der Auswirkungen auf die Charge QRM-ZEP-2604-014 vorliegt. Die Einstufung basiert lediglich auf einer Wiederholungsprobe mit 0 KBE, was keine ausreichende Begründung für die Bewertung der Abweichung darstellt.
- 🔁 25 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
