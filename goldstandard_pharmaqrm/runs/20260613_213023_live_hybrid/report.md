# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-06-13T21:30:23+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 24 von 25 versteckten Fehlern gefunden (96%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 205 von 221 Findings mit verifiziertem Zitat (93%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 10 | 168,808 | 65,024 | 233,832 |
| extraction:mistral | 10 | 34,854 | 27,656 | 62,510 |
| mistral | 70 | 1,286,885 | 197,021 | 1,483,906 |
| openai | 10 | 175,279 | 33,863 | 209,142 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_01 | completed | 51 | 26 | 2/2 | 0/1 | human_review_required |
| CASE_02 | needs_human_review | 28 | 15 | 2/2 | 0/1 | blocked_due_to_model_failure |
| CASE_03 | completed | 18 | 13 | 2/2 | 0/2 | human_review_required |
| CASE_04 | completed | 28 | 25 | 3/3 | 0/1 | human_review_required |
| CASE_05 | needs_human_review | 17 | 17 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_06 | needs_human_review | 22 | 21 | 1/2 | 0/1 | blocked_due_to_model_failure |
| CASE_07 | completed | 19 | 18 | 2/2 | 0/1 | human_review_required |
| CASE_08 | completed | 30 | 26 | 3/3 | 0/1 | human_review_required |
| CASE_09 | needs_human_review | 32 | 34 | 3/3 | 0/1 | blocked_due_to_model_failure |
| CASE_10 | needs_human_review | 23 | 26 | 3/3 | 0/1 | blocked_due_to_model_failure |

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2026-891 und die zugehörige CAPA CAPA-2026-441 weisen eine QA-Prüfung durch Dr. Anna Klar (Qualitätssicherung) mit digitaler Signatur vom 14.12.2026 auf. Allerdings liegt das Signaturdatum in der Zukunft (14.12.2026), was auf eine unplausible oder fehlende QA-Freigabe hindeutet. Eine Charge (XYL-2026-004A) wurde bereits am 25.03.2026 für die Verpackung freigegeben, obwohl die QA-Freigabe der Abweichung und CAPA nicht abgeschlossen ist.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2026-891 (Temperaturunterschreitung auf 34,2°C über 45 Minuten, Sollbereich 40–45°C) wurde als 'Minor' eingestuft. Die Begründung stützt sich ausschließlich auf visuelle Homogenität. Es liegen keine physikalisch-chemischen oder labortechnischen Daten (z.B. Viskositätsmessung im Rahmen einer formalen Prüfung, Wirkstoffgehalt, Freisetzungskinetik) vor, die eine Minor-Einstufung belegen. Die Viskositätswerte im Batch Record zeigen während der Temperaturabweichung einen signifikanten Anstieg (von 2410 auf 2910 mPa·s), was auf eine physikalische Veränderung der Salbenbasis hindeutet und die Entwarnung 'kein Einfluss auf Produktqualität' ohne Labordaten nicht trägt.
- ℹ️ 24 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Es gibt keine dokumentierten Nachweise für die Autorisierung oder Begründung manueller Overrides oder Admin-Eingriffe in GxP-relevante Systeme. Gemäß EU GMP Annex 11, Abschnitt 12, müssen solche Eingriffe begündet, autorisiert und im Audit Trail nachvollziehbar sein. Fehlende Nachweise stellen ein hohes Risiko für die Datenintegrität dar.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_fuzzy (Score 0.496): Die Bewertung der Ausbeute als 'im tolerierbaren Bereich' und die Entscheidung 'Keine weiteren Maßnahmen erforderlich' wurde vom Operator selbst getroffen, nicht durch QA. Dies stellt eine unzulässige Selbstbewertung dar: Der Operator hat sowohl die Korrektur des Ausbeute-Wertes vorgenommen als auch die Akzeptabilität dieser Korrektur beurteilt. Eine unabhängige QA-Bewertung dieser Entscheidung ist in den vorliegenden Claims nicht dokumentiert. Die QA-Freigabe durch Dr. Bernd Richter (10.04.2026) bestätigt lediglich, dass 'die Ausbeute der spezifizierten Vorgabe entspricht', ohne die Datenkorrektur explizit zu adressieren.
- ℹ️ 13 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Es gibt keine dokumentierte Prüfung der Plausibilität und Konsistenz der elektronischen Signaturen und Zeitstempel im Zusammenhang mit der Abweichung DEV-QS-2026-014. Dies stellt ein Risiko für die Datenintegrität dar, da zukünftige oder widersprüchliche Signaturdaten nicht ausgeschlossen werden können.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme (CAPA-2026-014) zur Anpassung des Reinigungsverfahrens für die Wände des Raums R-202 folgt der SOP-QS-REIN-001, Version 2.0. Es fehlt jedoch eine dokumentierte Wirksamkeitsprüfung (Effectiveness Check) der CAPA-Maßnahme, was gegen die Anforderungen an die Validierungsabdeckung des aktuellen Zustands verstößt.
- ℹ️ 11 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_fuzzy (Score 0.448): Zwischen den Dokumenten besteht ein relevanter Widerspruch im dokumentierten Maximalwert der Produkttemperatur: Im Batch Record ist 48.2°C um 13:30 Uhr erfasst, waehrend die Bewertung von einer maximal dokumentierten Temperatur von nur 44.5°C spricht. Dieser Widerspruch kann die Impact-Bewertung und Disposition beeinflussen und muss aufgeklaert werden.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Die Grundursache der Abweichung DEV-P-2026-092 wird ausschließlich als 'mangelnde Aufmerksamkeit des Bedienpersonals' (Bedienerfehler) klassifiziert. Es fehlt jeder dokumentierte Nachweis, dass technische Ursachen – insbesondere ein Versagen des Alarmsystems der Anlage WS-03, Kalibrierungsprobleme der Temperatursensoren oder ein Steuerungsdefekt – ausgeschlossen wurden. Die Zulufttemperatur stieg auf 61,0°C (um 13:30 Uhr), was auf ein mögliches Regelungsversagen hindeutet, das nicht untersucht wurde.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Sterilitätsbewertung der Abweichung DEV-P-2026-092 fehlt. Obwohl die Charge als qualitätskonform freigegeben wurde, ist nicht dokumentiert, ob die Temperaturüberschreitung die Sterilität des Produkts oder der Primärpackmittel beeinträchtigen könnte.
- ℹ️ 22 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Sterilitätsrisikobewertung für den Zyklus ZYK-STER-992 ist nicht explizit dokumentiert. Es fehlt eine klare Aussage, ob die Sterilitätsanforderungen für die sterilisierten Güter erfüllt sind, insbesondere im Hinblick auf die Beladungsmuster und die Einhaltung der validierten Parameter.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anwesenheit des Mitarbeiters PNN-8812 im Autoklavenbereich vor 08:45 Uhr ist nicht durch den Audit Trail belegt. Dies stellt ein Risiko für die Datenintegrität dar, da die Plausibilität der Aufzeichnungen nicht sichergestellt ist.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Die Anwesenheit des Mitarbeiters PNN-8812 im Autoklavenbereich vor 08:45 Uhr ist nicht durch den Audit Trail belegt. Dies stellt ein Risiko für die Datenintegrität dar, da die Plausibilität der Aufzeichnungen nicht sichergestellt ist.
- ℹ️ 15 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_06

