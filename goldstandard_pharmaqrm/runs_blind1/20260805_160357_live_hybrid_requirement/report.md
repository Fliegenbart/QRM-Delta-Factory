# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid` | Engine: `requirement`
- Zeitpunkt: 2026-08-05T16:03:57+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 25 von 34 versteckten Fehlern gefunden (74%)
- **In Prüfmappe sichtbar:** 25 von 34 versteckten Fehlern (74%)
- **Spezifität (Decoys):** 29 von 32 Decoys korrekt nicht beanstandet (91%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 42 von 150 (28%) — 23 als Treffer gewertet, 19 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 108 von 150 (72%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 15.0 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 87 von 150 Findings mit verifiziertem Zitat (58%)

## Qualitätsmetriken

- Must-detect Recall: `0.7353`
- Wiederholungen: `19` (Redundanzrate `0.4524`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `10/10/5`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 66 | 118,715 | 32,898 | 151,613 |
| mistral | 99 | 447,425 | 208,939 | 656,364 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 16 | 4 | 9 | 3/3 | 3/3 | 0/3 | - |
| CASE_02 | completed | 0 | 16 | 2 | 12 | 2/3 | 2/3 | 0/3 | - |
| CASE_03 | completed | 0 | 17 | 2 | 13 | 2/4 | 2/4 | 0/3 | - |
| CASE_04 | completed | 0 | 14 | 2 | 9 | 3/3 | 3/3 | 1/3 | - |
| CASE_05 | completed | 0 | 15 | 5 | 7 | 4/4 | 4/4 | 0/3 | - |
| CASE_06 | completed | 0 | 11 | 0 | 9 | 2/3 | 2/3 | 1/3 | - |
| CASE_07 | completed | 0 | 12 | 0 | 12 | 0/1 | 0/1 | 0/5 | - |
| CASE_08 | completed | 0 | 18 | 3 | 12 | 4/4 | 4/4 | 0/3 | - |
| CASE_09 | completed | 0 | 14 | 0 | 11 | 3/4 | 3/4 | 0/3 | - |
| CASE_10 | completed | 0 | 17 | 1 | 14 | 2/5 | 2/5 | 1/3 | - |

### CASE_01

- ✅ `BLIND01-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen erfüllen die ALCOA+-Kriterien. Die IPC-Daten im BMR sind vollständig, zeitgleich dokumentiert, signiert und konform. Der Audit-Trail wurde überprüft und wies keine Lücken oder nachträglichen Änderungen auf. Die Originaldaten sind verfügbar und konsistent.
- ✅ `BLIND01-E002` (medium) — gefunden via evidence_substring (Score 1.0): Das Modell hat für diese Anforderung kein Verdict geliefert; sie bleibt unbeurteilt.
- ✅ `BLIND01-E003` (high) — gefunden via evidence_fuzzy (Score 0.613): Der Audit-Trail des Steuerungssystems der Tablettenpresse TP-03 wurde für den relevanten Zeitraum überprüft und es wurden keine Auffälligkeiten hinsichtlich manueller Eingriffe oder nachträglicher Änderungen festgestellt. Dies belegt den durchgeführten Audit-Trail-Review.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `BLIND02-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Charge NX-24-0342 wurde erst nach Abschluss der Abweichungsbewertung, des Impact Assessments und der QA-Freigabe freigegeben. Der QA-Freigabevermerk (FGV-24-0142) datiert vom 18.04.2024 und bestätigt, dass die Bewertung abgeschlossen ist. Die Abweichung DEV-24-0129 wurde am 05.04.2024 eröffnet und die QA-Prüfung am 03.04.2024 durchgeführt (korrigiert: tatsächlich am 18.04.2024, siehe Freigabevermerk). Die Freigabe erfolgte somit erst nach Abschluss aller erforderlichen Schritte.
- ✅ `BLIND02-E003` (medium) — gefunden via evidence_substring (Score 1.0): Jede CAPA-Maßnahme im CAPA-Plan (CAPA-24-0091) hat einen benannten Verantwortlichen und einen plausiblen Umsetzungstermin. Beispielhaft sind M1 (N. Duran, 31.05.2024), M2 (B. Hofmann, 09.04.2024) und M3 (B. Hofmann, 30.09.2024) aufgeführt. Die Termine sind realisierbar und im Plan dokumentiert.
- ❌ `BLIND02-E002` (critical) — übersehen: Der Ausgangsstoff Lactose-Monohydrat (LM-24-0301) wurde am 02.04.2024 verarbeitet, obwohl die Freigabe erst am 04.04.2024 erteilt wurde; eine Bewertung dieses Sachverhalts fehlt vollständig.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `BLIND03-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass QA-Freigaben und Genehmigungen vor Abschluss dokumentiert vorliegen. Im CAPA-Plan (CAPA-24-0104) ist der Genehmigungsblock für QA zwar vorgesehen, aber nicht unterschrieben. Die QA-Bewertung (QAB-24-0121) wurde zwar von QA erstellt, ersetzt jedoch nicht die fehlende Genehmigung des CAPA-Plans durch QA.
- ✅ `BLIND03-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Bewertung QAB-24-0121 bestätigt die Bewertung des Sachverhalts und die Auswirkung auf die Charge TV-24-0518. Es wird explizit festgestellt, dass der Ansatz durchgehend innerhalb der zulässigen Standzeit war und die Sperrung im ERP-System unverzüglich erfolgte. Die Charge TV-24-0518 ist die einzige betroffene Charge, was durch den Abweichungsbericht DEV-24-0141 und die QA-Bewertung belegt ist.
- ❌ `BLIND03-E001` (critical) — übersehen: Der Gehaltswert IPC-1 (8,52 mg/ml) überschreitet die Spezifikation von 7,6–8,4 mg/ml, ist im Prüfprotokoll PP-24-0618 jedoch als 'entspricht' bewertet; die Konformitätsbewertung ist falsch.
- ❌ `BLIND03-E003` (medium) — übersehen: Der in der QA-Bewertung behauptete vollständige Schulungsstand ist durch keinen Nachweis im Paket belegt und steht im Spannungsfeld zur erst geplanten Unterweisung M2.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 13 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `BLIND04-E001` (high) — gefunden via evidence_substring (Score 1.0): Die kritischen Prozessparameter liegen innerhalb der spezifizierten Grenzen. Die Trocknungstemperatur (59,5 °C) liegt im zulässigen Bereich von 50–60 °C (SOP-Auszug, document_03_sop_auszug_granulation.md). Die Einwaagen von Magnesiumstearat (1,20 kg) und hochdispersem Siliciumdioxid (0,40 kg) entsprechen den Vorgaben der SOP (0,45–0,55 % bzw. 0,15–0,25 % der Ansatzmasse von 200,0 kg). Die Korngrößenverteilung der wiederaufgearbeiteten Teilmenge wurde geprüft und lag innerhalb der Vorgaben (QA-Bewertung, document_05_qa_bewertung.md).
- ✅ `BLIND04-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Bewertung QAB-24-0158 enthält eine dokumentierte Bewertung des Chargen-Impacts. Es wird bestätigt, dass die Korngrößenverteilung der wiederaufgearbeiteten Teilmenge innerhalb der Vorgaben liegt und der Chargen-Impact als nicht gegeben bewertet wird. Zudem wird die Freigabe der Charge DL-24-0733 explizit erklärt.
- ✅ `BLIND04-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahmen (CAPA-24-0133) adressieren ein Qualitätsrisiko (verwechslungsanfällige Lagerung von Siebeinsätzen), jedoch fehlt eine definierte und dokumentierte Wirksamkeitsprüfung (Effectiveness Check). Der CAPA-Plan (document_04_capa_plan.md) enthält lediglich den Eintrag: "Umfang, Kriterium und Termin der Wirksamkeitsprüfung: wird festgelegt." Dies stellt einen Verstoß gegen die Anforderung dar, da die Wirksamkeitsprüfung zum Zeitpunkt der Dokumentation nicht konkretisiert ist.
- ⚠️ Decoy `BLIND04-D001` fälschlich beanstandet: Die Freigabeentscheidung für die Charge DL-24-0733 ist begründet und mit dem Batch Record verknüpft. Die QA-Bewertung (document_05_qa_bewertung.md) enthält eine explizite Freigabeerklärung: "Hiermit erkläre ich, dass die Abweichung DEV-24-0166 vollständig bewertet wurde und der Weiterverarbeitung der Charge DL-24-0733 aus Sicht der Qualitätssicherung nichts entgegensteht." Zudem wird die Charge im Batch Manufacturing Record (document_02_bmr_auszug.md) mit allen relevanten Prozessdaten dokumentiert. Die Verknüpfung ist somit gegeben.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `BLIND05-E001` (medium) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen erfüllen die ALCOA+-Kriterien: Sie sind zurechenbar (z. B. durch Unterschriften wie 'B. Dahlke (BD)', 'Dr. I. Behrens (IB)'), lesbar, zeitgleich (z. B. Datum und Uhrzeit der Sofortmaßnahmen), original (Dokumente sind als Originale in der Fallmappe enthalten), korrekt (Messwerte und Bewertungen sind plausibel und konsistent), vollständig (alle relevanten Chargen und Maßnahmen sind dokumentiert), konsistent (z. B. Klimadaten und Belegungsliste stimmen überein) und dauerhaft verfügbar (Dokumente sind in der Fallmappe archiviert).
- ✅ `BLIND05-E002` (critical) — gefunden via evidence_fuzzy (Score 0.506): Die Aufzeichnungen erfüllen die ALCOA+-Kriterien: Sie sind zurechenbar (z. B. durch Unterschriften wie 'B. Dahlke (BD)', 'Dr. I. Behrens (IB)'), lesbar, zeitgleich (z. B. Datum und Uhrzeit der Sofortmaßnahmen), original (Dokumente sind als Originale in der Fallmappe enthalten), korrekt (Messwerte und Bewertungen sind plausibel und konsistent), vollständig (alle relevanten Chargen und Maßnahmen sind dokumentiert), konsistent (z. B. Klimadaten und Belegungsliste stimmen überein) und dauerhaft verfügbar (Dokumente sind in der Fallmappe archiviert).
- ✅ `BLIND05-E003` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan CAPA-24-0147 definiert eine Wirksamkeitsprfung mit klaren Kriterien (erfolgreicher dokumentierter Alarmkettentest ber zwei aufeinanderfolgende Halbjahresintervalle) und einem Termin fr die Erstbewertung (31.03.2025). Die Mafnahme M3 (prventiver Funktionstest) ist direkt auf die Wirksamkeitsprfung ausgerichtet.
- ✅ `BLIND05-E004` (high) — gefunden via evidence_substring (Score 1.0): Die Einstufung der Abweichung als 'schwerwiegend (major)' ist durch eine nachvollziehbare Risikobewertung belegt. Der Abweichungsbericht DEV-24-0180 bestätigt die Klassifizierung durch QA und verweist auf die Feuchteexkursion mit einer Dauer von 6,5 Stunden und einem Maximum von 71 % rF. Die Bewertung der Chargen-Impact-Bewertung IMP-24-0064 stützt diese Einstufung durch physikalisch-chemische Daten (Wasseraufnahme-Stichproben).
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `BLIND06-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die interne Spezifikation RS-KB-002, Rev. 05, wird im Abweichungsbericht (document_01_abweichungsbericht.md) zitiert und die Prüfergebnisse der Nachbeprobung (FTIR-Spektrum, Prüfbericht PB-24-0771) sowie das Analysenzertifikat des Lieferanten (CoA Nr. SFC-24-1834) werden gegen diese Spezifikation bewertet. Die Sulfatasche im CoA (0,14 %) überschreitet zwar die interne Spezifikation (NMT 0,10 %), wird jedoch im Abweichungsbericht als konform zum Lieferantenzertifikat behandelt. Da die interne Spezifikation jedoch als verbindlich genannt wird, liegt hier ein Verstoß vor, der im Abweichungsbericht dokumentiert und bewertet wird (Gebinde 2 gesperrt). Die Bewertung der Abweichung gegen die interne Spezifikation ist somit erfolgt.
- ✅ `BLIND06-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Bewertung (document_04_qa_bewertung.md) bestätigt eine dokumentierte Auswirkungsbewertung der Abweichung DEV-24-0152 auf die Charge KL-24-0288. Es wird explizit festgestellt, dass die Charge ausschließlich aus unauffälligen Gebinden hergestellt wurde und die In-Prozess-Kontrollen konform sind. Zudem wird der Ausschluss eines Impacts auf die Charge KL-24-0288 sowie die Vorcharge KL-24-0251 geprüft und bestätigt. Dies erfüllt die Anforderung einer dokumentierten Bewertung der Auswirkung auf Produktqualität und Patientensicherheit, einschließlich aller potenziell betroffenen Chargen.
- ❌ `BLIND06-E003` (high) — übersehen: Die Nachbeprobung vom 20.06.2024 erfolgte nach SOP-WAR-0033 Rev. 04, deren Inkraftsetzung und Schulung laut CAPA-Plan erst zum 01.07.2024 vorgesehen ist; es wurde eine nicht in Kraft gesetzte SOP-Version angewendet.
- ⚠️ Decoy `BLIND06-D001` fälschlich beanstandet: Die Freigabeentscheidung der Charge KL-24-0288 ist in der QA-Bewertung (QAB-24-0139) begründet und mit der Chargenhistorie verknüpft. Die Dispositionsentscheidung ist dokumentiert und unterschrieben.
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ❌ `BLIND07-E001` (high) — übersehen: Die Prüfsignatur des Abschnitts 4 im Verpackungsprotokoll VPR RV-24-0450 fehlt; das Feld 'Geprüft von' enthält nur ein Datum ohne Namen.
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `BLIND08-E001` (high) — gefunden via evidence_substring (Score 1.0): Jede CAPA-Maßnahme im CAPA-Plan (CAPA-24-0170) hat einen benannten Verantwortlichen und einen realistischen Umsetzungstermin. Die Maßnahmen M1 und M2 sind bereits abgeschlossen, M3 ist in Umsetzung mit Termin 30.09.2024.
- ✅ `BLIND08-E002` (high) — gefunden via evidence_fuzzy (Score 0.565): Der Audit-Trail-Export des Coater-Leitsystems wurde geprüft und deckt den Prozesszeitraum der Charge MV-24-0821 vollständig ab. Es gibt keine Hinweise auf manuelle Parameteränderungen außerhalb der dokumentierten Ereignisse, was den risikobasierten Audit-Trail-Review belegt.
- ✅ `BLIND08-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Sprührate lag zum Zeitpunkt 11:05 Uhr mit 310 g/min außerhalb des spezifizierten Prozessfensters von 450–550 g/min. Dies ist im BMR-Auszug dokumentiert und als Abweichung DEV-24-0198 referenziert. Die Überschreitung der Prozessparameter-Grenzen ist ein Verstoß, auch wenn das Produkt visuell unauffällig erschien.
- ✅ `BLIND08-E004` (medium) — gefunden via evidence_fuzzy (Score 0.733): Die Sprührate lag zum Zeitpunkt 11:05 Uhr mit 310 g/min außerhalb des spezifizierten Prozessfensters von 450–550 g/min. Dies ist im BMR-Auszug dokumentiert und als Abweichung DEV-24-0198 referenziert. Die Überschreitung der Prozessparameter-Grenzen ist ein Verstoß, auch wenn das Produkt visuell unauffällig erschien.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `BLIND09-E002` (medium) — gefunden via evidence_fuzzy (Score 0.467): Die Anforderung verlangt, dass bei einer SOP-Änderung das betroffene Personal nachweislich und wirksam geschult sein muss, bevor die geänderte Tätigkeit ausgeführt wird. Der Change-Control-Auszug CC-24-0071 beschreibt die Umstellung der Kalibrierplanung auf risikobasierte Intervalle und automatisierte Fälligkeitsläufe, was eine SOP-Änderung darstellt. Es gibt jedoch keine Nachweise (z. B. Schulungsprotokolle, Unterschriftenlisten) dafür, dass das betroffene Personal vor der Umsetzung der Änderungen geschult wurde. Die geplante Unterweisung (Maßnahme M3 im CAPA-Plan) ist für den 13.12.2024 terminiert, was nach der Umsetzung der Änderungen liegt.
- ✅ `BLIND09-E003` (low) — gefunden via evidence_substring (Score 1.0): Der Change-Control-Auszug CC-24-0071 enthält eine dokumentierte Auswirkungsbewertung ("regulatorische Auswirkungen: keine") und eine Validierungsbewertung (Regressionstest des Fälligkeitslaufs, Testplan VT-WPS-24-05). Die Bewertung ist begründet und von QA (Dr. E. Kortmann) genehmigt.
- ✅ `BLIND09-E004` (medium) — gefunden via evidence_fuzzy (Score 0.411): Jede Maßnahme im CAPA-Plan CAPA-24-0188 hat einen benannten Verantwortlichen und einen realistischen Umsetzungstermin. Beispiel: Maßnahme M2 (Systemhärtung) ist T. Brand (Metrologie) zugeordnet und bis 30.11.2024 terminiert.
- ❌ `BLIND09-E001` (critical) — übersehen: Die Charge OP-24-0503 wurde laut Gerätelogbuch am 18.09.2024 auf dem überfälligen FIT-2 getestet, fehlt aber in der Impact-Bewertung IMP-24-0081; die Vollständigkeitsaussage der Bewertung ist falsch.
- ℹ️ 11 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `BLIND10-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Plausibilität der elektronischen Unterschriften und Datumsangaben ist in den Dokumenten gegeben. Beispielsweise sind im Abfüllprotokoll (Auszug BMR ZN-24-0940) die Unterschriften mit Name, Datum und Uhrzeit versehen und zeitlich konsistent mit dem Prozessablauf (z. B. "Bestätigt: P. Kowarik (PK), 24.09.2024, 05:50 Uhr"). Zudem sind im QC-Prüfprotokoll (PP-24-0911) die Unterschriften mit Datum und Prüferkennung dokumentiert, was die Anforderungen an Name, Datum und Bedeutung der Signatur erfüllt.
- ✅ `BLIND10-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Auswirkungsbewertung der Abweichung auf Produktqualität und Patientensicherheit ist im QA-Freigabevermerk dokumentiert. Es wird bestätigt, dass die ausgeschleusten Vials vollständig verworfen wurden, die Mengenbilanz aufgeht und die Endprüfung der Charge gemäß Prüfprotokoll PP-24-0911 abgeschlossen ist. Zudem wird die 100%-Kamerakontrolle der Bördelung als Absicherung genannt.
- ❌ `BLIND10-E001` (critical) — übersehen: Der Gehalt von 106,2 % der Deklaration liegt außerhalb der Spezifikation 95,0–105,0 % (PV-ZEN-007, Abschnitt 3.2), ist im Prüfprotokoll PP-24-0911 aber als 'entspricht' bewertet.
- ❌ `BLIND10-E003` (high) — übersehen: Die im Freigabevermerk behauptete Sichtung der Umgebungsmonitoring-Daten vom 24.09.2024 ist durch keinen Nachweis im Paket belegt.
- ❌ `BLIND10-E005` (medium) — übersehen: Maßnahme M3 des CAPA-Plans CAPA-24-0203 enthält keinen Termin, obwohl der Plan genehmigt und die Maßnahme in Umsetzung ist.
- ⚠️ Decoy `BLIND10-D001` fälschlich beanstandet: Der Abweichungsbericht (DEV-24-0221) verweist auf die Line Clearance als Anlage 1 ("das ausgefüllte Formblatt liegt diesem Protokoll als Anlage 1 bei"). Diese Anlage ist jedoch in den bereitgestellten Dokumenten nicht enthalten. Damit fehlt ein referenzierter Pflichtanhang, was einen Verstoß gegen die Anforderung darstellt.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
