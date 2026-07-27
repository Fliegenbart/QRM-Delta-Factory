# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid` | Engine: `requirement`
- Zeitpunkt: 2026-07-27T13:53:36+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 19 von 34 versteckten Fehlern gefunden (56%)
- **In Prüfmappe sichtbar:** 18 von 34 versteckten Fehlern (53%)
- **Spezifität (Decoys):** 32 von 32 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 23 von 88 (26%) — 17 als Treffer gewertet, 6 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 65 von 88 (74%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 8.8 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 48 von 88 Findings mit verifiziertem Zitat (55%)

## Qualitätsmetriken

- Must-detect Recall: `0.5588`
- Wiederholungen: `6` (Redundanzrate `0.2609`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `5/8/6`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 50 | 88,726 | 23,265 | 111,991 |
| mistral | 50 | 278,280 | 143,712 | 421,992 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed_with_model_failures | 0 | 11 | 2 | 6 | 3/3 | 3/3 | 0/3 | - |
| CASE_02 | completed | 0 | 10 | 1 | 7 | 2/3 | 2/3 | 0/3 | - |
| CASE_03 | completed | 0 | 12 | 2 | 7 | 4/4 | 4/4 | 0/3 | - |
| CASE_04 | completed | 0 | 11 | 0 | 9 | 2/3 | 2/3 | 0/3 | - |
| CASE_05 | completed_with_model_failures | 0 | 6 | 0 | 6 | 0/4 | 0/4 | 0/3 | - |
| CASE_06 | completed_with_model_failures | 0 | 7 | 0 | 6 | 1/3 | 1/3 | 0/3 | - |
| CASE_07 | completed | 0 | 8 | 1 | 6 | 1/1 | 1/1 | 0/5 | - |
| CASE_08 | completed_with_model_failures | 0 | 6 | 0 | 5 | 1/4 | 1/4 | 0/3 | - |
| CASE_09 | completed | 0 | 5 | 0 | 3 | 3/4 | 2/4 | 0/3 | - |
| CASE_10 | completed | 0 | 12 | 0 | 10 | 2/5 | 2/5 | 0/3 | - |

## Modellausfälle

- **ProviderCallError** (2×): mistral provider output was truncated
  - betroffen: CASE_05/extract:7, CASE_08/extract:7
- **ProviderStructuredOutputError** (1×): 9 validation errors for RequirementGroupOutput
requirement_id
  Extra inputs are not permitted [type=extra_forbidden, input_value='req_cc_impact_and_validation'
  - betroffen: CASE_01/assess:0
- **ProviderStructuredOutputError** (1×): 1 validation error for RequirementGroupOutput
verdicts.3.status
  Input should be 'fulfilled', 'violated', 'unclear' or 'not_applicable' [type=enum, input_value
  - betroffen: CASE_06/assess:1

### CASE_01

- ✅ `BLIND01-E001` (critical) — gefunden via evidence_substring (Score 1.0): Der IPC-Wert K-14 (Bruchfestigkeit 92 N) überschreitet die spezifizierte obere Grenze von 90 N. Dies stellt eine Überschreitung eines kritischen Prozessparameters dar, die als Abweichung zu bewerten ist, auch wenn das Produkt visuell unauffällig erscheint. Die Überschreitung ist im BMR dokumentiert, wurde aber nicht als separate Abweichung behandelt.
- ✅ `BLIND01-E002` (medium) — gefunden via evidence_substring (Score 1.0): Modelllauf für diese Anforderungsgruppe fehlgeschlagen; die Anforderung bleibt unbeurteilt und gehört zur menschlichen Prüfung.
- ✅ `BLIND01-E003` (high) — gefunden via evidence_fuzzy (Score 0.613): Der Audit-Trail des Steuerungssystems der Tablettenpresse TP-03 wurde für den relevanten Zeitraum überprüft und es wurden keine Auffälligkeiten hinsichtlich manueller Eingriffe oder nachträglicher Änderungen festgestellt. Dies belegt den durchgeführten Audit-Trail-Review.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `BLIND02-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Freigabe der Charge NX-24-0342 erfolgte erst nach Abschluss der Abweichungsbewertung, des Impact Assessments und der QA-Freigabe. Der QA-Freigabevermerk (FGV-24-0142) datiert vom 18.04.2024, während die Abweichung DEV-24-0129 bereits am 05.04.2024 eröffnet und die QA-Prüfung am 03.04.2024 (falsches Datum im Dokument, korrigiert durch Kontext) durchgeführt wurde. Die Zusatzprüfungen (PA-24-1174 und PA-24-1175) und die CAPA-Maßnahmen (CAPA-24-0091) waren ebenfalls abgeschlossen.
- ✅ `BLIND02-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die SOP-PRD-0221 wurde im Rahmen der CAPA-Maßnahme M1 revidiert (Ergänzung einer Funktionsprüfung des Zuluftventils YV-207 vor Chargenstart). Es gibt jedoch keinen Nachweis, dass das betroffene Personal vor der nächsten Charge nachweislich und wirksam geschult wurde. Der Auslöser (SOP-Revision) ist belegt, der geforderte Schulungsnachweis fehlt.
- ❌ `BLIND02-E002` (critical) — übersehen: Der Ausgangsstoff Lactose-Monohydrat (LM-24-0301) wurde am 02.04.2024 verarbeitet, obwohl die Freigabe erst am 04.04.2024 erteilt wurde; eine Bewertung dieses Sachverhalts fehlt vollständig.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `BLIND03-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Gehaltsmessungen (8,52 mg/ml und 8,38 mg/ml) wurden gegen die interne Spezifikation (7,6–8,4 mg/ml) bewertet. Obwohl der erste Wert (8,52 mg/ml) die obere Spezifikationsgrenze überschreitet, wurde dies als Abweichung DEV-24-0141 behandelt. Die Wiederholungsmessung (8,38 mg/ml) lag innerhalb der Spezifikation, was die Einhaltung der Akzeptanzkriterien bestätigt. Die Bewertung erfolgte gemäß der Prüfvorschrift PV-TAV-011 und ist im QC-Prüfprotokoll PP-24-0618 dokumentiert.
- ✅ `BLIND03-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Aufzeichnungen vollständig, konsistent und original sein müssen (ALCOA+). Der Abweichungsbericht (document_01_abweichungsbericht.md) wurde erst am 14.05.2024 eröffnet, obwohl die Abweichung bereits am 06.05.2024 festgestellt wurde. Gemäß SOP-QM-0107 (document_05_sop_auszug_meldewesen.md) hätte die Eröffnung innerhalb von 2 Arbeitstagen nach Feststellung erfolgen müssen. Die verspätete Eröffnung stellt eine Verletzung der zeitgleichen Dokumentation dar. Zudem fehlt im CAPA-Plan (document_03_capa_plan.md) die finale Genehmigung durch QA (leerer Unterschriftenblock). Damit sind die Aufzeichnungen weder vollständig noch zeitgleich.
- ✅ `BLIND03-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Herstellvorschrift HV-TAV-002 wurde durch Maßnahme M1 des CAPA-Plans (CAPA-24-0104) ergänzt, um eine verbindliche Mindestmischzeit von 30 Minuten vor der ersten IPC-Probenahme festzulegen. Die Unterweisung des Herstellpersonals zur geänderten Herstellvorschrift ist zwar als Maßnahme M2 geplant, jedoch fehlt der Nachweis, dass das betroffene Personal vor Ausführung der geänderten Tätigkeit nachweislich und wirksam geschult wurde. Die Schulung ist erst für den 12.07.2024 terminiert, während die Abweichung bereits am 06.05.2024 auftrat und die Maßnahme M1 bis zum 28.06.2024 umgesetzt werden soll. Dies stellt einen Verstoß gegen die Anforderung dar, da die Schulung vor der Umsetzung der geänderten SOP erfolgen muss.
- ✅ `BLIND03-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Aufzeichnungen vollständig, konsistent und original sein müssen (ALCOA+). Der Abweichungsbericht (document_01_abweichungsbericht.md) wurde erst am 14.05.2024 eröffnet, obwohl die Abweichung bereits am 06.05.2024 festgestellt wurde. Gemäß SOP-QM-0107 (document_05_sop_auszug_meldewesen.md) hätte die Eröffnung innerhalb von 2 Arbeitstagen nach Feststellung erfolgen müssen. Die verspätete Eröffnung stellt eine Verletzung der zeitgleichen Dokumentation dar. Zudem fehlt im CAPA-Plan (document_03_capa_plan.md) die finale Genehmigung durch QA (leerer Unterschriftenblock). Damit sind die Aufzeichnungen weder vollständig noch zeitgleich.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `BLIND04-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen im BMR-Auszug (Abschnitt 5) sind vollständig, zeitgleich dokumentiert und durch Unterschriften bestätigt. Es gibt keine Hinweise auf fehlende oder nachträglich veränderte Originaldaten.
- ✅ `BLIND04-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahmen (CAPA-24-0133) sind mit einem Qualitätsrisiko verknüpft (verwechslungsanfällige Lagerung von Siebeinsätzen), jedoch fehlt eine definierte und dokumentierte Wirksamkeitsprüfung. Der CAPA-Plan enthält lediglich den Hinweis: "Umfang, Kriterium und Termin der Wirksamkeitsprüfung: wird festgelegt." Dies belegt, dass die Wirksamkeitsprüfung zum Zeitpunkt der Erstellung des Plans nicht definiert war, was einen Verstoß gegen die Anforderung darstellt.
- ❌ `BLIND04-E001` (high) — übersehen: Die Magnesiumstearat-Einwaage von 1,20 kg entspricht 0,60 % der Ansatzmasse (200,0 kg) und überschreitet die SOP-Vorgabe von 0,45–0,55 %; die Konformitätskennzeichnung im BMR ist falsch.
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ❌ `BLIND05-E001` (medium) — übersehen: Für 03:20 Uhr am 09.07.2024 dokumentieren Abweichungsbericht (Umlagerungsbeginn L-02) und Klimatrendbericht (Kontrollmessung L-14) unvereinbare gleichzeitige Handlungen derselben Person (BD).
- ❌ `BLIND05-E002` (critical) — übersehen: Die Bulkcharge SV-24-0619 war laut Belegungsliste während der Exkursion in Raum L-02, fehlt aber in der Chargen-Impact-Bewertung IMP-24-0064; die Aussage 'alle betroffenen Chargen wurden bewertet' ist falsch.
- ❌ `BLIND05-E003` (medium) — übersehen: Im CAPA-Plan CAPA-24-0147 verweist das Feld 'Wirksamkeitsprüfung durch' auf 'siehe oben', ohne dass dort ein Verantwortlicher für die Wirksamkeitsprüfung benannt ist.
- ❌ `BLIND05-E004` (high) — übersehen: Die in IMP-24-0064 verwendete Expositionsdauer (3,5 Stunden) widerspricht der im Trendbericht dokumentierten Überschreitungsdauer (6,5 Stunden); die Impact-Argumentation stützt sich auf falsche Daten.
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `BLIND06-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die interne Spezifikation RS-KB-002, Rev. 05 wird im Abweichungsbericht (Dokument 01) zitiert und die Prüfergebnisse der Nachbeprobung (Partikelbefund nur in Gebinde 2, Wassergehalt 0,44 % vs. NMT 0,5 %) sowie das Lieferantenzertifikat (Sulfatasche 0,14 % vs. NMT 0,10 %) werden explizit gegen diese Spezifikation bewertet. Die Sulfatasche überschreitet zwar die interne Spezifikation, wird jedoch im CoA des Lieferanten als 'complies' ausgewiesen. Die QA-Bewertung (Dokument 04) bestätigt, dass die Abweichung auf Gebinde 2 begrenzt ist und die Charge KL-24-0288 aus konformen Gebinden hergestellt wurde. Damit ist die Anforderung erfüllt, da die Mess- und Prüfergebnisse gegen die interne Spezifikation bewertet wurden, auch wenn das Lieferantenzertifikat eine Abweichung (Sulfatasche) nicht korrekt abbildet.
- ❌ `BLIND06-E002` (medium) — übersehen: Die behauptete Nachprüfung des Chargenprotokolls der Vorcharge KL-24-0251 ist durch keinen referenzierbaren Nachweis belegt.
- ❌ `BLIND06-E003` (high) — übersehen: Die Nachbeprobung vom 20.06.2024 erfolgte nach SOP-WAR-0033 Rev. 04, deren Inkraftsetzung und Schulung laut CAPA-Plan erst zum 01.07.2024 vorgesehen ist; es wurde eine nicht in Kraft gesetzte SOP-Version angewendet.
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `BLIND07-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass elektronische Unterschriften Name, Datum, Zeit und Bedeutung enthalten und zeitlich plausibel sind. Im Verpackungsprotokoll (chunk_0d6a24d9bf1f45aa8e9b5f5e731b97a6_p1) fehlt bei der Abschlusskontrolle die Unterschrift des Prüfers: 'Geprüft von: ____________ Datum: 22.06.2024'. Dies stellt einen Verstoß gegen die Plausibilität und Vollständigkeit der Signaturdaten dar. Zudem ist der Nachtrag vom 24.06.2024 zwar gegengezeichnet, aber die ursprüngliche Lücke bleibt bestehen und ist nicht nachvollziehbar dokumentiert.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `BLIND08-E002` (high) — gefunden via evidence_fuzzy (Score 0.565): Der Audit-Trail-Export des Coater-Leitsystems wurde geprüft und deckt den Prozesszeitraum der Charge MV-24-0821 vollständig ab. Es gibt keine Hinweise auf manuelle Parameteränderungen außerhalb der dokumentierten Ereignisse, was den risikobasierten Audit-Trail-Review belegt.
- ❌ `BLIND08-E001` (high) — übersehen: Der als Erledigungsnachweis für CAPA M2 angeführte Schulungsnachweis SN-CO-24-019 belegt eine Schulung auf SOP-COA-0110 Rev. 04 statt der seit 01.08.2024 gültigen Rev. 05; der CAPA-Abschluss ist nicht nachgewiesen.
- ❌ `BLIND08-E003` (high) — übersehen: Die Zulufttemperatur von 62.8 °C (12:30 Uhr) überschreitet das Prozessfenster 58,0–62,0 °C der SOP-COA-0110, ist im Coatingprotokoll jedoch als konform vermerkt und nirgends bewertet.
- ❌ `BLIND08-E004` (medium) — übersehen: Die Aussage des Abweichungsberichts, die Sprührate habe nie über 520 g/min gelegen, widerspricht dem protokollierten Wert von 545 g/min um 10:42 Uhr.
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `BLIND09-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Mess- und Prüfergebnisse gegen die gültige interne Spezifikation bewertet werden und eine Verletzung interner Akzeptanzkriterien als Abweichung behandelt wird. Im vorliegenden Fall wurde das Filterintegritätstestgerät FIT-2 nach Ablauf der Kalibrierfrist (31.08.2024) weiterhin genutzt (Chunk chunk_da0b8d8c27ce4b9bbdb06a8bfa5a53eb_p1, Nutzungseinträge 05.09.-18.09.2024). Die Nachkalibrierung ergab zwar keine Abweichung ('as found' ohne Befund, Chunk chunk_2e11a075a6b24b188c80617833bd2b6c_p1), jedoch fehlt der Nachweis, dass die im überfälligen Zeitraum durchgeführten Tests (z. B. für Chargen OP-24-0501 bis OP-24-0503) explizit gegen die internen Akzeptanzkriterien bewertet wurden. Die bloße Feststellung 'Testparameter im Protokoll plausibel, Grenzwertreserve > 25 %' (Chunk chunk_2e11a075a6b24b188c80617833bd2b6c_p1) ersetzt keine dokumentierte Bewertung gegen die Spezifikation. Die Nutzung eines nicht kalibrierten Geräts stellt zudem eine Verletzung der GMP-Anforderungen dar, unabhängig vom Testergebnis.
- ✅ `BLIND09-E002` (medium) — gefunden via evidence_fuzzy (Score 0.467): Die Anforderung verlangt, dass bei einer SOP-Änderung das betroffene Personal nachweislich und wirksam geschult sein muss, bevor die geänderte Tätigkeit ausgeführt wird. Im Change-Control-Auszug CC-24-0071 (Chunk chunk_ff4c88b932544d2ea92fdf95bfb193ef_p1) wird die Umstellung der Kalibrierplanung auf risikobasierte Intervalle und automatisierte Fälligkeitsläufe beschrieben. Die Maßnahme M3 im CAPA-Plan (Chunk chunk_e8c160e105ab4b0eaa3e8e7a0d1f2fcb_p1) sieht eine Unterweisung der Bereichsleitungen zur wöchentlichen Prüfung des Kalibrier-Kontrollreports vor, jedoch ist diese zum Zeitpunkt der Abweichung (21.09.2024) noch nicht durchgeführt (Termin: 13.12.2024). Es fehlt der Nachweis, dass das Personal vor der Umsetzung der geänderten Kalibrierplanung (z. B. manueller Abgleich der Fälligkeitsliste bei Systemupdates) wirksam geschult wurde. Die Abweichung DEV-24-0205 (Chunk chunk_7b10d4d300d344188c80ca11e15543bc_p1) wurde durch ein fehlendes Systemupdate ausgelöst, was auf eine mangelnde Schulung oder unzureichende SOP-Umsetzung hindeutet.
- ✅ `BLIND09-E003` (low) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass bei einer SOP-Änderung das betroffene Personal nachweislich und wirksam geschult sein muss, bevor die geänderte Tätigkeit ausgeführt wird. Im Change-Control-Auszug CC-24-0071 (Chunk chunk_ff4c88b932544d2ea92fdf95bfb193ef_p1) wird die Umstellung der Kalibrierplanung auf risikobasierte Intervalle und automatisierte Fälligkeitsläufe beschrieben. Die Maßnahme M3 im CAPA-Plan (Chunk chunk_e8c160e105ab4b0eaa3e8e7a0d1f2fcb_p1) sieht eine Unterweisung der Bereichsleitungen zur wöchentlichen Prüfung des Kalibrier-Kontrollreports vor, jedoch ist diese zum Zeitpunkt der Abweichung (21.09.2024) noch nicht durchgeführt (Termin: 13.12.2024). Es fehlt der Nachweis, dass das Personal vor der Umsetzung der geänderten Kalibrierplanung (z. B. manueller Abgleich der Fälligkeitsliste bei Systemupdates) wirksam geschult wurde. Die Abweichung DEV-24-0205 (Chunk chunk_7b10d4d300d344188c80ca11e15543bc_p1) wurde durch ein fehlendes Systemupdate ausgelöst, was auf eine mangelnde Schulung oder unzureichende SOP-Umsetzung hindeutet.
- ❌ `BLIND09-E004` (medium) — übersehen: Für die Gerätesperrung des FIT-2 am 21.09.2024 nennen Abweichungsbericht (HV) und Gerätelogbuch (RE) unterschiedliche Kürzel; RE ist in der referenzierten Unterschriftenliste nicht geführt.
- ℹ️ 3 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `BLIND10-E001` (critical) — gefunden via evidence_substring (Score 1.0): Der Messwert 106,2 % der Deklaration für 'Gehalt Zentrivamesilat' liegt außerhalb der deklarierten Grenze (Bereich 95,0–105,0).
- ✅ `BLIND10-E005` (medium) — gefunden via evidence_fuzzy (Score 0.535): Die Dokumente belegen, dass das Formatteil FT-SP3-11 aufgrund überschrittener Laufleistung ausgetauscht wurde. Es gibt jedoch keine explizite Aussage, ob die Validierungs-, Reinigungsvalidierungs- oder Sterilisationsnachweise den aktuellen Zustand des Formatteils (nach Austausch) abdecken. Die Übertragbarkeit der bestehenden Validierung auf das neue Formatteil ist nicht dokumentiert. Der Auslöser (Formatteilaustausch) ist belegt, der geforderte Nachweis fehlt jedoch.
- ❌ `BLIND10-E002` (high) — übersehen: Der Freigabevermerk FGV-24-0217 (04.10.2024) referenziert die Endprüfung PP-24-0911 als abgeschlossen, obwohl deren Prüfabschluss erst am 07.10.2024 erfolgte; die zeitliche Abfolge ist nicht plausibel.
- ❌ `BLIND10-E003` (high) — übersehen: Die im Freigabevermerk behauptete Sichtung der Umgebungsmonitoring-Daten vom 24.09.2024 ist durch keinen Nachweis im Paket belegt.
- ❌ `BLIND10-E004` (medium) — übersehen: Die Abweichung DEV-24-0221 wurde erst am 02.10.2024 und damit außerhalb der 3-Arbeitstage-Frist der SOP-QM-0119 eröffnet; eine Begründung fehlt.
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
