# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid` | Engine: `requirement`
- Zeitpunkt: 2026-08-03T17:40:24+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 26 von 34 versteckten Fehlern gefunden (76%)
- **In Prüfmappe sichtbar:** 26 von 34 versteckten Fehlern (76%)
- **Spezifität (Decoys):** 28 von 32 Decoys korrekt nicht beanstandet (88%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 44 von 159 (28%) — 24 als Treffer gewertet, 20 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 115 von 159 (72%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 15.9 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 95 von 159 Findings mit verifiziertem Zitat (60%)

## Qualitätsmetriken

- Must-detect Recall: `0.7647`
- Wiederholungen: `20` (Redundanzrate `0.4545`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `7/12/7`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 61 | 106,848 | 28,176 | 135,024 |
| mistral | 99 | 439,039 | 259,205 | 698,244 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 17 | 3 | 11 | 3/3 | 3/3 | 2/3 | - |
| CASE_02 | completed | 0 | 17 | 2 | 13 | 2/3 | 2/3 | 0/3 | - |
| CASE_03 | completed | 0 | 18 | 3 | 11 | 4/4 | 4/4 | 0/3 | - |
| CASE_04 | completed | 0 | 17 | 1 | 14 | 2/3 | 2/3 | 0/3 | - |
| CASE_05 | completed | 0 | 17 | 6 | 7 | 4/4 | 4/4 | 0/3 | - |
| CASE_06 | completed_with_model_failures | 0 | 14 | 0 | 12 | 2/3 | 2/3 | 1/3 | - |
| CASE_07 | completed | 0 | 16 | 0 | 16 | 0/1 | 0/1 | 0/5 | - |
| CASE_08 | completed | 0 | 14 | 2 | 9 | 4/4 | 4/4 | 0/3 | - |
| CASE_09 | completed | 0 | 14 | 3 | 8 | 4/4 | 4/4 | 1/3 | - |
| CASE_10 | completed | 0 | 15 | 0 | 14 | 1/5 | 1/5 | 0/3 | - |

## Modellausfälle

- **ProviderStructuredOutputError** (1×): 1 validation error for FulfilledChallenge
missing_or_asserted_evidence
  Input should be a valid list [type=list_type, input_value='["Zeitgleichheit (contem...E
  - betroffen: CASE_06/challenge:8

### CASE_01

- ✅ `BLIND01-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen erfüllen die ALCOA+-Kriterien: Sie sind zurechenbar (signierte Einträge im BMR), lesbar, zeitgleich (Uhrzeiten der IPC-Proben), original (keine nachträglichen Änderungen im Audit-Trail), korrekt (konforme IPC-Werte), vollständig (alle relevanten Daten dokumentiert), konsistent (keine Widersprüche) und dauerhaft verfügbar.
- ✅ `BLIND01-E002` (medium) — gefunden via evidence_substring (Score 1.0): Das Modell hat für diese Anforderung kein Verdict geliefert; sie bleibt unbeurteilt.
- ✅ `BLIND01-E003` (high) — gefunden via evidence_fuzzy (Score 0.631): Der Audit-Trail des Steuerungssystems der Tablettenpresse TP-03 wurde für den relevanten Zeitraum überprüft und es ergaben sich keine Auffälligkeiten. Dies belegt einen dokumentierten Audit-Trail-Review.
- ⚠️ Decoy `BLIND01-D001` fälschlich beanstandet: Die Auswirkungsbewertung der Abweichung auf Produktqualität und Patientensicherheit ist dokumentiert. Die QA-Bewertung (QAB-24-0087) bestätigt, dass die Charge VC-24-0187 den Zulassungsanforderungen entspricht und die ausgeschleuste Teilmenge mengenmäßig erfasst wurde. Zudem wird der mechanische Verschleiß als Root Cause bestätigt, was die Bewertung der Auswirkung stützt.
- ⚠️ Decoy `BLIND01-D002` fälschlich beanstandet: Die IPC-Ergebnisse im BMR-Auszug (Abschnitt 4) werden explizit gegen die interne Spezifikation (Prüfanweisung PA-TAB-021, Rev. 03) bewertet. Der Einzelwert der Bruchfestigkeit von 89 N liegt nahe der oberen Spezifikationsgrenze von 90 N, wird aber im Abweichungsbericht als akzeptabel bewertet und durch zusätzliche Zerfallsprüfung (Protokoll ZP-24-0455) gestützt. Die Konformität jedes Messwerts ist dokumentiert und signiert.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 11 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `BLIND02-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Charge NX-24-0342 wurde erst nach abgeschlossener Abweichungsbewertung, Impact Assessment und QA-Freigabe freigegeben. Der QA-Freigabevermerk (FGV-24-0142) datiert vom 18.04.2024 und bestätigt, dass die Bewertung abgeschlossen ist. Die Abweichung DEV-24-0129 wurde am 05.04.2024 eröffnet und die QA-Prüfung am 03.04.2024 durchgeführt (chunk_2d77c8f0e5b9415a963ea7605560b6d8_p1). Die Freigabe erfolgte somit nach Abschluss aller erforderlichen Schritte.
- ✅ `BLIND02-E003` (medium) — gefunden via evidence_substring (Score 1.0): Jede CAPA-Maßnahme im CAPA-Plan (CAPA-24-0091) hat einen benannten Verantwortlichen und einen plausiblen Umsetzungstermin. Beispielhaft: Maßnahme M1 (SOP-Revision) hat N. Duran als Verantwortlichen und den Termin 31.05.2024; Maßnahme M2 (Austausch Stellungsregler) ist bereits abgeschlossen (Termin 09.04.2024); Maßnahme M3 (jährliche Funktionsprüfung) hat B. Hofmann als Verantwortlichen und den Termin 30.09.2024.
- ❌ `BLIND02-E002` (critical) — übersehen: Der Ausgangsstoff Lactose-Monohydrat (LM-24-0301) wurde am 02.04.2024 verarbeitet, obwohl die Freigabe erst am 04.04.2024 erteilt wurde; eine Bewertung dieses Sachverhalts fehlt vollständig.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 13 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `BLIND03-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Gehaltsmessungen im QC-Prüfprotokoll PP-24-0618 wurden gegen die interne Spezifikation (7,6–8,4 mg/ml) bewertet. Die Ergebnisse (8,52 mg/ml und 8,38 mg/ml) zeigen, dass das erste Ergebnis die obere Spezifikationsgrenze überschritt und somit als Abweichung behandelt wurde, obwohl das zweite Ergebnis innerhalb der Spezifikation lag. Dies belegt die Einhaltung der Anforderung, interne Akzeptanzkriterien strikt anzuwenden.
- ✅ `BLIND03-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte QA-Freigabe vor Abschluss des Vorgangs. Der CAPA-Plan (chunk_386877f6b3474d30a97be0935a0bc44c_p1) enthält einen Genehmigungsblock mit einem leeren Feld für die QA-Genehmigung ("__________  Datum: 21.05.2024"). Dies belegt, dass die QA-Freigabe zum Zeitpunkt der Dokumentation nicht vorlag. Die QA-Bewertung (chunk_ffdcf70bc279455a833df28030acf22c_p1) wurde zwar erstellt, ersetzt aber nicht die fehlende Genehmigung des CAPA-Plans.
- ✅ `BLIND03-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Herstellvorschrift HV-TAV-002 wurde durch Maßnahme M1 des CAPA-Plans geändert (verbindliche Mindestmischzeit von 30 Minuten vor der ersten IPC-Probenahme). Die QA-Bewertung bestätigt, dass das betroffene Personal nachweislich geschult ist, jedoch fehlt der Nachweis, dass die Schulung VOR der Ausführung der geänderten Tätigkeit (nächste Ansätze) durchgeführt wurde. Die Wirksamkeitsprüfung ist erst für den 31.10.2024 geplant, was bedeutet, dass die Schulung nicht vor der Umsetzung der geänderten Vorschrift abgeschlossen sein muss. Dies verstößt gegen die Anforderung, dass das Personal nachweislich und wirksam geschult sein muss, BEVOR die geänderte Tätigkeit ausgeführt wird.
- ✅ `BLIND03-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit, einschließlich aller potenziell betroffenen Chargen. Im Abweichungsbericht (document_01_abweichungsbericht.md) wird zwar die Ursache (unvollständige Durchmischung) und die Wiederholungsmessung beschrieben, es fehlt jedoch eine explizite Bewertung der Auswirkung auf die Produktqualität oder Patientensicherheit. Zudem wird keine Chargenliste oder Referenz auf andere betroffene Chargen genannt. Der Auslöser für die Pflicht (die Abweichung selbst) ist belegt, der geforderte Nachweis (Impact Assessment) fehlt jedoch.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 11 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `BLIND04-E001` (high) — gefunden via evidence_substring (Score 1.0): Die kritischen Prozessparameter liegen innerhalb der spezifizierten Grenzen. Die Trocknungstemperatur am Trocknungsende betrug 59,5 °C und liegt damit innerhalb der Vorgabe von 50–60 °C (SOP-GRA-0140, Abschnitt 6.3). Die Einwaagen für Magnesiumstearat und hochdisperses Siliciumdioxid entsprechen den Vorgaben der SOP (0,45–0,55 % bzw. 0,15–0,25 % der Ansatzmasse). Die Abweichung betraf den Siebeinsatz, nicht die Prozessparameter, und wurde durch Nachsieben korrigiert. Die QA-Bewertung bestätigt, dass die Korngrößenverteilung innerhalb der Vorgaben lag.
- ✅ `BLIND04-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahmen (CAPA-24-0133) sind mit einem Qualitätsrisiko verknüpft, da sie eine Verwechslung von Siebeinsätzen verhindern sollen. Die Wirksamkeitsprüfung (Effectiveness Check) ist jedoch nicht definiert oder dokumentiert. Der CAPA-Plan enthält lediglich den Hinweis: "Umfang, Kriterium und Termin der Wirksamkeitsprüfung: wird festgelegt." Dies stellt einen Verstoß gegen die Anforderung dar, da keine dokumentierte Wirksamkeitsprüfung vorliegt.
- ❌ `BLIND04-E002` (medium) — übersehen: Für den Siebwechsel am 14.06.2024 um 10:15 Uhr nennen Abweichungsbericht (FH) und BMR-Prozesslog (CM) unterschiedliche ausführende Personen.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `BLIND05-E001` (medium) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen erfüllen die ALCOA+-Kriterien. Sie sind zurechenbar (mit Unterschriften und Kürzeln), lesbar, zeitgleich (mit Zeitstempeln), original (keine nachträglichen Änderungen erkennbar), korrekt und vollständig. Die Dokumente sind konsistent, dauerhaft und verfügbar.
- ✅ `BLIND05-E002` (critical) — gefunden via evidence_substring (Score 1.0): Die Chargen-Impact-Bewertung IMP-24-0064 listet alle während der Feuchteexkursion in Raum L-02 gelagerten Bulkchargen auf (SV-24-0611, SV-24-0612, SV-24-0619) und begründet den Ausschluss der Charge SV-24-0605 mit deren vorherigem Transfer in die Konfektionierung. Die Belegungsliste aus dem Klimatrendbericht TRB-L-24-033 bestätigt diese Auswahl.
- ✅ `BLIND05-E003` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan CAPA-24-0147 definiert eine Wirksamkeitsprüfung mit Kriterium (erfolgreicher dokumentierter Alarmkettentest über zwei Halbjahresintervalle) und Termin (31.03.2025). Die Maßnahme M3 (halbjährlicher Funktionstest) ist direkt mit der Wirksamkeitsprüfung verknüpft.
- ✅ `BLIND05-E004` (high) — gefunden via evidence_substring (Score 1.0): Die Dispositionsentscheidung für jede betroffene Charge ist in der Chargen-Impact-Bewertung IMP-24-0064 begründet und mit den Stichprobenprüfungen (Karl-Fischer-Titration) verknüpft. Der QA-Freigabevermerk FGV-24-0169 bestätigt die Aufhebung der ERP-Sperrung und verweist auf die Bewertung.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `BLIND06-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die interne Spezifikation RS-KB-002, Rev. 05 wird im Abweichungsbericht (document_01_abweichungsbericht.md) zitiert und die Prüfergebnisse der Nachbeprobung (Partikelbefund nur in Gebinde 2, Wassergehalt 0,44 % vs. NMT 0,5 %) werden explizit gegen diese Spezifikation bewertet. Das Lieferantenzertifikat (CoA) wird zwar als konform ausgewiesen, aber die interne Bewertung der Partikel und des Wassergehalts erfolgt unabhängig davon und bestätigt die Einhaltung der internen Akzeptanzkriterien.
- ✅ `BLIND06-E003` (high) — gefunden via evidence_substring (Score 1.0): Jede CAPA-Maßnahme im CAPA-Plan (CAPA-24-0119) hat einen benannten Verantwortlichen und einen plausiblen Umsetzungstermin. Dies erfüllt die Anforderung nach einem verantwortlichen Ansprechpartner und einem realistischen Zeitplan.
- ❌ `BLIND06-E002` (medium) — übersehen: Die behauptete Nachprüfung des Chargenprotokolls der Vorcharge KL-24-0251 ist durch keinen referenzierbaren Nachweis belegt.
- ⚠️ Decoy `BLIND06-D001` fälschlich beanstandet: Die Auswirkungsbewertung der Abweichung DEV-24-0152 auf die Produktqualität und Patientensicherheit ist dokumentiert. Es wird bestätigt, dass die Charge KL-24-0288 ausschließlich aus unauffälligen Gebinden hergestellt wurde und die In-Prozess-Kontrollen konform sind. Zudem wurde die Vorcharge KL-24-0251 nachgeprüft und keine Beanstandungen festgestellt. Die Freigabeempfehlung der QA bestätigt die Bewertung.
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ❌ `BLIND07-E001` (high) — übersehen: Die Prüfsignatur des Abschnitts 4 im Verpackungsprotokoll VPR RV-24-0450 fehlt; das Feld 'Geprüft von' enthält nur ein Datum ohne Namen.
- ℹ️ 16 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `BLIND08-E001` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan (CAPA-24-0170) benennt für jede Maßnahme einen verantwortlichen Mitarbeiter und einen realistischen Umsetzungstermin. Beispielsweise ist für die Maßnahme M1 (Quellzeit in SOP verankert) B. Steinbrecher als Verantwortlicher und der 01.08.2024 als Termin genannt, was mit der tatsächlichen Umsetzung übereinstimmt. Die Nachschulung (M2) wurde ebenfalls fristgerecht bis zum 15.08.2024 abgeschlossen.
- ✅ `BLIND08-E002` (high) — gefunden via evidence_fuzzy (Score 0.565): Der Audit-Trail-Export des Coater-Leitsystems wurde geprüft und deckt den Prozesszeitraum der Charge MV-24-0821 vollständig ab. Es gibt keine Hinweise auf manuelle Parameteränderungen außerhalb der dokumentierten Ereignisse, was den risikobasierten Audit-Trail-Review belegt.
- ✅ `BLIND08-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Sprührate lag zum Zeitpunkt 11:05 Uhr mit 310 g/min außerhalb des spezifizierten Prozessfensters von 450–550 g/min. Dies ist im BMR-Auszug dokumentiert und als Abweichung DEV-24-0198 referenziert. Obwohl der Massenauftrag des Films im Sollfenster lag, stellt die Unterschreitung der Sprührate eine Verletzung der Prozessparameter-Grenzen dar.
- ✅ `BLIND08-E004` (medium) — gefunden via evidence_fuzzy (Score 0.733): Die Sprührate lag zum Zeitpunkt 11:05 Uhr mit 310 g/min außerhalb des spezifizierten Prozessfensters von 450–550 g/min. Dies ist im BMR-Auszug dokumentiert und als Abweichung DEV-24-0198 referenziert. Obwohl der Massenauftrag des Films im Sollfenster lag, stellt die Unterschreitung der Sprührate eine Verletzung der Prozessparameter-Grenzen dar.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `BLIND09-E001` (critical) — gefunden via evidence_substring (Score 1.0): Dieselbe Tätigkeit ('Filterintegritätstest nach Abfüllung durchgeführt für Charge Optril, OP-24-0501') ist von unterschiedlichen Personen gezeichnet: MS, MSt. Ohne dokumentierte Erklärung ist die Zurechenbarkeit nicht gegeben.
- ✅ `BLIND09-E002` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan CAPA-24-0188 definiert eine dokumentierte Wirksamkeitsprüfung (Effectiveness Check) für die präventiven Maßnahmen. Das Kriterium und der Prüfumfang sind konkret benannt, und die Verantwortung liegt bei QA.
- ✅ `BLIND09-E003` (low) — gefunden via evidence_substring (Score 1.0): Der Change-Control-Auszug CC-24-0071 enthält eine dokumentierte Auswirkungsbewertung ('regulatorische Auswirkungen: keine') und eine Validierungsbewertung (Regressionstest des Fälligkeitslaufs). Die 'no impact'-Bewertung ist begründet.
- ✅ `BLIND09-E004` (medium) — gefunden via evidence_fuzzy (Score 0.436): Dieselbe Tätigkeit ('Filterintegritätstest nach Abfüllung durchgeführt für Charge Optril, OP-24-0501') ist von unterschiedlichen Personen gezeichnet: MS, MSt. Ohne dokumentierte Erklärung ist die Zurechenbarkeit nicht gegeben.
- ⚠️ Decoy `BLIND09-D003` fälschlich beanstandet: Dieselbe Tätigkeit ('Filterintegritätstest nach Abfüllung durchgeführt für Charge Optril, OP-24-0501') ist von unterschiedlichen Personen gezeichnet: MS, MSt. Ohne dokumentierte Erklärung ist die Zurechenbarkeit nicht gegeben.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `BLIND10-E005` (medium) — gefunden via evidence_fuzzy (Score 0.535): Die Dokumente belegen, dass das Formatteil FT-SP3-11 aufgrund überschrittener Laufleistung getauscht wurde. Es gibt jedoch keine explizite Dokumentation, die bestätigt, dass die Validierungs-, Reinigungsvalidierungs- oder Sterilisationsnachweise den aktuellen Zustand des Formatteils oder des Stopfensetzers SP-3 abdecken. Der CAPA-Plan erwähnt korrektive Maßnahmen, aber keinen aktuellen Validierungsbericht oder eine Übertragbarkeitsbegründung für das neue oder getauschte Formatteil.
- ❌ `BLIND10-E001` (critical) — übersehen: Der Gehalt von 106,2 % der Deklaration liegt außerhalb der Spezifikation 95,0–105,0 % (PV-ZEN-007, Abschnitt 3.2), ist im Prüfprotokoll PP-24-0911 aber als 'entspricht' bewertet.
- ❌ `BLIND10-E002` (high) — übersehen: Der Freigabevermerk FGV-24-0217 (04.10.2024) referenziert die Endprüfung PP-24-0911 als abgeschlossen, obwohl deren Prüfabschluss erst am 07.10.2024 erfolgte; die zeitliche Abfolge ist nicht plausibel.
- ❌ `BLIND10-E003` (high) — übersehen: Die im Freigabevermerk behauptete Sichtung der Umgebungsmonitoring-Daten vom 24.09.2024 ist durch keinen Nachweis im Paket belegt.
- ❌ `BLIND10-E004` (medium) — übersehen: Die Abweichung DEV-24-0221 wurde erst am 02.10.2024 und damit außerhalb der 3-Arbeitstage-Frist der SOP-QM-0119 eröffnet; eine Begründung fehlt.
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
