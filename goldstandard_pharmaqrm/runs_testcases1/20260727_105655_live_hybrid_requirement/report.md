# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid` | Engine: `requirement`
- Zeitpunkt: 2026-07-27T10:56:55+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 35 von 41 versteckten Fehlern gefunden (85%)
- **In Prüfmappe sichtbar:** 35 von 41 versteckten Fehlern (85%)
- **Spezifität (Decoys):** 20 von 20 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 87 von 171 (51%) — 31 als Treffer gewertet, 56 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 84 von 171 (49%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 17.1 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 142 von 171 Findings mit verifiziertem Zitat (83%)

## Qualitätsmetriken

- Must-detect Recall: `0.8537`
- Wiederholungen: `56` (Redundanzrate `0.6437`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `14/5/16`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 117 | 193,938 | 38,280 | 232,218 |
| mistral | 40 | 164,061 | 77,791 | 241,852 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 16 | 0 | 13 | 3/4 | 3/4 | 0/2 | - |
| CASE_02 | completed | 0 | 19 | 3 | 12 | 4/4 | 4/4 | 0/2 | - |
| CASE_03 | completed | 0 | 18 | 0 | 17 | 1/4 | 1/4 | 0/2 | - |
| CASE_04 | completed | 0 | 17 | 7 | 7 | 3/4 | 3/4 | 0/2 | - |
| CASE_05 | completed | 0 | 15 | 10 | 2 | 4/4 | 4/4 | 0/2 | - |
| CASE_06 | completed | 0 | 20 | 6 | 11 | 3/3 | 3/3 | 0/2 | - |
| CASE_07 | completed | 0 | 13 | 5 | 5 | 4/4 | 4/4 | 0/2 | - |
| CASE_08 | completed | 0 | 18 | 10 | 4 | 5/5 | 5/5 | 0/2 | - |
| CASE_09 | completed_with_model_failures | 0 | 15 | 5 | 7 | 3/4 | 3/4 | 0/2 | - |
| CASE_10 | completed | 0 | 20 | 10 | 6 | 5/5 | 5/5 | 0/2 | - |

## Modellausfälle

- **ProviderStructuredOutputError** (1×): 3 validation errors for RequirementGroupOutput
requirement_id
  Extra inputs are not permitted [type=extra_forbidden, input_value='req_supplier_change_impact', 
  - betroffen: CASE_09/assess:3

### CASE_01

- ✅ `CASE01-E001` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass elektronische Unterschriften Name, Datum, Zeit und Bedeutung enthalten und zeitlich plausibel sind. Im Deviation Report (DEV-2603-041) fehlt die Unterschrift der Abteilungsleitung Produktion (PL-03) zum Datum 2026-03-15, obwohl das Feld vorgesehen ist. Dies stellt einen Verstoß gegen die Plausibilität und Vollständigkeit der Signaturdaten dar.
- ✅ `CASE01-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit, einschließlich aller potenziell betroffenen Chargen. Im Deviation Report (DEV-2603-041) wird lediglich eine vorläufige Bewertung als 'niedrig' vorgenommen, ohne detaillierte Auswirkungsanalyse oder Chargenliste. Die Quality Approval Note (QA-N-2603-044) bestätigt, dass die Charge bis zur vollständigen Abweichungsbewertung gesperrt bleibt, was impliziert, dass die Auswirkungsbewertung noch aussteht. Es fehlt somit der geforderte Nachweis.
- ✅ `CASE01-E003` (high) — gefunden via evidence_substring (Score 1.0): Die IPC-Ergebnisse (Feuchte nach Trocknung: 1.8 %, Korngrößenanteil > 1.0 mm: 2.4 %) werden im Batch Manufacturing Record explizit gegen die Akzeptanzkriterien bewertet und liegen innerhalb der spezifizierten Grenzen (Feuchte: 1.0 - 2.5 %; Korngrößenanteil: NMT 5.0 %). Die Ausbeute (91.2 %) wird ebenfalls als plausibel dokumentiert bewertet, obwohl sie außerhalb des Soll-Bereichs (95.0 - 101.0 %) liegt, da dies gesondert begründet ist.
- ❌ `CASE01-E004` (medium) — übersehen: CAPA-Maßnahme 1 hat keinen benannten Verantwortlichen.
- ℹ️ 13 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `CASE02-E001` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass elektronische Unterschriften Name, Datum und Zeit der Signatur sowie deren Bedeutung enthalten und dass diese Angaben zeitlich plausibel und konsistent mit dem Vorgang sind. Im Deviation Report (DEV-2604-058) ist das Datum der Feststellung mit '2026-04-31' angegeben, was ein ungültiges Datum ist (April hat nur 30 Tage). Dies stellt einen Datenintegritätsbefund dar, da das Datum nicht plausibel ist.
- ✅ `CASE02-E002` (high) — gefunden via evidence_substring (Score 1.0): Die nichtviable Partikelmessung von 1.240 Partikeln ≥0,5 µm/m³ in der Klasse-A-Zone während des Eingriffs überschreitet das interne Action Limit von 550 Partikeln. Dies ist im Environmental Monitoring Report (EM-2604-116) dokumentiert. Allerdings fehlt im Deviation Report (DEV-2604-058) und im Quality Approval Note (QA-N-2605-012) eine explizite Bewertung dieser Überschreitung gegen die interne Spezifikation. Die bloße Einstufung als 'minor' ohne weitere Begründung oder Risikobewertung reicht nicht aus, um die Anforderung zu erfüllen.
- ✅ `CASE02-E003` (high) — gefunden via evidence_substring (Score 1.0): Das Füllvolumen-IPC (Stichprobe 12) lag mit 4.82 mL außerhalb des Akzeptanzkriteriums (4.90–5.10 mL), wurde jedoch ohne dokumentierte Bewertung oder OOS-Untersuchung fortgesetzt. Eine Dispositionsentscheidung (z. B. Freigabe oder Verwerfung der Charge) erfolgte vor Abschluss der erforderlichen Untersuchung.
- ✅ `CASE02-E004` (medium) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan (CAPA-2604-037) sieht keine Wirksamkeitsprüfung für die administrativen Maßnahmen (Wiederholung der Schulung, Ergänzung des Hinweises) vor. Die Anforderung verlangt jedoch eine definierte und dokumentierte Wirksamkeitsprüfung für CAPA-Maßnahmen, die mit einem Qualitätsrisiko verknüpft sind. Die Partikelüberschreitung stellt ein Qualitätsrisiko dar, daher ist der fehlende Effectiveness Check ein Verstoß.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `CASE03-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass die Grundursache einer Abweichung durch eine angemessene Untersuchung belegt sein muss. Eine Zuschreibung als 'Bedienerfehler' ist nur zulässig, wenn technische Ursachen dokumentiert ausgeschlossen wurden. Die Root Cause Analysis (Chunk chunk_011b7f69aeb64201b438cfa4b43c6a72_p1) nennt als Root Cause "kurzzeitige Unaufmerksamkeit bei Sprühposition B", ohne technische Ursachen (z. B. Equipment, Kalibrierung) zu prüfen oder zu dokumentieren. Zudem fehlen Nachweise für eine Befragung des Reinigungspersonals oder eine protokollierte Untersuchung.
- ❌ `CASE03-E001` (high) — übersehen: Swab-Ergebnis wurde geändert, aber Änderungsgrund und Änderungsdatum fehlen.
- ❌ `CASE03-E003` (medium) — übersehen: CAPA-Maßnahme ist zu allgemein formuliert.
- ❌ `CASE03-E004` (medium) — übersehen: QA-Note verweist auf nicht vorhandenen Anhang 3.
- ℹ️ 17 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `CASE04-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Aufzeichnungen vollständig, original, zeitgleich und korrekt sind (ALCOA+). Im Batch Manufacturing Record (BMR-SEL-2604-112-C) wird eine Raumtemperatur von 31.2 °C dokumentiert, die außerhalb des definierten Grenzbereichs (18.0–25.0 °C) liegt. Es fehlt eine zeitnahe Dokumentation der Ursache für diese Grenzwertüberschreitung oder eine Korrekturmaßnahme. Die Aufzeichnung ist somit unvollständig, da keine Begründung für die Abweichung oder eine Nachverfolgbarkeit der Maßnahmen vorliegt. Der Auslöser für diese Pflicht ist die dokumentierte Grenzwertüberschreitung im BMR.
- ✅ `CASE04-E003` (medium) — gefunden via evidence_fuzzy (Score 0.422): Die Charge QRM-SEL-2604-112 wurde vor Abschluss der Abweichungsbewertung und der technischen Sichtprüfung wieder in die Produktion genommen. Der Batch Manufacturing Record zeigt, dass die Kompression bereits um 11:25 Uhr wieder aufgenommen wurde, während die technische Sichtprüfung (Maßnahme 2 im CAPA-Plan) erst am 2026-04-28 abgeschlossen sein sollte. Die Wiederinbetriebnahme ist im Deviation Report dokumentiert: "11:25 Uhr: Produktion nimmt die Kompression wieder auf." Die QA-Note bestätigt, dass die technische Sichtprüfung zum Zeitpunkt der Freigabeempfehlung noch offen war: "QA empfiehlt Fortsetzung in die Beschichtung nach Abschluss der technischen Sichtprüfung."
- ✅ `CASE04-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die Erfassung aller potenziell betroffenen Chargen, einschliesslich Vorgänger- und Folgechargen. Im Deviation Report (DEV-2604-071) und CAPA-Plan (CAPA-2604-049) wird nur die Charge QRM-SEL-2604-112 genannt. Es gibt keinen Nachweis, dass Vorgänger- oder Folgechargen (z. B. QRM-SEL-2604-121, die im Quality Approval Note erwähnt wird) auf Impact bewertet wurden. Der Auslöser für die Pflicht ist die technische Unterbrechung und der Motorwechsel, die im Deviation Report dokumentiert sind: "Während der Tablettenkompression wurde ein ungewöhnliches Geräusch am Hauptmotor der Presse TP-402 gemeldet. Der Schichtleiter veranlasste eine technische Prüfung."
- ❌ `CASE04-E002` (medium) — übersehen: Gleiche Uhrzeit 10:30 dokumentiert widersprüchliche Ereignisse.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `CASE05-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Out-of-Specification- (OOS) oder Out-of-Trend- (OOT) Ergebnisse vollständig untersucht und bewertet sein müssen, bevor eine Chargen- oder Marktware-Disposition erfolgt. Im vorliegenden Fall wurde im Material Deviation Report (DEV-2604-063) eine Abweichung zwischen Lieferantenspezifikation (95,0–105,0 %) und interner Spezifikation (98,0–102,0 %) für den Gehalt der Hauptkomponente festgestellt. Das interne QC-Lab (QC-LAB-2604-221) hat den Gehalt mit 96,9 % als 'bestanden' bewertet, obwohl dieser Wert außerhalb der internen Spezifikation liegt. Es gibt keine dokumentierte OOS/OOT-Untersuchung oder Dispositionsentscheidung vor der Freigabe der Charge QRM-NIV-2604-033. Die Quality Approval Note (QA-N-2604-094) bestätigt lediglich die Freigabe ohne vorherige Untersuchung.
- ✅ `CASE05-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Aufzeichnungen zurechenbar, lesbar, zeitgleich, original und korrekt sowie vollständig, konsistent, dauerhaft und verfügbar sein müssen (ALCOA+). Die Quality Approval Note (QA-N-2604-094) bestätigt, dass eine vollständige Audit-Trail-Prüfung durchgeführt wurde und keine Auffälligkeiten festgestellt wurden. Zudem sind alle relevanten Dokumente (Supplier CoA, interne QC-Ergebnisse, Material Deviation Report, BMR-Materialverwendung) vorhanden und signiert.
- ✅ `CASE05-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die vollständige Erfassung aller potenziell betroffenen Chargen, einschließlich Vorgänger- und Folgechargen. Der Material Deviation Report (DEV-2604-063) listet nur zwei Chargen (QRM-NIV-2604-031 und QRM-NIV-2604-033) auf, die das betroffene Material RM-SX14-2604-02 verwendet haben. Es gibt keinen Nachweis, dass weitere Chargen (z. B. Vorgänger- oder Folgechargen) geprüft oder berücksichtigt wurden. Die vorläufige Bewertung im Deviation Report beschränkt sich explizit auf die genannten Chargen: 'Die laufende QA-Bewertung fokussiert auf QRM-NIV-2604-033. Für freigegebene Chargen ist derzeit keine zusätzliche Maßnahme vorgesehen.'
- ✅ `CASE05-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Aufzeichnungen zurechenbar, lesbar, zeitgleich, original und korrekt sowie vollständig, konsistent, dauerhaft und verfügbar sein müssen (ALCOA+). Die Quality Approval Note (QA-N-2604-094) bestätigt, dass eine vollständige Audit-Trail-Prüfung durchgeführt wurde und keine Auffälligkeiten festgestellt wurden. Zudem sind alle relevanten Dokumente (Supplier CoA, interne QC-Ergebnisse, Material Deviation Report, BMR-Materialverwendung) vorhanden und signiert.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 2 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `CASE06-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen zur Sterilfiltration (BMR-Auszug) sind nicht vollständig im Sinne von ALCOA+. Der Differenzdruck-Peak von 3.6 bar (document_01_batch_record_excerpt.md) überschreitet den validierten maximalen Differenzdruck von ≤3.2 bar (document_02_validation_note.md). Diese Abweichung ist im BMR nicht als solche gekennzeichnet oder begründet. Zudem fehlt die Change-Control-Referenz für den Pumpenwechsel (document_03_maintenance_note.md), was die Nachvollziehbarkeit beeinträchtigt. Die Originalaufzeichnung ist somit unvollständig und inkonsistent.
- ✅ `CASE06-E002` (high) — gefunden via evidence_substring (Score 1.0): Der Pumpenwechsel von LFP-120 auf LFP-200 (Maintenance Note MTN-2604-033) wurde ohne dokumentierte Change-Impact-Assessment oder Validierungsbewertung durchgeführt. Die Validierungsnotiz (VAL-N-2603-018) fordert für Änderungen an Pumpentyp oder Pulsationscharakteristik eine technische Vergleichsbewertung, die nicht vorliegt.
- ✅ `CASE06-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2604-077 ist als kritisch einzustufen (erhöhter Differenzdruck während Sterilfiltration, Pumpenwechsel ohne Change Control). Eine nachvollziehbare Risikobewertung mit belastbaren physikalisch-chemischen oder labortechnischen Daten fehlt jedoch. Die Einstufung als 'mögliche Root Cause: Pumpenpulsation' (document_04_deviation_report.md) ist keine ausreichende Risikobewertung. Die visuelle Unauffälligkeit des Produkts ('Keine sichtbaren Partikel') ersetzt keine labortechnische Bewertung.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 11 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `CASE07-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die Erfassung aller potenziell betroffenen Chargen, einschliesslich Vorgänger- und Folgechargen. Im Deviation Report (DEV-2604-081) wird zwar festgestellt, dass 'keine Charge betroffen' ist, jedoch fehlt eine dokumentierte Bewertung oder Chargenliste, die Vorgänger- oder Folgechargen (z. B. QRM-LUM-2604-079 oder QRM-LUM-2604-081) explizit ausschliesst. Zudem wird im Quality Approval Note (QA-N-2604-102) ein ähnlicher Etikettenfund (DEV-2601-019) auf derselben Linie erwähnt, was die Pflicht zur Prüfung weiterer Chargen verstärkt. Es gibt keine Evidenz, dass diese Prüfung durchgeführt oder dokumentiert wurde.
- ✅ `CASE07-E002` (medium) — gefunden via evidence_fuzzy (Score 0.505): Die Anforderung verlangt, dass CAPA-Maßnahmen mit einem Qualitätsrisiko nur mit definierter und dokumentierter Wirksamkeitsprüfung abgeschlossen werden dürfen. Im CAPA Plan (CAPA-2604-061) ist zwar eine Wirksamkeitsprüfung ('Review der nächsten fünf Aufträge auf PK-3 auf Etikettenfund') vorgesehen, jedoch fehlt der Nachweis, dass diese Wirksamkeitsprüfung tatsächlich durchgeführt und dokumentiert wurde. Der Status der Maßnahme Nr. 2 ('Checkliste Line Clearance um Sichtprüfung Abfallbehälter ergänzen') ist als 'offen' markiert, was bedeutet, dass die CAPA-Maßnahmen noch nicht vollständig umgesetzt sind. Es gibt keine Evidenz, dass die Wirksamkeitsprüfung abgeschlossen oder deren Ergebnisse dokumentiert wurden.
- ✅ `CASE07-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die Erfassung aller potenziell betroffenen Chargen, einschliesslich Vorgänger- und Folgechargen. Im Deviation Report (DEV-2604-081) wird zwar festgestellt, dass 'keine Charge betroffen' ist, jedoch fehlt eine dokumentierte Bewertung oder Chargenliste, die Vorgänger- oder Folgechargen (z. B. QRM-LUM-2604-079 oder QRM-LUM-2604-081) explizit ausschliesst. Zudem wird im Quality Approval Note (QA-N-2604-102) ein ähnlicher Etikettenfund (DEV-2601-019) auf derselben Linie erwähnt, was die Pflicht zur Prüfung weiterer Chargen verstärkt. Es gibt keine Evidenz, dass diese Prüfung durchgeführt oder dokumentiert wurde.
- ✅ `CASE07-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine begründete Dispositionsentscheidung für jede betroffene Charge, verknüpft mit den Batch Records. Im vorliegenden Fall wird im Deviation Report (DEV-2604-081) zwar festgestellt, dass keine Charge betroffen ist, jedoch fehlt eine explizite Dispositionsentscheidung oder Freigabeerklärung für die Charge QRM-LUM-2604-080 im Packaging Record oder Quality Approval Note. Die Freigabeempfehlung im Quality Approval Note bezieht sich auf eine andere Charge (QRM-LUM-2604-088), nicht auf die im Packaging Record genannte Charge QRM-LUM-2604-080. Es gibt keine dokumentierte Verknüpfung zwischen der Dispositionsentscheidung und dem Batch Record der Charge QRM-LUM-2604-080.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `CASE08-E001` (critical) — gefunden via evidence_substring (Score 1.0): Der Change Control CC-2604-011 beschreibt die Einführung des Auto-Endpunkt Algorithmus AE-2, jedoch fehlt eine dokumentierte Auswirkungsbewertung oder Validierungsbewertung. Der Status zeigt, dass die Implementierungsfreigabe aussteht und die PPQ-Läufe noch nicht abgeschlossen sind. Damit ist die Anforderung nicht erfüllt.
- ✅ `CASE08-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Out-of-Specification- (OOS) oder Out-of-Trend- (OOT) Ergebnisse vollständig untersucht und bewertet sein müssen, bevor eine Chargen- oder Marktware-Disposition erfolgt. Im Batch Manufacturing Record (BMR-MER-2604-052-D) wird ein LOD-Wert von 2,8 % dokumentiert, der die Spezifikation von NMT 2,5 % überschreitet. Dieser OOS-Wert wurde ohne abgeschlossene Untersuchung akzeptiert ('Wert akzeptiert, da Stabilitätsbewertung mit NMT 3,5 % geplant'). Zudem fehlt ein OOS-Untersuchungsbericht oder eine Dispositionsentscheidung, die den OOS-Wert abschließend bewertet. Die Charge wurde dennoch zur Freigabe empfohlen (QA-N-2604-117), obwohl die Deviation (DEV-2604-095) offen bleibt und der Sensorfehler nicht bestätigt ist.
- ✅ `CASE08-E003` (critical) — gefunden via evidence_substring (Score 1.0): Die Unterlagen belegen, dass der Deviation Report DEV-2604-095 die vorherige Charge QRM-MER-2604-046 erwähnt, jedoch fehlt eine explizite Impact-Bewertung für diese Charge. Der Stability Assessment STAB-2604-027 beschränkt sich auf QRM-MER-2604-052 und schließt eine Bewertung freigegebener Chargen aus. Damit ist die vollständige Erfassung aller potenziell betroffenen Chargen nicht nachgewiesen.
- ✅ `CASE08-E004` (critical) — gefunden via evidence_substring (Score 1.0): Die Unterlagen belegen, dass der Deviation Report DEV-2604-095 die vorherige Charge QRM-MER-2604-046 erwähnt, jedoch fehlt eine explizite Impact-Bewertung für diese Charge. Der Stability Assessment STAB-2604-027 beschränkt sich auf QRM-MER-2604-052 und schließt eine Bewertung freigegebener Chargen aus. Damit ist die vollständige Erfassung aller potenziell betroffenen Chargen nicht nachgewiesen.
- ✅ `CASE08-E005` (medium) — gefunden via evidence_substring (Score 1.0): Die Quality Approval Note QA-N-2604-117 nennt eine geplante CAPA-Wirksamkeitsprüfung (drei aufeinanderfolgende Folgechargen ohne LOD-Abweichung bis 2026-05-05), jedoch fehlt der Nachweis, dass diese Prüfung tatsächlich durchgeführt und dokumentiert wurde. Damit ist die Wirksamkeitsprüfung der CAPA nicht belegt.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `CASE09-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Reinigungsdokumentation (CR-2603-041) und der RCA/CAPA-Bericht (RCA-CAPA-2603-057) belegen, dass die Reinigung und Bewertung der Abweichung erst nach dem Ende der Abfüllung (2026-03-10) und mit Verzögerung (Reinigung am 2026-03-12) durchgeführt wurden. Es gibt keine Hinweise darauf, dass die Charge QRM-TER-2603-067 vor Abschluss der Bewertung gesperrt oder nicht freigegeben wurde. Die verspätete Reinigungsdokumentation und die technische Abweichung (Sprühverteilung) deuten auf ein Risiko hin, dass die Charge vor Abschluss der Bewertung freigegeben worden sein könnte.
- ✅ `CASE09-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Unterlagen belegen eine dokumentierte Bewertung der Detergentkonzentration im Rahmen des Change-Control-Prozesses. Die Bewertung kommt zu dem Schluss, dass keine Auswirkungen vorliegen ("Change Control für Detergentkonzentration: nicht anwendbar, da Endwerte bestanden"). Die Validierungsnotiz (VAL-CLN-FB22 Rev.05) bestätigt, dass jede Änderung der Detergentkonzentration eine dokumentierte Brückenbewertung erfordert, was hier eingehalten wurde.
- ✅ `CASE09-E003` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahmen (Retraining und Erinnerung an zeitnahe Dokumentation) sind im RCA/CAPA-Bericht dokumentiert, aber es gibt keine definierte oder dokumentierte Wirksamkeitsprüfung (Effectiveness Check). Die Wirksamkeit soll lediglich im "Review der nächsten Reinigung" oder im "Schichtprotokoll" geprüft werden, was keine konkrete, nachvollziehbare Wirksamkeitsprüfung darstellt.
- ❌ `CASE09-E004` (medium) — übersehen: Root Cause 'Operatorfehler' ist nicht ausreichend belegt und widerspricht technischem Befund.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `CASE10-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ZEP-2604-014 wurde zur Freigabe empfohlen (Quality Approval Note QA-N-2604-132), obwohl die Abweichungsbewertung (DEV-2604-074) und das Change Control (CC-2604-019) nicht abgeschlossen waren. Insbesondere fehlte die QA-Freigabe für die Implementierung der geänderten Füllgeschwindigkeit und des Stopfentrichters SB-9.
- ✅ `CASE10-E002` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ZEP-2604-014 wurde zur Freigabe empfohlen (Quality Approval Note QA-N-2604-132), obwohl die Abweichungsbewertung (DEV-2604-074) und das Change Control (CC-2604-019) nicht abgeschlossen waren. Insbesondere fehlte die QA-Freigabe für die Implementierung der geänderten Füllgeschwindigkeit und des Stopfentrichters SB-9.
- ✅ `CASE10-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine belegte Grundursache für die Abweichung. Die EM-Abweichung DEV-2604-074 (Chunk chunk_38f4151a865c4d038c33af84d9bc7310_p1) wurde mit einem KBE-Nachweis im Stopfentrichter SB-9 dokumentiert, jedoch fehlt eine Untersuchung, die technische Ursachen (z. B. Equipment, Kalibrierung) ausschließt. Die Abweichung wird lediglich mit einem 'aseptischen Eingriff' (Chunk chunk_9bfb9ce4e8194e2897b511ea24d920f9_p1) in Verbindung gebracht, ohne weitere Analyse.
- ✅ `CASE10-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Change Control (CC-2604-019) listet als offene Nachweise 'APS-Bridging Bericht' und 'Aktualisierte Interventionsbewertung' auf, die für die Implementierung der geänderten Füllgeschwindigkeit (165 Vials/min) und des neuen Stopfentrichters (SB-9) erforderlich sind. Diese Nachweise sind in den bereitgestellten Chunks nicht vorhanden. Die Quality Approval Note (QA-N-2604-132) erwähnt zwar einen 'Abgleich APS vs Routine' (Anhang MF-3), aber dieser Anhang ist nicht als Dokument in den Chunks enthalten.
- ✅ `CASE10-E005` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit, einschließlich aller potenziell betroffenen Chargen. Die EM-Abweichung DEV-2604-074 (Chunk chunk_38f4151a865c4d038c33af84d9bc7310_p1) wurde zwar als 'low' eingestuft, es fehlt jedoch eine explizite Impact-Assessment-Dokumentation, die die Auswirkung auf die Charge QRM-ZEP-2604-014 oder andere Chargen bewertet. Die QA-Note (Chunk chunk_799e9b6c4c6640d0a096c2c0bd2898de_p1) bestätigt lediglich die Einstufung als 'low' und verweist auf eine 'prozessnahe' Bewertung, ohne konkrete Daten oder eine Chargenliste vorzulegen.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
