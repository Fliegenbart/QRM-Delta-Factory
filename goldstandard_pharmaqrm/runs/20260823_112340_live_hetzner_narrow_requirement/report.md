# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hetzner` | Engine: `requirement`
- Zeitpunkt: 2026-08-23T11:23:40+00:00
- Anthropic-Modell: `-`
- OpenAI-Modell: `-`
- Hetzner-Modell: `Qwen3.8-27B`

## Gesamtergebnis

- **Sensitivität:** 22 von 25 versteckten Fehlern gefunden (88%)
- **In Prüfmappe sichtbar:** 22 von 25 versteckten Fehlern (88%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 75 von 143 (52%) — 20 als Treffer gewertet, 55 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 68 von 143 (48%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 14.3 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 130 von 143 Findings mit verifiziertem Zitat (91%)

## Qualitätsmetriken

- Must-detect Recall: `0.88`
- Wiederholungen: `55` (Redundanzrate `0.7333`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `10/5/7`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| hetzner | 729 | 1,501,073 | 163,954 | 1,665,027 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 15 | 6 | 7 | 2/2 | 2/2 | 0/1 | - |
| CASE_02 | completed_with_model_failures | 0 | 16 | 10 | 4 | 2/2 | 2/2 | 0/1 | - |
| CASE_03 | completed_with_model_failures | 0 | 15 | 3 | 10 | 2/2 | 2/2 | 0/2 | - |
| CASE_04 | completed_with_model_failures | 0 | 11 | 4 | 5 | 2/3 | 2/3 | 0/1 | - |
| CASE_05 | completed_with_model_failures | 0 | 12 | 5 | 5 | 3/3 | 3/3 | 0/1 | - |
| CASE_06 | completed_with_model_failures | 0 | 15 | 2 | 11 | 2/2 | 2/2 | 0/1 | - |
| CASE_07 | completed_with_model_failures | 0 | 15 | 4 | 10 | 1/2 | 1/2 | 0/1 | - |
| CASE_08 | completed_with_model_failures | 0 | 16 | 7 | 6 | 3/3 | 3/3 | 0/1 | - |
| CASE_09 | completed_with_model_failures | 0 | 17 | 10 | 5 | 3/3 | 3/3 | 0/1 | - |
| CASE_10 | completed_with_model_failures | 0 | 11 | 4 | 5 | 2/3 | 2/3 | 0/1 | - |

## Modellausfälle

- **ProviderCallError** (42×): hetzner provider call failed with HTTP 503
  - betroffen: CASE_02/judge:28, CASE_02/judge:39, CASE_02/locate:41, CASE_02/entailment:55, CASE_02/entailment:66, CASE_02/entailment:68
  - … und 36 weitere
- **ProviderCallError** (26×): hetzner provider call failed with HTTP 504
  - betroffen: CASE_02/locate:0, CASE_02/locate:4, CASE_02/locate:42, CASE_02/locate:46, CASE_03/locate:41, CASE_04/locate:13
  - … und 20 weitere
- **ProviderCircuitOpenError** (3×): Circuit breaker is open for hetzner
  - betroffen: CASE_05/entailment:57, CASE_05/entailment:58, CASE_05/entailment:59
- **ProviderCallError** (1×): hetzner provider call timed out
  - betroffen: CASE_03/locate:25
- **ProviderCallError** (1×): hetzner provider output was truncated
  - betroffen: CASE_07/locate:1
- **ProviderCallError** (1×): hetzner provider call failed with HTTP 500
  - betroffen: CASE_07/locate:36
- **ProviderCallError** (1×): hetzner provider returned invalid JSON
  - betroffen: CASE_07/extract[doc_64014c11582b46279f9c9d5c73253d21:werte]:72

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen sind nicht vollständig und konsistent im Sinne von ALCOA+. Im Abweichungsbericht (Zitat 0) ist die Prüfung durch Dr. Anna Klar mit dem Datum 14.12.2026 signiert, was zeitlich nach der Chargenfreigabe am 25.03.2026 (Zitat 3) liegt. Dies stellt einen logischen Widerspruch dar und deutet auf eine nachträgliche oder fehlerhafte Datenerfassung hin. Zudem wird in der Freigabe (Zitat 3) die Abwesenheit negativer Einflüsse ausschließlich auf Basis der 'visuellen Homogenität' begründet, während das Chargenprotokoll (Zitat 2) eine deutliche Viskositätsänderung (von 2400 auf 2910 mPa·s) während der Abweichung dokumentiert. Die fehlende korrelierende Bewertung dieser physikalischen Parameter in der Freigabe und die zeitliche Inkonsistenz der Signatur belegen einen Verstoß gegen die Anforderungen an die Vollständigkeit und Korrektheit der Originalaufzeichnungen.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Auswirkungsbewertung (Change-Impact-Assessment) und eine Prüfung der betroffenen Validierungen. Die vorliegenden Zitate (0 und 1) belegen lediglich eine qualitative Einschätzung, dass ein negativer Einfluss auf Stabilität oder Freisetzungskinetik durch visuelle Homogenität ausgeschlossen wurde. Es fehlt jedoch der explizite Nachweis einer formalen Auswirkungsbewertung sowie die Dokumentation, dass die relevanten Validierungen geprüft oder aktualisiert wurden. Die Behauptung 'kein Einfluss' ohne Bezug auf Validierungsdaten oder ein formales Impact-Assessment-Dokument erfüllt die hohen Anforderungen an die Dokumentation nicht.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Die Auszüge belegen einen dokumentierten Verstoß gegen die Chargenfreigabe (Ausbeute 96,47 % unter Soll-Minimum 98,0 %), der durch eine nachträgliche, nicht primär belegte Korrektur auf 98,1 % im Chargenprotokoll behoben wurde. Die Anforderung verlangt, dass CAPA-Maßnahmen, die mit einem Qualitätsrisiko verknüpft sind, nur mit definierter und dokumentierter Wirksamkeitsprüfung (Effectiveness Check) abgeschlossen werden dürfen. In den vorliegenden Dokumenten (Chargenprotokoll und Freigabe-Zertifikat) fehlt jeglicher Nachweis einer durchgeführten Wirksamkeitsprüfung oder eines CAPA-Protokolls. Die bloße Behauptung im Freigabe-Zertifikat, die Ausbeute entspreche der Vorgabe, ist keine Primärevidenz für eine Wirksamkeitsprüfung. Da der auslösende Vorgang (Qualitätsrisiko durch Abweichung) belegt ist, der geforderte Nachweis (Wirksamkeitsprüfung) aber fehlt, liegt ein Verstoß vor.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_fuzzy (Score 0.496): Die Chargenprotokolle weisen eine berechnete Ausbeute von 96,47 % auf, die unterhalb der spezifizierten Soll-Ausbeute von 98,0 % - 101,0 % liegt. Der Operator hat den Wert nachträglich auf 98,1 % korrigiert, was jedoch durch die Freigabenotiz der Qualitätssicherung nicht gedeckt ist, da dort pauschal behauptet wird, die Ausbeute entspreche der Vorgabe. Es fehlt eine dokumentierte Aufklärung des Widerspruchs zwischen der Primärdokumentation (Batch Record) und der Freigabe, was einen Verstoß gegen die Anforderung der Konsistenz darstellt.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen einen zeitlichen Widerspruch zwischen dem elektronischen Logbuch (Eintritt 14:35 Uhr) und dem Zeitstempel der Partikelmessung (14:15 Uhr). Dies deutet auf eine mögliche Manipulation oder Fehlfunktion des Audit Trails hin. Es fehlt jedoch jeglicher Nachweis, dass ein Audit-Trail-Review durchgeführt wurde, um diesen Widerspruch aufzuklären oder die Integrität der Daten zu bestätigen. Da der geforderte Nachweis (dokumentierter Audit-Trail-Review) in den Auszügen fehlt und ein möglicher schwerer Verstoß (Datenintegrität) nicht widerlegt ist, wird dies als Verstoß gewertet.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Die Auszüge listen zwar die referenzierten Dokumente (Zitate 0-2) und eine SOP (Zitat 3) auf, belegen aber nicht deren tatsächliche Vorhandensein oder Aktualität. Es fehlen Primärevidenzen wie Checklisten, Rohdaten oder signierte Bestätigungen, die die Anwesenheit der Anhänge im Vorgang nachweisen. Da die Pflicht zur Vorhandenseinsprüfung nicht durch die vorliegenden Zitate erfüllt wird, ist der Status 'unclear'.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen sind nicht konsistent. Das manuelle Protokoll (Zitat 0) dokumentiert eine Produkttemperatur von 48,2 °C, während der Abweichungsbericht (Zitat 1) und die QS-Bewertung (Zitat 2) die maximale Temperatur mit 44,5 °C angeben. Diese Diskrepanz widerspricht dem ALCOA+-Prinzip der Konsistenz und Vollständigkeit. Zudem fehlt eine Begründung für die Abweichung der manuellen Einträge von den SCADA-Daten, was einen Verstoß darstellt.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Auswirkungsbewertung (Change-Impact-Assessment) und eine Prüfung der Validierungen. Die vorliegenden Zitate belegen lediglich die Feststellung einer Abweichung (Zitat 0), die qualitative Bewertung der Charge (Zitat 1) und die Festlegung einer CAPA-Maßnahme (Zitat 2). Es fehlt in den Auszügen jeglicher Nachweis über eine systematische Auswirkungsbewertung der Änderung bzw. des Vorfalls auf andere Prozesse oder Produkte sowie über die Prüfung oder Aktualisierung von Validierungen. Da der auslösende Vorgang (Abweichung) belegt ist, der geforderte Nachweis aber fehlt, liegt ein Verstoß vor.
- ❌ `ERR_04_03` (critical) — übersehen: Kritische Chargenfreigabe beruhend auf fehlerhafter und unvollständiger Abweichungsbewertung.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Validierungsnote referenziert explizit auf 'Anhang 4' für die Beladungsmuster und Gewichte. In den bereitgestellten Auszügen (Chunks) ist jedoch weder der Inhalt dieses Anhangs noch ein Nachweis seiner tatsächlichen Existenz und Aktualität enthalten. Da die Pflichtanhang nicht in den vorliegenden Primärevidenzen verifiziert werden kann, liegt ein Verstoß gegen die Anforderung der Vollständigkeit der Pflichtanhang vor.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen den auslösenden Vorgang (Autoklavierung) und eine zeitliche Diskrepanz (Mitarbeiter PNN-8812 betrat den Raum erst um 08:45 Uhr, obwohl der Zyklus um 08:20 Uhr startete und um 08:55 Uhr endete). Es fehlt jedoch vollständig die geforderte dokumentierte Bewertung der Auswirkung auf die Produktqualität und Patientensicherheit sowie eine Liste der potenziell betroffenen Chargen. Da der Nachweis der Auswirkungsbewertung in den Auszügen fehlt, liegt ein Verstoß vor.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen den auslösenden Vorgang (Autoklavierung) und eine zeitliche Diskrepanz (Mitarbeiter PNN-8812 betrat den Raum erst um 08:45 Uhr, obwohl der Zyklus um 08:20 Uhr startete und um 08:55 Uhr endete). Es fehlt jedoch vollständig die geforderte dokumentierte Bewertung der Auswirkung auf die Produktqualität und Patientensicherheit sowie eine Liste der potenziell betroffenen Chargen. Da der Nachweis der Auswirkungsbewertung in den Auszügen fehlt, liegt ein Verstoß vor.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Die Zitate belegen, dass ein Out-of-Specification-Ergebnis (Wassergehalt 13,2% bei Obergrenze 12,8%) vorliegt und die Abweichung noch offen ist (Status: In Untersuchung). Gleichzeitig wird in einem separaten Dokument die finale Freigabe und der Einsatz des Rohstoffs autorisiert. Die geforderte vollständige Untersuchung und Bewertung vor der Disposition ist somit nicht nachgewiesen, was einen Verstoß darstellt.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine nachvollziehbare Risikobewertung zur Begründung der Schweregradeinstufung der Abweichung. Die vorliegenden Zitate belegen zwar das Vorliegen einer Abweichung (Wassergehalt 13,2 % gegenüber dem Grenzwert 12,8 %) und die Freigabe des Rohstoffs, jedoch fehlt in den Auszügen jegliche Dokumentation einer Risikobewertung oder einer Begründung für die Einstufung (z. B. als Major oder Kritisch). Da der geforderte Nachweis (Risikobewertung) in den bereitgestellten Dokumenten fehlt, obwohl der auslösende Vorgang (Abweichung) dokumentiert ist, liegt ein Verstoß vor.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 11 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.491): Die vorliegenden Auszüge belegen eine Änderung der Wartungsintervalle (Quote 1) und eine Abweichung im Coating-Prozess (Quote 0), die zu einer Ausbeute unterhalb des spezifizierten Toleranzbereichs führte (Quotes 2 und 3). Es fehlt jedoch jegliche Dokumentation einer Auswirkungsbewertung (Change-Impact-Assessment) oder einer Validierungsbewertung, die prüft, ob die geänderten Intervalle oder die Abweichung die Validierung des Coating-Prozesses beeinflussen. Da der geforderte Nachweis in den Auszügen fehlt, liegt ein Verstoß vor.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Auszüge belegen die Durchführung einer Änderung (Nachrüstung eines Metallsuchgeräts) und die Einleitung einer Validierung. Es fehlt jedoch der explizite Nachweis einer dokumentierten Auswirkungsbewertung (Change-Impact-Assessment) auf das Produkt oder die Prozessparameter. Die Aussage, dass ein Einfluss auf andere Chargen 'absolut ausgeschlossen' ist, ist eine Behauptung ohne die geforderte dokumentierte Begründung oder Analyse. Da die Primärevidenz für die Auswirkungsbewertung fehlt, ist die Anforderung nicht erfüllt.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): Die Anforderung verlangt die vollständige Erfassung aller potenziell betroffenen Chargen, einschließlich Vorgänger- und Folgechargen. Das Abweichungsbericht (Zitat 0) behauptet, dass ein Einfluss auf andere Chargen 'absolut ausgeschlossen' ist, und klassifiziert das Ereignis als isoliert. Das Logbuch (Zitate 1 und 2) belegt jedoch, dass es in den Monaten März und April 2026 bereits zwei weitere Vorfälle mit Werkzeugschäden an derselben Presse (TAB-02) bei den Vorgängerchargen IBU-2026-P01 und IBU-2026-P02 gab. Diese wiederkehrenden Vorfälle an derselben Anlage deuten auf ein systematisches Problem hin, was die Behauptung der Isolation und den Ausschluss von Auswirkungen auf andere Chargen in Frage stellt. Es fehlt eine belastbare Begründung oder eine Chargenliste, die nachweist, dass die Vorgängerchargen tatsächlich nicht betroffen sind oder dass die wiederkehrenden Vorfälle keine systematische Ursache haben. Daher ist die Anforderung nicht erfüllt.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen die Definition der CAPA-Maßnahme (Nachrüstung eines Metallsuchgeräts) und die Festlegung einer Deadline für den Abschluss der Validierung. Es fehlt jedoch jeglicher Nachweis über die Durchführung einer spezifischen Wirksamkeitsprüfung (Effectiveness Check) oder deren dokumentierte Ergebnisse. Da die Anforderung zwingend eine definierte und dokumentierte Wirksamkeitsprüfung für den Abschluss verlangt und diese in den Zitatfragmenten nicht enthalten ist, liegt ein Verstoß vor.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Zitate belegen einen manuellen Override-Eingriff (Zitat 0), bei dem der automatische Regelkreis deaktiviert und der pH-Sollwert auf 7,70 erhöht wurde. Die Anforderung verlangt, dass solche Eingriffe begründet, autorisiert und im Audit Trail nachvollziehbar sein müssen. Zwar wird in Zitat 0 ein technischer Grund (Schaumbildung) genannt, jedoch fehlt in den vorliegenden Auszügen jeglicher Nachweis einer formellen Autorisierung (z. B. durch eine qualifizierte Person oder ein Freigabeverfahren) sowie einer rollenbasierten Berechtigung für diesen spezifischen Override. Zudem widerspricht die handschriftliche Anmerkung in Zitat 1 ('Keine besonderen Vorkommnisse') dem dokumentierten Override, was auf eine unzureichende Dokumentation oder ein Kontrollversagen hindeutet. Da der geforderte Nachweis der Autorisierung und des Berechtigungskonzepts fehlt, liegt ein Verstoß vor.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen, dass eine Abweichung (DEV-CEF-77) auftrat und die Aufarbeitung fortgesetzt wurde, ohne dass eine abschließende Freigabeentscheidung oder ein abgeschlossener Impact Assessment dokumentiert ist. Zudem fehlt die Unterschrift der Leitung QK im Change Control, was auf eine unvollständige Bewertung hindeutet. Da die Pflicht zur Freigabe erst nach abgeschlossener Bewertung besteht und diese in den Dokumenten nicht nachgewiesen ist, liegt ein Verstoß vor.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen, dass eine Abweichung (DEV-CEF-77) auftrat und die Aufarbeitung fortgesetzt wurde, ohne dass eine abschließende Freigabeentscheidung oder ein abgeschlossener Impact Assessment dokumentiert ist. Zudem fehlt die Unterschrift der Leitung QK im Change Control, was auf eine unvollständige Bewertung hindeutet. Da die Pflicht zur Freigabe erst nach abgeschlossener Bewertung besteht und diese in den Dokumenten nicht nachgewiesen ist, liegt ein Verstoß vor.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Keine einschlägige Stelle in den Auszügen gefunden: Der CAPA-Plan enthält zwar ein Zieldatum, weist jedoch unter dem Feld für den Verantwortlichen explizit auf einen fehlenden Eintrag hin, was die Anforderung an einen benannten Maßnahmenverantwortlichen verletzt.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine begründete Dispositionsentscheidung, die explizit mit den Batch Records verknüpft ist. Die vorliegenden Auszüge belegen zwar die Feststellung einer OOS-Abweichung (Quote 1) und die Einleitung einer Re-Analyse (Quote 0), sowie die vorläufige Einstufung als marktfähig (Quote 2 und 3). Es fehlt jedoch in den Dokumenten jeglicher Verweis auf die Batch Records der betroffenen Charge INS-GLA-2025-05. Da die geforderte Verknüpfung mit den Primärdaten (Batch Records) nicht nachgewiesen ist, liegt ein Verstoß gegen die Nachvollziehbarkeitsanforderung vor.
- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
