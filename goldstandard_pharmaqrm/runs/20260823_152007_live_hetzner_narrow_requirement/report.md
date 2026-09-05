# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hetzner` | Engine: `requirement`
- Zeitpunkt: 2026-08-23T15:20:07+00:00
- Anthropic-Modell: `-`
- OpenAI-Modell: `-`
- Hetzner-Modell: `Qwen3.8-27B`

## Gesamtergebnis

- **Sensitivität:** 23 von 25 versteckten Fehlern gefunden (92%)
- **In Prüfmappe sichtbar:** 23 von 25 versteckten Fehlern (92%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 90 von 160 (56%) — 21 als Treffer gewertet, 69 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 70 von 160 (44%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 16.0 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 148 von 160 Findings mit verifiziertem Zitat (92%)

## Qualitätsmetriken

- Must-detect Recall: `0.92`
- Wiederholungen: `69` (Redundanzrate `0.7667`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `11/6/6`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| hetzner | 794 | 1,610,398 | 208,208 | 1,818,606 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed_with_model_failures | 0 | 14 | 3 | 9 | 2/2 | 2/2 | 0/1 | - |
| CASE_02 | completed_with_model_failures | 0 | 18 | 10 | 6 | 2/2 | 2/2 | 0/1 | - |
| CASE_03 | completed_with_model_failures | 0 | 20 | 8 | 10 | 2/2 | 2/2 | 0/2 | - |
| CASE_04 | completed_with_model_failures | 0 | 17 | 11 | 3 | 3/3 | 3/3 | 0/1 | - |
| CASE_05 | completed_with_model_failures | 0 | 16 | 9 | 5 | 3/3 | 3/3 | 0/1 | - |
| CASE_06 | completed_with_model_failures | 0 | 15 | 1 | 12 | 2/2 | 2/2 | 0/1 | - |
| CASE_07 | completed_with_model_failures | 0 | 18 | 4 | 13 | 1/2 | 1/2 | 0/1 | - |
| CASE_08 | completed_with_model_failures | 0 | 17 | 8 | 7 | 3/3 | 3/3 | 0/1 | - |
| CASE_09 | completed_with_model_failures | 0 | 20 | 14 | 3 | 3/3 | 3/3 | 0/1 | - |
| CASE_10 | completed_with_model_failures | 0 | 5 | 1 | 2 | 2/3 | 2/3 | 0/1 | - |

## Modellausfälle

- **ProviderCallError** (31×): hetzner provider call failed with HTTP 504
  - betroffen: CASE_01/locate:3, CASE_01/locate:4, CASE_01/locate:17, CASE_01/locate:50, CASE_02/locate:0, CASE_02/locate:1
  - … und 25 weitere
- **ProviderCircuitOpenError** (27×): Circuit breaker is open for hetzner
  - betroffen: CASE_10/locate:19, CASE_10/locate:20, CASE_10/locate:21, CASE_10/locate:22, CASE_10/locate:23, CASE_10/locate:24
  - … und 21 weitere
- **ProviderCallError** (1×): hetzner provider returned invalid JSON
  - betroffen: CASE_07/extract[doc_b83d9d6b34af439e91b48bd433f23bf9:werte]:82

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt den Nachweis eines Audit-Trail-Reviews für GxP-relevante elektronische Daten. Die vorliegenden Zitate belegen lediglich die zeitliche Erfassung und Prüfung des Abweichungsberichts durch digitale Signaturen. Es fehlt jeglicher Nachweis, dass der Audit Trail des Systems, in dem diese Daten erfasst wurden, regelmäßig und risikobasiert geprüft wurde. Da der auslösende Vorgang (digitale Signatur) belegt ist, der geforderte Nachweis (Audit-Trail-Review) aber in den Auszügen fehlt, liegt ein Verstoß vor.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Bewertung der Auswirkung auf die Produktqualität und Patientensicherheit, einschließlich aller potenziell betroffenen Chargen. Die vorliegenden Zitate (0 und 1) belegen zwar eine qualitative Einschätzung der Produktqualität (visuelle Homogenität, keine Phasentrennung) und schließen einen negativen Einfluss auf Stabilität und Freisetzungskinetik aus. Es fehlt jedoch jegliche Dokumentation bezüglich der Patientensicherheit. Zudem wird in den Auszügen keine explizite Auflistung oder Bewertung aller potenziell betroffenen Chargen vorgenommen (Zitat 2 nennt nur die spezifische Charge XYL-2026-004A, ohne den Kontext einer umfassenden Chargenliste oder -bewertung zu liefern). Da der geforderte Nachweis für die Patientensicherheit und die vollständige Chargenbewertung in den Auszügen fehlt, ist die Anforderung nicht erfüllt.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Die Zitate belegen, dass die Charge freigegeben wurde (Zitat 2) und dass die Ausbeute der Vorgabe entspricht (Zitat 1). Zitat 0 belegt jedoch eine nachträgliche Korrektur der Ausbeute von 96,47 % auf 98,1 %, da der Wiegebegleitschein unvollständig war. Dies deutet auf eine Abweichung oder einen Dokumentationsfehler hin. In den vorliegenden Auszügen fehlt jedoch jeglicher Nachweis über eine abgeschlossene Abweichungsbewertung, ein Impact Assessment oder eine spezifische QA-Freigabe für diese Korrektur. Da die Freigabe (Zitat 2) erfolgt ist, ohne dass der Abschluss der Bewertung der Abweichung (Korrektur der Ausbeute) belegt ist, liegt ein Verstoß gegen die Anforderung vor, keine Freigabe vor abgeschlossener Bewertung zu erteilen.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_fuzzy (Score 0.496): Die Dokumente weisen einen erheblichen Widerspruch auf: Das Chargenprotokoll (Zitat 0) dokumentiert eine nachträgliche Korrektur der Ausbeute von 96,47 % auf 98,1 % mit der Begründung, der Wiegebegleitschein sei unvollständig gewesen. Die berechnete Ausbeute von 96,47 % (Zitat 3) liegt jedoch unterhalb des Soll-Bereichs von 98,0 % - 101,0 % (Zitat 2). Die Freigabenotiz (Zitat 1) behauptet pauschal, die Ausbeute entspreche der Vorgabe, ohne die Korrektur oder die ursprüngliche Abweichung zu erwähnen oder zu rechtfertigen. Da die Korrektur im Chargenprotokoll als Eintrag des Operators ohne sichtbare unabhängige Validierung oder Aufklärung der Ursache (außer der vagen Angabe 'unvollständiger Wiegebegleitschein') erfolgt und die Freigabe diese Diskrepanz ignoriert, ist die Konsistenz nicht gegeben und der Verstoß nicht aufgeklärt.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt den Nachweis einer Grundursache durch eine angemessene Untersuchung, einschließlich des dokumentierten Ausschlusses technischer Ursachen. Die vorliegenden Zitate beschreiben lediglich den Vorfall (Partikelpeak) und die geplanten Korrekturmaßnahmen (Anpassung des Reinigungsverfahrens). Es fehlt jegliche Primärevidenz für eine durchgeführte Root-Cause-Analyse, einen Untersuchungsbericht oder den expliziten Ausschluss technischer Fehler (z. B. Equipment, Kalibrierung). Zudem enthält das Abweichungsprotokoll einen zeitlichen Widerspruch (Peak 14:15 Uhr, Mitarbeiter-Eintritt 14:35 Uhr), der ohne weitere Untersuchung nicht aufgelöst ist. Da der geforderte Nachweis in den Auszügen fehlt, liegt ein Verstoß vor.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen die Durchführung einer Änderung (Anpassung des Reinigungsverfahrens) und die Referenzierung einer SOP. Es fehlen jedoch die explizit geforderten Nachweise einer dokumentierten Auswirkungsbewertung (Change-Impact-Assessment) sowie einer Validierungsbewertung. Da die Auszüge den auslösenden Vorgang (die Änderung) belegen, der geforderte Nachweis aber nicht enthalten ist, liegt ein Verstoß vor.
- 🔁 8 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Die Dispositionsentscheidung (Zitat 0) stützt sich auf eine maximale Temperatur von 44,5 °C, die laut Abweichungsbericht (Zitat 2) aus dem SCADA-Protokoll stammt. Das Batch Record (Zitat 1) dokumentiert jedoch eine manuell eingetragene Produkttemperatur von 48,2 °C, die das Limit von 42,0 °C deutlich überschreitet. Da die Begründung der Freigabe auf widersprüchlichen Daten beruht und die höhere Temperatur im Batch Record nicht in der Disposition berücksichtigt oder erklärt wird, ist die geforderte nachvollziehbare Verknüpfung und Begründung nicht gegeben.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen die Festlegung einer CAPA-Maßnahme (Re-Training) und die Freigabe der Charge, enthalten jedoch keinerlei Dokumentation einer Wirksamkeitsprüfung (Effectiveness Check). Da die Anforderung zwingend eine definierte und dokumentierte Wirksamkeitsprüfung für den Abschluss der Maßnahme verlangt und dieser Nachweis in den Auszügen fehlt, liegt ein Verstoß vor. Im CAPA-Plan fehlt der regulatorisch geforderte Effectiveness Check (Wirksamkeitsprüfung) für 1 Maßnahme(n), z. B. 'bebildertes Re-Training bezüglich der Alarmgrenzen an der Anlage WS-03'.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Dokumente (Abweichungsbericht, QS-Bewertung, Fallzusammenfassung) beziehen sich ausschließlich auf die Charge PAR-2026-H102. Es fehlt jegliche Dokumentation, die eine Prüfung auf potenziell betroffene Vorgänger- oder Folgechargen (z. B. durch gemeinsame Rohstoffchargen oder gleichzeitige Nutzung der Anlage) belegt. Da die Anforderung die vollständige Erfassung aller potenziell betroffenen Chargen verlangt und dieser Nachweis in den Auszügen fehlt, liegt ein Verstoß vor.
- 🔁 11 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 3 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Validierungsnote referenziert explizit auf 'Anhang 4' für die Beladungsmuster und Gewichte. In den bereitgestellten Auszügen (Chunks) ist jedoch der Inhalt dieses Anhangs nicht enthalten. Da die Anforderung verlangt, dass referenzierte Pflichtanhang tatsächlich vorhanden sind, und die Evidenz für die Existenz oder den Inhalt von Anhang 4 in den Auszügen fehlt, kann die Erfüllung nicht belegt werden. Es liegt ein Verstoß vor, da der geforderte Nachweis in den Auszügen fehlt.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen einen dokumentationsrelevanten Vorfall (Diskrepanz zwischen Personalnummer und Initialen sowie zeitliche Unstimmigkeiten bei der Autoklavierung), der eine CAPA auslösen würde. In den bereitgestellten Dokumenten (Fallzusammenfassung, Batch-Record-Auszug, Reinraum-Bericht) fehlen jedoch jegliche Angaben zu einer eingeleiteten CAPA-Maßnahme, einem benannten Maßnahmenverantwortlichen oder einem Umsetzungstermin. Da der geforderte Nachweis (Verantwortlicher und Termin) in den Auszügen nicht enthalten ist, liegt ein Verstoß gegen die Anforderung vor.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen einen dokumentationsrelevanten Vorfall (Diskrepanz zwischen Personalnummer und Initialen sowie zeitliche Unstimmigkeiten bei der Autoklavierung), der eine CAPA auslösen würde. In den bereitgestellten Dokumenten (Fallzusammenfassung, Batch-Record-Auszug, Reinraum-Bericht) fehlen jedoch jegliche Angaben zu einer eingeleiteten CAPA-Maßnahme, einem benannten Maßnahmenverantwortlichen oder einem Umsetzungstermin. Da der geforderte Nachweis (Verantwortlicher und Termin) in den Auszügen nicht enthalten ist, liegt ein Verstoß gegen die Anforderung vor.
- 🔁 9 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Die Dokumente enthalten einen direkten Widerspruch bezüglich des Wassergehalts. Das Lieferanten-Zertifikat (Zitat 0) weist 13,2 % aus, während der interne Prüfplan (Zitat 1) ein striktes Akzeptanzkriterium von 11,5 % bis 12,8 % definiert. Die interne Re-Analyse bestätigt den Wert von 13,2 %, was außerhalb der Spezifikation liegt. Trotz dieser Abweichung und des offenen Abweichungsberichts (LAB-DEV-2026-031) wird in der Freigabenotiz (Zitat 2) die Charge final autorisiert und als 'frei verwendbar' eingestuft. Die Anforderung verlangt, dass Widersprüche aufgeklärt werden müssen, bevor eine Freigabe erfolgt. Da die Freigabe trotz des nachgewiesenen Widerspruchs und ohne Beleg für eine Aufklärung oder Abweichungsgenehmigung erteilt wurde, ist die Anforderung verletzt.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen den Auslöser der Abweichung (Wassergehalt 13,2 % bei einem Grenzwert von 11,5–12,8 %) und die Freigabe der Charge. Es fehlt jedoch der geforderte Nachweis einer dokumentierten Bewertung der Auswirkung auf die Produktqualität und Patientensicherheit sowie einer Auflistung aller potenziell betroffenen Chargen. Da die Abweichung vorliegt und der erforderliche Nachweis in den Auszügen fehlt, ist die Anforderung verletzt.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.491): Die Ausbeute von 92,4 % liegt unterhalb des spezifizierten Toleranzbereichs von 95,0 % bis 102,0 %. Trotz dieses kritischen Befunds und der dokumentierten Abweichung (verstopfte Düse) wird im Batch Record der Status 'Pass' manuell angekreuzt. Es fehlt eine begründete Dispositionsentscheidung, die diesen Widerspruch erklärt oder die Freigabe trotz Abweichung rechtfertigt. Die geforderte Verknüpfung der Disposition mit den Batch Records und deren Begründung ist nicht nachvollziehbar.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 13 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die vollständige Erfassung aller potenziell betroffenen Chargen, einschließlich Vorgänger- und Folgechargen, sowie die Begründung der Chargenauswahl. Das Abweichungsbericht (Zitat 0 und 3) behauptet, dass es sich um ein isoliertes Einzelereignis handelt und ein Einfluss auf andere Chargen 'absolut ausgeschlossen' sei. Das Logbuch (Zitat 1 und 2) belegt jedoch, dass an derselben Anlage (TAB-02) in den Monaten März und April 2026 bereits zwei weitere Vorfälle mit Werkzeugschäden (Oberstempel-Beschädigung, Mikrorisse) auftraten. Diese wiederkehrenden Vorfälle an derselben Anlage deuten auf ein systematisches Problem oder ein erhöhtes Risiko hin, was die Behauptung der Isolation und den Ausschluss von Auswirkungen auf andere Chargen in Frage stellt. Es fehlt eine belastbare Begründung, warum trotz der wiederkehrenden Vorfälle keine weiteren Chargen betroffen sind, und es fehlt eine explizite Chargenliste, die die Nicht-Betroffenheit der anderen Chargen belegt. Die bloße Behauptung 'absolut ausgeschlossen' ohne Primärevidenz oder systematische Analyse der wiederkehrenden Vorfälle erfüllt die Anforderung nicht.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): Die Anforderung verlangt die vollständige Erfassung aller potenziell betroffenen Chargen, einschließlich Vorgänger- und Folgechargen, sowie die Begründung der Chargenauswahl. Das Abweichungsbericht (Zitat 0 und 3) behauptet, dass es sich um ein isoliertes Einzelereignis handelt und ein Einfluss auf andere Chargen 'absolut ausgeschlossen' sei. Das Logbuch (Zitat 1 und 2) belegt jedoch, dass an derselben Anlage (TAB-02) in den Monaten März und April 2026 bereits zwei weitere Vorfälle mit Werkzeugschäden (Oberstempel-Beschädigung, Mikrorisse) auftraten. Diese wiederkehrenden Vorfälle an derselben Anlage deuten auf ein systematisches Problem oder ein erhöhtes Risiko hin, was die Behauptung der Isolation und den Ausschluss von Auswirkungen auf andere Chargen in Frage stellt. Es fehlt eine belastbare Begründung, warum trotz der wiederkehrenden Vorfälle keine weiteren Chargen betroffen sind, und es fehlt eine explizite Chargenliste, die die Nicht-Betroffenheit der anderen Chargen belegt. Die bloße Behauptung 'absolut ausgeschlossen' ohne Primärevidenz oder systematische Analyse der wiederkehrenden Vorfälle erfüllt die Anforderung nicht.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen die Definition der CAPA-Maßnahme (Installation eines Metallsuchgeräts) und die Festlegung einer Deadline für den Abschluss der Validierung. Es fehlt jedoch jeglicher Nachweis über die Durchführung einer spezifischen Wirksamkeitsprüfung (Effectiveness Check), die den Erfolg der Maßnahme im laufenden Betrieb oder nach der Validierung belegt. Da die geforderte Primärevidenz für die Wirksamkeitsprüfung in den Dokumenten nicht enthalten ist, kann die Erfüllung nicht bestätigt werden. Im CAPA-Plan fehlt der regulatorisch geforderte Effectiveness Check (Wirksamkeitsprüfung) für 2 Maßnahme(n), z. B. 'Automatisches Metallsuchgerät (Inline-Metalldetektor) am Auslauf der Tablettenpresse nachrüsten'.
- 🔁 8 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine begründete Dispositionsentscheidung, die mit den Batch Records verknüpft ist. Das Zitat 0 belegt zwar, dass die Aufarbeitung fortgesetzt wurde, liefert jedoch keine formale Begründung oder Verknüpfung zu den Batch Records. Das Zitat 1 ist eine handschriftliche Anmerkung, die behauptet, es gäbe keine besonderen Vorkommnisse, was im Widerspruch zu den SCADA-Daten steht und keine Primärevidenz für eine korrekte Disposition darstellt. Da die geforderte begründete Verknüpfung fehlt, ist die Anforderung verletzt.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verbietet die Freigabe einer Charge, solange die Abweichungsbewertung oder die QA-Freigabe nicht abgeschlossen sind. Das Zitat 0 belegt, dass die Root Cause der pH-Drift (DEV-CEF-77) nicht final aufgeklärt wurde. Das Zitat 2 bestätigt, dass die Aufarbeitung fortgesetzt wurde, was impliziert, dass der Prozess noch läuft und keine abschließende Freigabeentscheidung vorliegt. Da die Bewertung der Abweichung nicht abgeschlossen ist (Root Cause offen) und keine Evidenz für eine abgeschlossene QA-Freigabe der Charge vorliegt, ist die Anforderung verletzt.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen den auslösenden Vorgang (pH-Drift mit unaufgeklärter Ursache), für den eine CAPA-Maßnahme erforderlich wäre. Es fehlen jedoch in den Dokumenten sowohl ein benannter Maßnahmenverantwortlicher als auch ein konkreter, realisierbarer Umsetzungstermin für die CAPA. Der im Change Control genannte Termin (September 2026) bezieht sich auf eine geplante Wartung und nicht auf die CAPA-Maßnahme zur Aufklärung der Drift. Zudem ist das Unterschriftenfeld für die Leitung QK im Change Control leer, was auf unvollständige Dokumentation hindeutet. Da der geforderte Nachweis in den Auszügen fehlt, liegt ein Verstoß vor.
- 🔁 14 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 3 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt einen benannten Maßnahmenverantwortlichen. Das Zitat 0 zeigt jedoch explizit den Eintrag '[Kein Eintrag / Offen]', was bedeutet, dass kein Verantwortlicher benannt ist. Dies stellt einen Verstoß gegen die Anforderung dar, da ein leeres oder offenes Pflichtfeld als Befund gewertet wird.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verbietet die Freigabe einer Charge, solange die Abweichungsbewertung oder die QA-Freigabe nicht abgeschlossen sind. Die vorliegenden Dokumente belegen, dass eine OOS-Abweichung (Verunreinigung 0,32% > 0,20%) vorliegt und ein Re-Testing eingeleitet wurde (Quote 2). Der Marktstatus-Vermerk (Quote 0 und 3) behauptet jedoch, dass die Analytikvorgaben als 'vorläufig erfüllt' betrachtet werden und keine marktregulierenden Maßnahmen erforderlich sind, was impliziert, dass die Charge bereits im Handel ist (Quote 3: 'bereits im Juni 2025 vollständig in den Handel überführt'). Da die Abweichungsbewertung zum Zeitpunkt der Freigabe/Vermarktung offensichtlich nicht abgeschlossen war (Re-Testing läuft noch), liegt ein Verstoß gegen die Regel 'Keine Freigabe vor abgeschlossener Bewertung' vor. Die Behauptung der 'vorläufigen Erfüllung' ist keine abgeschlossene Bewertung im Sinne der GMP-Anforderung.
- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 2 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
