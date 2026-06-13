# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-06-13T12:07:54+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 25 von 25 versteckten Fehlern gefunden (100%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 213 von 234 Findings mit verifiziertem Zitat (91%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 10 | 124,675 | 82,444 | 207,119 |
| extraction:mistral | 10 | 34,849 | 27,765 | 62,614 |
| mistral | 70 | 733,725 | 218,550 | 952,275 |
| openai | 10 | 105,113 | 32,372 | 137,485 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 49 | 22 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_02 | needs_human_review | 22 | 19 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_03 | completed | 18 | 25 | 2/2 | 0/2 | human_review_required |
| CASE_04 | completed | 29 | 22 | 3/3 | 0/1 | human_review_required |
| CASE_05 | needs_human_review | 18 | 18 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_06 | needs_human_review | 21 | 19 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_07 | needs_human_review | 20 | 30 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_08 | needs_human_review | 32 | 26 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_09 | completed | 32 | 29 | 3/3 | 0/1 | human_review_required |
| CASE_10 | completed | 20 | 24 | 3/3 | 0/1 | human_review_required |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Freigabe der Abweichung DEV-2026-891 durch Dr. Anna Klar ist mit dem Datum 14.12.2026 dokumentiert, obwohl die Abweichung bereits am 12.03.2026 erfasst wurde. Dies stellt einen Datenintegritätsbefund dar, da das Freigabedatum in der Zukunft liegt und nicht mit dem Audit Trail konsistent ist.
- ✅ `ERR_01_02` (high) — gefunden via evidence_fuzzy (Score 0.442): Die Batch-Impact-Bewertung der Abweichung DEV-2026-891 listet nur die Charge XYL-2026-004A auf, ohne eine klare Verknüpfung der Freigabeentscheidung mit den Batch Records. Dies entspricht nicht den Anforderungen an die Vollständigkeit der Batch-Impact-Bewertung gemäß QRM Batch Impact Checkliste Abschnitt 3.2.
- ℹ️ 20 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Die Korrektur der Ausbeute von 96.47% auf 98.1% aufgrund eines unvollständigen Wiegebegleitscheins (Claim: '~~96.47%~~ -> Korrektur auf 98.1% da Wiegebegleitschein unvollständig war') ist dokumentiert, aber es fehlt eine detaillierte Risikobewertung der Abweichung. Eine Einstufung der Abweichung (Minor/Major/Kritisch) und eine Begründung mit physikalisch-chemischen Daten sind nicht vorhanden.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_fuzzy (Score 0.496): Die QA-Freigabe der Charge CPH-2026-991 durch Dr. Bernd Richter (10.04.2026) bestätigt, dass 'die Ausbeute der spezifizierten Vorgabe entspricht' und der 'Reinigungsvorgang ordnungsgemäß dokumentiert' wurde. Diese Freigabe erfolgte, obwohl im Batch Record eine nachträgliche, nicht QA-genehmigte Datenkorrektur (96,47% → 98,1%) vorliegt und kein Abweichungsbericht für den ursprünglichen OOS-Wert existiert. Die QA-Freigabe basiert damit auf einem nicht vollständig geklärten Sachverhalt und ist ohne Auflösung der Datenintegritätsfrage nicht valide.
- ℹ️ 17 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Fehlende Nachweise für die Durchführung einer Audit-Trail-Review der elektronischen Partikelzählerdaten im Rahmen der Abweichung DEV-QS-2026-014. Die Zeitstempel der Partikelmessung (14:15 Uhr) und des Mitarbeitereintritts (14:35 Uhr) sind zeitlich unplausibel, was auf ein potenzielles Datenintegritätsrisiko hindeutet.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme (CAPA-2026-014) verweist auf SOP-QS-REIN-001 Version 2.0 mit Gültigkeitsdatum 12.01.2018. Diese SOP ist zum Zeitpunkt der CAPA-Erstellung (April/Mai 2026) über 8 Jahre alt. Es besteht das Risiko, dass diese Version nicht mehr den aktuellen Prozesszustand, die aktuelle Ausrüstung oder aktuelle regulatorische Anforderungen abdeckt. Eine veraltete SOP-Version als Grundlage für eine CAPA-Maßnahme in einem Klasse-B-Reinraum ist gemäß req_gs_validation_coverage und req_gs_qa_approval_documented nicht zulässig, sofern keine Bestätigung der aktuellen Gültigkeit vorliegt.
- ℹ️ 23 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Es liegt keine dokumentierte Evidenz für einen Audit-Trail-Review der elektronischen Records (SCADA-Protokoll) im Zusammenhang mit der Abweichung DEV-P-2026-092 vor. Gemäß SOP-DI-002 (4.1) müssen elektronische Unterschriften und Datumsangaben ALCOA+ erfüllen, was eine Prüfung des Audit-Trails erfordert.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Die Root-Cause-Analyse der Abweichung DEV-P-2026-092 nennt 'Bedienerfehler' als Ursache, ohne dass dies durch dokumentierte Evidenz (z. B. Schulungsnachweise, Prozessüberwachungsdaten) belegt ist. Gemäß SOP-DEV-001 (6.2) sind Root-Cause-Angaben wie 'Bedienerfehler' nur mit belastbaren Nachweisen zulässig.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Widerspruch in der Spezifikationsüberschreitung: Die Produkttemperatur überschritt mit 44,5°C das spezifizierte Limit von 42,0°C, jedoch wird in der QA-Freigabe die Charge als 'qualitätskonform' und 'kein nennenswerter Substanzabbau' bewertet. Eine solche Bewertung ohne belastbare physikalisch-chemische Daten ist nicht GMP-konform.
- ℹ️ 19 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Es gibt keine dokumentierte Validierungsabdeckung für das aktuelle Beladungsmuster oder die verwendeten Materialien im Autoklavenzyklus ZYK-STER-992. Die letzte Re-Validierung des Autoklaven AT-442 erfolgte im Januar 2026, jedoch fehlt ein Nachweis, dass die aktuellen Beladungsmuster und Materialien durch diese Validierung abgedeckt sind.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Die elektronischen Signaturen und Datumsangaben im Zusammenhang mit dem Autoklavenzyklus ZYK-STER-992 sind zeitlich unplausibel. Der Mitarbeiter PNN-8812 betrat die Personenschleuse erst um 08:45 Uhr, jedoch wurden Aktivitäten im Autoklavenbereich bereits ab 08:15 Uhr dokumentiert. Dies stellt einen Datenintegritätsbefund dar.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Die elektronischen Signaturen und Datumsangaben im Zusammenhang mit dem Autoklavenzyklus ZYK-STER-992 sind zeitlich unplausibel. Der Mitarbeiter PNN-8812 betrat die Personenschleuse erst um 08:45 Uhr, jedoch wurden Aktivitäten im Autoklavenbereich bereits ab 08:15 Uhr dokumentiert. Dies stellt einen Datenintegritätsbefund dar.
- ℹ️ 16 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Der Wassergehalt der Rohstoffcharge CS-AMX-9982 (13,2%) überschreitet die interne Spezifikation von 11,5% bis 12,8% für Amoxicillin Trihydrat (Prüf-Spez-API-04). Diese Abweichung ist im Abweichungsbericht LAB-DEV-2026-031 dokumentiert, jedoch fehlt eine dokumentierte Risikobewertung (Minor/Major/Kritisch) sowie eine Impact-Assessment für die betroffene Charge. Die Freigabe der Formulierungscharge AMO-SUP-2026-01 erfolgte ohne Nachweis der Konformität mit den Spezifikationsgrenzen.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_fuzzy (Score 0.718): Es besteht ein Widerspruch zwischen dem im Analysenzertifikat des Lieferanten angegebenen Wassergehalt (13,2%) und der internen Spezifikation (11,5% bis 12,8%). Dieser Widerspruch wurde in der QA-Freigabe der Charge AMO-SUP-2026-01 nicht konsistent adressiert. Angaben zu Chargen, Daten und Ergebnissen müssen über alle Dokumente hinweg konsistent sein.
- ℹ️ 17 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): Die Impact-Bewertung der Abweichung DEV-MET-09 stuft die Abweichung als 'Minor' ein, jedoch fehlt eine detaillierte, chargenspezifische Begründung für die Dispositionsentscheidung der Charge MET-2026-C09. Die Ausbeute von 92,4% liegt außerhalb des spezifizierten Toleranzbereichs von 95,0% bis 102,0%, was auf ein potenzielles Qualitätsrisiko hindeutet, das nicht ausreichend adressiert wurde.
- ✅ `ERR_07_02` (medium) — gefunden via evidence_fuzzy (Score 0.639): Zum CAPA-Plan ist im vorliegenden Claim-Satz zwar Verantwortlichkeit und Deadline dokumentiert, jedoch keine definierte oder dokumentierte Wirksamkeitspruefung erkennbar. Damit ist die fuer den CAPA-Abschluss erforderliche Effectiveness-Check-Evidenz nicht belegt.
- ℹ️ 28 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-IBU-2026-112 (Haarriss am Oberstempel, Charge IBU-2026-P03) wurde als isoliertes Ereignis ohne systematischen Charakter bewertet. Es fehlen jedoch belastbare physikalisch-chemische Daten zur Risikoeinstufung, insbesondere zur Bewertung möglicher metallischer Mikrofragmente im Endprodukt. Eine Einstufung ohne solche Daten ist gemäß SOP-DEV-001 nicht zulässig.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.697): Die Abweichung DEV-IBU-2026-112 wird als isoliertes Einzelereignis ohne Einfluss auf andere Chargen oder vorangegangene Produktionsschritte bewertet (Claims claim_2084e5a5b522959af96f und claim_0d051396808bd912a548). Allerdings fehlt eine explizite Auflistung aller betroffenen Chargen im Rahmen der Batch-Impact-Bewertung, was der Anforderung widerspricht, dass Batch-Impact-Bewertungen alle betroffenen Chargen auflisten müssen.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme CAPA-112-IBU wurde ohne dokumentierten Effectiveness-Check abgeschlossen. Gemäß SOP-CAPA-003 (Abschnitt 7.5) ist ein Effectiveness-Check zwingend erforderlich, um die Wirksamkeit der Maßnahmen nachzuweisen. Fehlende Wirksamkeitsnachweise gefährden die Compliance und können zu regulatorischen Beanstandungen führen.
- ℹ️ 23 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Der handschriftliche Batch Record für Charge CEF-BIOR-2026-77 enthält die Eintragung 'Keine besonderen Vorkommnisse in der Schicht. Werte stabil.' – obwohl in derselben Schicht (14:00–20:15 Uhr) der automatische pH-Regelkreis manuell deaktiviert, der Sollwert eigenmächtig von pH 7,20 auf pH 7,70 hochgesetzt und damit die spezifizierte Obergrenze von pH 7,40 überschritten wurde. Diese Eintragung widerspricht den SCADA-Daten und dem Abweichungsbericht DEV-CEF-77 fundamental. Es besteht der begründete Verdacht auf eine vorsätzliche oder fahrlässige Verschleierung eines Abweichungsereignisses im Batch Record, was einen schwerwiegenden Datenintegritätsbefund (ALCOA+: accurate, complete) darstellt.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-CEF-77 (pH-Wert-Drift auf 7,85) wurde als 'Root Cause unaufgeklärt' dokumentiert, ohne dass eine belastbare Risikobewertung mit physikalisch-chemischen Daten vorliegt. Dies widerspricht der Anforderung, dass Abweichungen von kritischen Prozessparametern mit einer begründeten Risikoeinstufung bewertet werden müssen.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Freigabe des Change-Control-Dokuments (CC-2026-104) ist unvollständig, da die Unterschrift der Leitung Qualitätskontrolle (Leitung QK) fehlt. Dies stellt ein Datenintegritätsrisiko dar, da die Freigabe nicht gemäß SOP-QA-004 dokumentiert ist und die versionskonsistente Genehmigung nicht nachgewiesen werden kann.
- ℹ️ 26 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge INS-GLA-2025-05 weist eine unbekannte Verunreinigung von 0,32% auf, die eine Laborabweichung ausgelöst hat. Die Impact-Bewertung stuft dies als 'temporären Ausreißer' ein, jedoch fehlt eine klare, dokumentierte Dispositionsentscheidung (Freigabe oder Sperrung) für die betroffene Charge.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Die Verantwortlichkeit für die CAPA-Maßnahme ist nicht dokumentiert. Der Eintrag '**Verantwortlich:** [Kein Eintrag / Offen]' stellt einen Verstoß gegen die Datenintegrität und die Anforderungen an dokumentierte QA-Freigaben dar.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge INS-GLA-2025-05 wurde bereits im Juni 2025 in den Handel überführt und seit 11 Monaten ohne Beschwerden appliziert. Dennoch fehlt eine explizite Bestätigung, dass die unbekannte Verunreinigung von 0,32% keine Auswirkungen auf die Produktqualität oder Patientensicherheit hat. Die vorläufige Erfüllung der Analytikvorgaben ist kein ausreichender Nachweis für die Freigabe.
- ℹ️ 21 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