- ✅ `ERR_06_02` (critical) — gefunden via evidence_fuzzy (Score 0.4): Die Sterilitätsassurance für die Formulierungscharge AMO-SUP-2026-01 ist nicht ausreichend dokumentiert. Es fehlt eine explizite Bewertung, ob der erhöhte Wassergehalt des Rohstoffs (13,2%) die Sterilität oder mikrobiologische Qualität des Endprodukts beeinträchtigen könnte.
- ❌ `ERR_06_01` (high) — übersehen: Akzeptanzkriterium der internen Spezifikation wird durch das Lieferanten-Zertifikat verletzt.
- ℹ️ 20 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): Die Charge MET-2026-C09 weist eine Netto-Ausbeute von 92,4% auf, was unterhalb des spezifizierten Toleranzbereichs von 95,0% bis 102,0% liegt. Die Abweichung wurde als 'Pass' markiert, ohne dass eine detaillierte Bewertung der Auswirkungen auf die Produktqualität oder eine Verknüpfung mit der Abweichung DEV-MET-09 (Düsenverstopfung) dokumentiert ist.
- ✅ `ERR_07_02` (medium) — gefunden via evidence_fuzzy (Score 0.579): Für CAPA-MET-2026-09 ist kein Effectiveness-Check-Claim vorhanden. Die CAPA adressiert die Düsenverstopfung an Coater COAT-04 mit Deadline 15.06.2026. Es fehlt jeder Nachweis, dass eine Wirksamkeitsprüfung geplant oder definiert wurde. Gemäß req_capa_effectiveness dürfen CAPA-Maßnahmen mit Qualitätsrisiko nur mit definierter und dokumentierter Wirksamkeitsprüfung abgeschlossen werden.
- ℹ️ 16 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Impact-Assessment-Dokumentation für die Abweichung DEV-IBU-2026-112 (Charge IBU-2026-P03) bewertet die betroffene Charge als isoliertes Einzelereignis ohne systematischen Charakter. Allerdings fehlt eine explizite Bewertung der Vorgängerschargen IBU-2026-P01 und IBU-2026-P02, die am selben Equipment (Rundläuferpresse Korsch TAB-02) innerhalb des Betrachtungszeitraums (März 2026 - Mai 2026) ebenfalls Abweichungen aufwiesen (DEV-IBU-2026-042 und DEV-IBU-2026-081). Dies stellt ein Risiko für die Vollständigkeit der Chargenbewertung dar.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): Das Abweichungsdokument DEV-IBU-2026-112 klassifiziert das Ereignis als 'isoliertes Einzelereignis ohne systematischen Charakter' und schließt einen Einfluss auf andere Chargen 'absolut' aus. Das Equipmentverlaufsprotokoll (doc_8dfe7727f1464f51b4c96c74615547d5) dokumentiert jedoch drei gleichartige Werkzeugschäden an derselben Presse TAB-02 innerhalb von weniger als zwei Monaten (14.03.2026: Oberstempel-Beschädigung DEV-IBU-2026-042; 18.04.2026: Mikrorisse Unterstempel DEV-IBU-2026-081; 10.05.2026: Werkzeugbruch Oberstempel Station 12 DEV-IBU-2026-112). Dieser Trend widerspricht der Einstufung als Einzelereignis und der unbelegten Entwarnung für Vorgängerchargen IBU-2026-P01 und IBU-2026-P02 direkt. Eine nicht durch Daten belegte Entwarnung bei einem sicherheitsrelevanten Metallkontaminationsrisiko erfüllt Major/Critical-Kriterien.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme CAPA-112-IBU zur Nachrüstung eines automatischen Metallsuchgeräts am Auslauf der Tablettenpresse ist dokumentiert, jedoch fehlt ein Nachweis über die Wirksamkeitsprüfung (Effectiveness Check) zum aktuellen Zeitpunkt. Dies stellt ein Risiko für die Compliance mit CAPA-Anforderungen dar.
- ℹ️ 23 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Es liegt kein dokumentierter Audit-Trail-Review für die manuelle Änderung des pH-Sollwerts im Bioreaktor BIO-10 vor. Die temporäre Deaktivierung des automatischen Regelkreises und die manuelle Sollwertänderung sind GxP-relevante elektronische Daten, für die ein Audit Trail und dessen risikobasierte Prüfung gemäß EU GMP Annex 11, Abschnitt 9, erforderlich sind. Ohne diesen Nachweis ist die Datenintegrität nicht sichergestellt.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Es besteht ein Widerspruch zwischen der dokumentierten manuellen Sollwertänderung des pH-Werts im Batch Record und der Angabe im Deviation Record, dass die Ursache der pH-Wert-Drift technisch nicht aufgeklärt werden konnte. Dies deutet auf eine unvollständige oder inkonsistente Dokumentation der Abweichung hin.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Die Verantwortlichkeiten für die Umsetzung der CAPA-Maßnahme CC-2026-104 sind nicht eindeutig dokumentiert. Dies kann zu Verzögerungen oder unvollständiger Umsetzung der Maßnahmen führen.
- ℹ️ 31 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Die unbekannte Verunreinigung von 0,32% in der Charge INS-GLA-2025-05 wurde als temporärer Ausreißer bewertet, ohne dass eine dokumentierte Bewertung der Auswirkungen auf die Sterilitätssicherung vorliegt. Es fehlt eine explizite Prüfung, ob die Verunreinigung die Sterilität oder die Produktqualität beeinträchtigen könnte.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme (CAPA-OOS-INS) zur unbekannten Verunreinigung in der Charge INS-GLA-2025-05 enthält keinen benannten Verantwortlichen und keinen Nachweis für einen Effectiveness Check. Dies stellt ein Compliance-Risiko dar, da die Wirksamkeit der Maßnahme nicht überprüft wird und die Umsetzung nicht nachvollziehbar ist.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Das QS-Dokument (19.05.2026) erklärt, dass keine marktregulierenden Maßnahmen erforderlich seien, und begründet dies mit 11 Monaten beschwerdefreier Anwendung sowie der vorläufigen Erfüllung aller Analytikvorgaben. Diese Entwarnung ist nicht durch abgeschlossene analytische Daten belegt: Die OOS-Untersuchung ist noch offen, die Re-Analyse steht aus, und die Identität der unbekannten Verunreinigung (0,32%) ist nicht dokumentiert. Die Bewertung 'vorläufig erfüllt' ist kein abgeschlossener Konformitätsnachweis. Zudem fehlt eine Betrachtung potenziell betroffener Vor- oder Folgechargen.
- ℹ️ 23 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
