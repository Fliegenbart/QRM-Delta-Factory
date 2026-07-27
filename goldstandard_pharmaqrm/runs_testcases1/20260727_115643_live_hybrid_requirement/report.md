# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid` | Engine: `requirement`
- Zeitpunkt: 2026-07-27T11:56:43+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 40 von 41 versteckten Fehlern gefunden (98%)
- **In Prüfmappe sichtbar:** 40 von 41 versteckten Fehlern (98%)
- **Spezifität (Decoys):** 20 von 20 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 96 von 170 (56%) — 33 als Treffer gewertet, 63 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 74 von 170 (44%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 17.0 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 134 von 170 Findings mit verifiziertem Zitat (79%)

## Qualitätsmetriken

- Must-detect Recall: `0.9756`
- Wiederholungen: `63` (Redundanzrate `0.6562`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `21/5/14`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 122 | 201,048 | 38,408 | 239,456 |
| mistral | 40 | 167,998 | 80,158 | 248,156 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 17 | 0 | 14 | 3/4 | 3/4 | 0/2 | - |
| CASE_02 | completed | 0 | 18 | 0 | 14 | 4/4 | 4/4 | 0/2 | - |
| CASE_03 | completed | 0 | 17 | 6 | 8 | 4/4 | 4/4 | 0/2 | - |
| CASE_04 | completed | 0 | 16 | 7 | 5 | 4/4 | 4/4 | 0/2 | - |
| CASE_05 | completed | 0 | 15 | 8 | 4 | 4/4 | 4/4 | 0/2 | - |
| CASE_06 | completed | 0 | 19 | 7 | 9 | 3/3 | 3/3 | 0/2 | - |
| CASE_07 | completed | 0 | 12 | 4 | 5 | 4/4 | 4/4 | 0/2 | - |
| CASE_08 | completed | 0 | 19 | 11 | 5 | 5/5 | 5/5 | 0/2 | - |
| CASE_09 | completed | 0 | 19 | 10 | 5 | 4/4 | 4/4 | 0/2 | - |
| CASE_10 | completed | 0 | 18 | 10 | 5 | 5/5 | 5/5 | 0/2 | - |

### CASE_01

- ✅ `CASE01-E001` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass elektronische Unterschriften Name, Datum, Zeit und Bedeutung enthalten und zeitlich plausibel sind. Im Deviation Report (DEV-2603-041) fehlt die Unterschrift der Abteilungsleitung Produktion (PL-03) trotz dokumentiertem Datum (2026-03-15). Dies stellt einen Datenintegritätsbefund dar, da die Signatur nicht vollständig geleistet wurde. Zudem ist die Korrektur der IPC-Probennummer (P-24-090 auf P-24-091) zwar dokumentiert, aber es gibt keine unabhängige Bestätigung der zeitlichen Plausibilität dieser Korrektur (z. B. durch einen Audit-Trail).
- ✅ `CASE01-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2603-041 ist belegt (document_01_deviation_report.md, Chunk chunk_d80b5d4946024c859ce24ad777b99e26_p1), jedoch fehlt eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit. Die vorläufige Bewertung stuft die Abweichung lediglich als 'niedrig' ein, ohne eine detaillierte Impact-Assessment-Dokumentation oder eine Chargenliste potenziell betroffener Chargen vorzulegen. Der CAPA-Plan (document_03_capa_plan.md) und die Quality Approval Note (document_04_quality_approval_note.md) enthalten keine Hinweise auf eine durchgeführte Impact-Assessment.
- ✅ `CASE01-E003` (high) — gefunden via evidence_substring (Score 1.0): Die IPC-Ergebnisse (Feuchte nach Trocknung: 1.8 %, Korngrößenanteil > 1.0 mm: 2.4 %) wurden gegen die im Batch Manufacturing Record (BMR) genannten Akzeptanzkriterien (Feuchte: 1.0 - 2.5 %; Korngrößenanteil: NMT 5.0 %) bewertet und liegen innerhalb der Spezifikationen. Die Ausbeute (91.2 %) wurde ebenfalls als plausibel dokumentiert bewertet, obwohl sie leicht unter der Soll-Ausbeute (95.0 - 101.0 %) liegt, da dies explizit als nicht bewertungsrelevant eingestuft wurde.
- ❌ `CASE01-E004` (medium) — übersehen: CAPA-Maßnahme 1 hat keinen benannten Verantwortlichen.
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `CASE02-E001` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Aufzeichnungen zurechenbar, lesbar, zeitgleich, original, korrekt und vollständig sein müssen. Die vorliegenden Dokumente (Deviation Report, Batch Record, EM Report, CAPA Plan, Quality Approval Note) enthalten durchgängig Pflichtangaben wie Dokument-ID, Datum, Verantwortliche, Unterschriften und Inhalte, die den ALCOA+-Kriterien entsprechen. Es gibt keine Hinweise auf fehlende oder nachträglich veränderte Originaldaten.
- ✅ `CASE02-E002` (high) — gefunden via evidence_substring (Score 1.0): Die nichtviable Partikelmessung von 1.240 Partikeln ≥0,5 µm/m³ in der Klasse-A-Zone während des Eingriffs überschreitet das interne Action Limit von 550 Partikeln ≥0,5 µm/m³. Dies stellt eine Verletzung interner Akzeptanzkriterien dar, da die Spezifikation nicht eingehalten wurde. Zudem wurde das Füllvolumen-IPC (4,82 mL bei Akzeptanzkriterium 4,90–5,10 mL) nicht bewertet, obwohl es außerhalb des Akzeptanzbereichs lag. Beide Verstöße sind belegt, aber nicht als Abweichung behandelt.
- ✅ `CASE02-E003` (high) — gefunden via evidence_substring (Score 1.0): Der kritische Prozessparameter Füllvolumen lag in Stichprobe 12 (15:30 Uhr) mit 4.82 mL außerhalb des Akzeptanzkriteriums (4.90 - 5.10 mL). Dies ist eine Überschreitung der spezifizierten Grenzen und muss als Abweichung bewertet werden. Die Dokumentation im Batch Record bestätigt dies, ohne dass eine Bewertung oder Korrekturmaßnahme eingetragen wurde.
- ✅ `CASE02-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Massnahmen (CAPA-2604-037) sind mit einem Qualitätsrisiko verknüpft (Partikelüberschreitung in der Klasse-A-Zone), jedoch fehlt eine definierte und dokumentierte Wirksamkeitsprüfung. Der CAPA-Plan bestätigt explizit, dass keine Wirksamkeitsprüfung vorgesehen ist, obwohl dies für risikobehaftete Massnahmen erforderlich ist.
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `CASE03-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit, einschließlich aller potenziell betroffenen Chargen. Im vorliegenden Fall (Swab B2 Restproteinwert korrigiert) fehlt eine solche Bewertung. Zwar wird die Korrektur als 'dokumentarische Einzelabweichung' bewertet (RCA-2603-031), jedoch ohne konkrete Analyse der Auswirkungen auf die betroffene Charge QRM-CAN-2603-028 oder andere Chargen. Der Auslöser (korrigierter Swab-Wert) ist belegt, der geforderte Nachweis (Impact Assessment) fehlt.
- ✅ `CASE03-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit, einschließlich aller potenziell betroffenen Chargen. Im vorliegenden Fall (Swab B2 Restproteinwert korrigiert) fehlt eine solche Bewertung. Zwar wird die Korrektur als 'dokumentarische Einzelabweichung' bewertet (RCA-2603-031), jedoch ohne konkrete Analyse der Auswirkungen auf die betroffene Charge QRM-CAN-2603-028 oder andere Chargen. Der Auslöser (korrigierter Swab-Wert) ist belegt, der geforderte Nachweis (Impact Assessment) fehlt.
- ✅ `CASE03-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahmen sehen eine Sensibilisierung des Teams und eine Erinnerung an die Dokumentationspraxis vor, jedoch fehlen Nachweise über die Durchführung eines wirksamen Trainings (z. B. Schulungsprotokolle, Unterschriften der Teilnehmer, Wirksamkeitsprüfung). Die bloße Erwähnung der Maßnahmen reicht nicht aus, um die Erfüllung der Anforderung zu belegen.
- ✅ `CASE03-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die QA Approval Note verweist auf Anhang 1 (Reinigungsprotokoll), Anhang 2 (Laborfreigabe) und Anhang 3 (Restproteinbewertung). Diese Anhänge sind in den bereitgestellten Chunks nicht enthalten, daher kann ihre Vollständigkeit und Aktualität nicht bestätigt werden.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `CASE04-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Aufzeichnungen vollständig, konsistent und original sein müssen (ALCOA+). Im Batch Manufacturing Record (BMR-SEL-2604-112-C) wird eine Raumtemperatur von 31.2 °C dokumentiert, die die deklarierte Grenze von 18.0–25.0 °C überschreitet. Es fehlt eine zeitnahe Dokumentation der Ursache für diese Grenzwertüberschreitung oder eine Bewertung der Auswirkung auf die Produktqualität. Die Aufzeichnung ist somit unvollständig, da keine korrigierende oder erklärende Maßnahme dokumentiert ist.
- ✅ `CASE04-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-SEL-2604-112 wurde laut Batch Manufacturing Record (BMR-SEL-2604-112-C) bereits um 10:30 Uhr wieder gestartet, bevor die Abweichungsbewertung und QA-Freigabe abgeschlossen waren. Die QA-Freigabe (QA-N-2604-083) datiert vom 2026-04-23, also fünf Tage nach dem Ereignis. Der Auslöser (Wiederanlauf der Kompression) ist belegt, aber die erforderliche QA-Freigabe vor Freigabe fehlt.
- ✅ `CASE04-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass alle in einem Vorgang referenzierten Pflichtanhänge tatsächlich vorhanden und aktuell sind. Die Dokumente verweisen auf Schulungsunterlagen (SOP-PR-COMP-033) und technische Sichtprüfungen, aber es gibt keine Nachweise, dass diese Anhänge (z. B. Schulungsprotokolle, technische Prüfberichte) als separate Dokumente vorliegen. Die bloße Erwähnung im CAPA-Plan oder Training Record reicht als Nachweis nicht aus.
- ✅ `CASE04-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die Erfassung aller potenziell betroffenen Chargen, einschliesslich Vorgänger- und Folgechargen. Im Deviation Report (DEV-2604-071) und CAPA-Plan (CAPA-2604-049) wird nur die Charge QRM-SEL-2604-112 genannt. Es gibt keine Hinweise auf eine Bewertung von Vorgänger- oder Folgechargen, obwohl die technische Unterbrechung und der Motorwechsel ein Risiko für benachbarte Chargen darstellen könnten. Der Auslöser (technische Unterbrechung) ist belegt, aber der geforderte Nachweis fehlt.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `CASE05-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Out-of-Specification- (OOS) oder Out-of-Trend- (OOT) Ergebnisse vollständig untersucht und bewertet sein müssen, bevor eine Chargen- oder Marktware-Disposition erfolgt. Im vorliegenden Fall wurde eine Abweichung zwischen Lieferantenspezifikation (95,0–105,0 %) und interner Spezifikation (98,0–102,0 %) für den Gehalt der Hauptkomponente festgestellt. Das QC-Lab hat den Gehalt mit 96,9 % als 'bestanden' bewertet, obwohl dieser Wert außerhalb der internen Spezifikation liegt. Es gibt keine dokumentierte OOS/OOT-Untersuchung oder Bewertung dieser Abweichung vor der Freigabeentscheidung in der Quality Approval Note (QA-N-2604-094). Die Charge QRM-NIV-2604-033 wurde zur Freigabe vorgeschlagen, ohne dass die Abweichung untersucht wurde.
- ✅ `CASE05-E002` (medium) — gefunden via evidence_fuzzy (Score 0.41): Die Anforderung verlangt, dass Aufzeichnungen zurechenbar, lesbar, zeitgleich, original, korrekt, vollständig, konsistent, dauerhaft und verfügbar sein müssen (ALCOA+). Die bereitgestellten Dokumente (Supplier CoA, interne Spezifikation, QC-Lab Result Sheet, Material Deviation Report, Quality Approval Note) enthalten durchgängig signierte und datierte Einträge, die den ALCOA+-Kriterien entsprechen. Es gibt keine Hinweise auf fehlende oder nachträglich veränderte Originaldaten. Die Audit-Trail-Prüfung in der Quality Approval Note bestätigt die Vollständigkeit und Konsistenz der Aufzeichnungen.
- ✅ `CASE05-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die vollständige Erfassung aller potenziell betroffenen Chargen, einschließlich Vorgänger- und Folgechargen. Der Material Deviation Report (DEV-2604-063) listet zwar zwei Chargen (QRM-NIV-2604-031 und QRM-NIV-2604-033) auf, die das betroffene Material verwendet haben, es gibt jedoch keine Evidenz dafür, dass Vorgänger- oder Folgechargen (z. B. QRM-NIV-2604-032 oder QRM-NIV-2604-034) geprüft oder berücksichtigt wurden. Die Quality Approval Note (QA-N-2604-094) beschränkt die Bewertung explizit auf QRM-NIV-2604-033 und schließt bereits ausgelieferte Chargen aus, ohne eine Prüfung auf weitere betroffene Chargen zu dokumentieren.
- ✅ `CASE05-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Aufzeichnungen zurechenbar, lesbar, zeitgleich, original, korrekt, vollständig, konsistent, dauerhaft und verfügbar sein müssen (ALCOA+). Die bereitgestellten Dokumente (Supplier CoA, interne Spezifikation, QC-Lab Result Sheet, Material Deviation Report, Quality Approval Note) enthalten durchgängig signierte und datierte Einträge, die den ALCOA+-Kriterien entsprechen. Es gibt keine Hinweise auf fehlende oder nachträglich veränderte Originaldaten. Die Audit-Trail-Prüfung in der Quality Approval Note bestätigt die Vollständigkeit und Konsistenz der Aufzeichnungen.
- 🔁 8 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `CASE06-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen zur Sterilfiltration (document_01_batch_record_excerpt.md) enthalten einen erhöhten Differenzdruck-Peak (3.6 bar), der die validierte Grenze von ≤3.2 bar (document_02_validation_note.md) überschreitet. Diese Abweichung wurde im BMR nicht zeitgleich dokumentiert oder begründet. Zudem fehlt die Change-Control-Nummer im Wartungsauftrag (document_03_maintenance_note.md), was die Nachvollziehbarkeit der Aufzeichnungen beeinträchtigt.
- ✅ `CASE06-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die Erfassung aller potenziell betroffenen Chargen, einschließlich Vorgänger- und Folgechargen. Die Dokumente nennen ausschließlich die Charge QRM-ORX-2604-009 (siehe chunk_7b286a64e0b54b368561e7e946abb3c0_p1 und chunk_29f90bd0a6c140a3b7ac3610e41cdd92_p1). Es gibt keinen Nachweis über eine Bewertung von Vorgänger- oder Folgechargen, obwohl der Pumpenwechsel (chunk_3e1b2301fc894e0fb0dad9853136c9aa_p1) ein Risiko für andere Chargen darstellt.
- ✅ `CASE06-E003` (medium) — gefunden via evidence_fuzzy (Score 0.5): Die Validierungsnotiz (Chunk chunk_2d07369bdc654492825ae9c8581d861c_p1) bezieht sich auf die Pumpenkonfiguration P-77 (Pumpentyp LFP-120), während die aktuelle Pumpe P-77 durch einen LFP-200 ersetzt wurde (Chunk chunk_3e1b2301fc894e0fb0dad9853136c9aa_p1). Es gibt keine Evidenz, dass die Validierung den aktuellen Prozess- und Equipmentzustand abdeckt.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 9 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `CASE07-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die vollständige Erfassung aller potenziell betroffenen Chargen, einschließlich Vorgänger- und Folgechargen. Im Deviation Report (DEV-2604-081) wird zwar festgestellt, dass 'keine Charge betroffen' ist, jedoch fehlt eine dokumentierte Bewertung oder Begründung, warum Vorgänger- oder Folgechargen (z. B. QRM-LUM-2604-080 oder andere Chargen auf Linie PK-3) nicht berücksichtigt werden müssen. Zudem wird im Quality Approval Note (QA-N-2604-102) ein ähnlicher Etikettenfund (DEV-2601-019) auf derselben Linie erwähnt, was die Pflicht zur Prüfung weiterer Chargen unterstreicht. Es gibt keine Evidenz, dass eine solche Prüfung durchgeführt wurde.
- ✅ `CASE07-E002` (medium) — gefunden via evidence_fuzzy (Score 0.505): Die Anforderung verlangt, dass CAPA-Maßnahmen mit einem Qualitätsrisiko nur mit definierter und dokumentierter Wirksamkeitsprüfung abgeschlossen werden dürfen. Im CAPA Plan (CAPA-2604-061) ist zwar eine Wirksamkeitsprüfung ('Review der nächsten fünf Aufträge auf PK-3 auf Etikettenfund') vorgesehen, jedoch fehlt der Nachweis, dass diese Wirksamkeitsprüfung tatsächlich durchgeführt und dokumentiert wurde. Der Status der Maßnahme Nr. 2 ('Checkliste Line Clearance ergänzen') ist zudem als 'offen' markiert, was bedeutet, dass die CAPA noch nicht abgeschlossen ist. Es gibt keine Evidenz für einen Effectiveness Check.
- ✅ `CASE07-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die vollständige Erfassung aller potenziell betroffenen Chargen, einschließlich Vorgänger- und Folgechargen. Im Deviation Report (DEV-2604-081) wird zwar festgestellt, dass 'keine Charge betroffen' ist, jedoch fehlt eine dokumentierte Bewertung oder Begründung, warum Vorgänger- oder Folgechargen (z. B. QRM-LUM-2604-080 oder andere Chargen auf Linie PK-3) nicht berücksichtigt werden müssen. Zudem wird im Quality Approval Note (QA-N-2604-102) ein ähnlicher Etikettenfund (DEV-2601-019) auf derselben Linie erwähnt, was die Pflicht zur Prüfung weiterer Chargen unterstreicht. Es gibt keine Evidenz, dass eine solche Prüfung durchgeführt wurde.
- ✅ `CASE07-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass keine Charge freigegeben wird, bevor Abweichungsbewertung, Impact Assessment oder QA-Freigabe abgeschlossen sind. Im Quality Approval Note (QA-N-2604-102) wird zwar eine Freigabeempfehlung für eine *andere* Charge (QRM-LUM-2604-088) ausgesprochen, jedoch fehlt ein klarer Nachweis, dass die betroffene Charge QRM-LUM-2604-080 (oder andere Chargen) nicht vor Abschluss der Bewertung freigegeben wurde. Der Packaging Record (PKR-LUM-2604-080) zeigt, dass die Verpackung nach dem Vorfall fortgesetzt wurde, aber es gibt keine dokumentierte QA-Freigabe *vor* der Fortsetzung. Die Evidenz reicht nicht aus, um die Einhaltung oder Verletzung der Anforderung zu belegen.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `CASE08-E001` (critical) — gefunden via evidence_substring (Score 1.0): Der Change Control (CC-2604-011) dokumentiert die Einführung des Auto-Endpunkt Algorithmus AE-2, jedoch fehlt eine dokumentierte Auswirkungsbewertung oder Validierungsprüfung. Der Status der Implementierung ist 'ausstehend', und die vorläufige Nutzung im Routinebetrieb ist nicht freigegeben. Die Quality Approval Note (QA-N-2604-117) bewertet den Validierungsstatus als 'akzeptabel', ohne eine konkrete Validierungsbewertung oder -dokumentation zu referenzieren.
- ✅ `CASE08-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Freigabeentscheidung für die Charge QRM-MER-2604-052 ist im Quality Approval Note (QA-N-2604-117) dokumentiert, jedoch fehlt eine explizite Verknüpfung der Dispositionsentscheidung mit den Batch Records. Der Batch Record (BMR-MER-2604-052-D) enthält zwar den LOD-Wert, aber keine direkte Referenzierung der Freigabeentscheidung oder eine Begründung, warum der LOD-Wert außerhalb der Spezifikation (NMT 2.5 %) akzeptiert wurde.
- ✅ `CASE08-E003` (critical) — gefunden via evidence_substring (Score 1.0): Die Unterlagen belegen, dass der Deviation Report (DEV-2604-095) zwar die Charge QRM-MER-2604-052 und die vorherige Charge QRM-MER-2604-046 erwähnt, jedoch keine Bewertung oder Erfassung der Folgechargen (z. B. geplante Charge ab 2026-07-14) erfolgt. Der Auslöser für die Pflicht zur Erfassung aller potenziell betroffenen Chargen ist der Driftverdacht des Feuchtesensors RH-D17, der im Deviation Report dokumentiert ist.
- ✅ `CASE08-E004` (critical) — gefunden via evidence_substring (Score 1.0): Die Unterlagen belegen, dass der Deviation Report (DEV-2604-095) zwar die Charge QRM-MER-2604-052 und die vorherige Charge QRM-MER-2604-046 erwähnt, jedoch keine Bewertung oder Erfassung der Folgechargen (z. B. geplante Charge ab 2026-07-14) erfolgt. Der Auslöser für die Pflicht zur Erfassung aller potenziell betroffenen Chargen ist der Driftverdacht des Feuchtesensors RH-D17, der im Deviation Report dokumentiert ist.
- ✅ `CASE08-E005` (medium) — gefunden via evidence_substring (Score 1.0): Die Unterlagen belegen, dass der Deviation Report (DEV-2604-095) zwar die Charge QRM-MER-2604-052 und die vorherige Charge QRM-MER-2604-046 erwähnt, jedoch keine Bewertung oder Erfassung der Folgechargen (z. B. geplante Charge ab 2026-07-14) erfolgt. Der Auslöser für die Pflicht zur Erfassung aller potenziell betroffenen Chargen ist der Driftverdacht des Feuchtesensors RH-D17, der im Deviation Report dokumentiert ist.
- 🔁 11 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `CASE09-E001` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme Nr. 1 sieht ein Retraining des Operators OP-44 auf das Einrasten der Sprühlanze vor (Termin: 2026-03-20). Die Reinigung wurde jedoch bereits am 2026-03-12 durchgeführt, also *vor* dem geplanten Retraining. Damit fehlt der Nachweis, dass das betroffene Personal wirksam geschult war, bevor die Tätigkeit ausgeführt wurde. Der Auslöser für die Pflicht ist die dokumentierte Abweichung (Sprühverteilung) in der Reinigung.
- ✅ `CASE09-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Cleaning Validation Note (VAL-CLN-FB22 Rev.05) bestätigt, dass jede Änderung der Detergentkonzentration einen Change Control und eine dokumentierte Brückenbewertung erfordert. Der RCA/CAPA-Report stellt fest, dass Change Control für die Detergentkonzentration nicht anwendbar ist, da die Endwerte bestanden. Diese Bewertung ist dokumentiert und begründet.
- ✅ `CASE09-E003` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahmen (Retraining und Erinnerung an zeitnahe Dokumentation) sind dokumentiert, aber es gibt keinen Nachweis einer definierten oder durchgeführten Wirksamkeitsprüfung. Die Wirksamkeit soll laut CAPA-Record durch 'Review der nächsten Reinigung' bzw. 'Schichtprotokoll' geprüft werden, aber es fehlen konkrete Kriterien oder Ergebnisse dieser Prüfung.
- ✅ `CASE09-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass die Grundursache einer Abweichung durch eine angemessene Untersuchung belegt ist. Im RCA/CAPA-Bericht (RCA-CAPA-2603-057) wird die Grundursache als 'Operator hat Sprühlanze N-4 nicht vollständig in Reinigungsposition eingerastet' angegeben. Allerdings fehlt der dokumentierte Ausschluss technischer Ursachen (z. B. Equipment, Kalibrierung, Alarme). Die Wartungsnotiz (MTN-2603-049) beschreibt zwar eine partielle Blockade der Sprühdüse, jedoch wird diese nicht mit der Abweichung in der Reinigung verknüpft oder als technische Ursache ausgeschlossen.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `CASE10-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ZEP-2604-014 wurde zur Freigabe empfohlen, obwohl die Abweichungsbewertung (DEV-2604-074) und das Change Control (CC-2604-019) zum Zeitpunkt der Freigabeentscheidung nicht abgeschlossen waren. Die EM-Abweichung DEV-2604-074 blieb offen, und das APS-Bridging sowie die QA-Freigabe für den Change Control waren ausstehend.
- ✅ `CASE10-E002` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ZEP-2604-014 wurde zur Freigabe empfohlen, obwohl die Abweichungsbewertung (DEV-2604-074) und das Change Control (CC-2604-019) zum Zeitpunkt der Freigabeentscheidung nicht abgeschlossen waren. Die EM-Abweichung DEV-2604-074 blieb offen, und das APS-Bridging sowie die QA-Freigabe für den Change Control waren ausstehend.
- ✅ `CASE10-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Grundursache der Abweichung DEV-2604-074 (2 KBE im Stopfentrichter SB-9) ist nicht durch eine angemessene Untersuchung belegt. Es fehlt der dokumentierte Ausschluss technischer Ursachen (z. B. Equipment, Kalibrierung). Die Abweichung wird lediglich mit dem manuellen Eingriff des OP-SG in Verbindung gebracht, ohne weitere technische oder prozessuale Ursachenanalyse.
- ✅ `CASE10-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ZEP-2604-014 wurde zur Freigabe empfohlen, obwohl die Abweichungsbewertung (DEV-2604-074) und das Change Control (CC-2604-019) zum Zeitpunkt der Freigabeentscheidung nicht abgeschlossen waren. Die EM-Abweichung DEV-2604-074 blieb offen, und das APS-Bridging sowie die QA-Freigabe für den Change Control waren ausstehend.
- ✅ `CASE10-E005` (high) — gefunden via evidence_substring (Score 1.0): Die Einstufung der Abweichung DEV-2604-074 als 'low' ist nicht durch eine nachvollziehbare Risikobewertung mit belastbaren physikalisch-chemischen oder labortechnischen Daten belegt. Die QA-Note (Chunk chunk_2485106c908442c08a5f777055f2df0e_p1) bestätigt lediglich die Einstufung ohne detaillierte Risikobewertung oder unterstützende Daten.
- 🔁 10 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
