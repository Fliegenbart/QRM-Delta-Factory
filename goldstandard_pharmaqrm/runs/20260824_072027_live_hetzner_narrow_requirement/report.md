# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hetzner` | Engine: `requirement`
- Zeitpunkt: 2026-08-24T07:20:27+00:00
- Anthropic-Modell: `-`
- OpenAI-Modell: `-`
- Hetzner-Modell: `Qwen3.8-27B`

## Gesamtergebnis

- **Sensitivität:** 14 von 16 versteckten Fehlern gefunden (88%)
- **In Prüfmappe sichtbar:** 14 von 16 versteckten Fehlern (88%)
- **Spezifität (Decoys):** 16 von 16 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 46 von 98 (47%) — 14 als Treffer gewertet, 32 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 52 von 98 (53%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 12.2 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 81 von 98 Findings mit verifiziertem Zitat (83%)

## Qualitätsmetriken

- Must-detect Recall: `0.875`
- Wiederholungen: `32` (Redundanzrate `0.6957`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `7/5/2`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| hetzner | 549 | 1,389,479 | 127,632 | 1,517,111 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_11 | completed_with_model_failures | 0 | 16 | 8 | 6 | 2/2 | 2/2 | 0/2 | - |
| CASE_12 | completed_with_model_failures | 0 | 11 | 0 | 11 | 0/2 | 0/2 | 0/2 | - |
| CASE_13 | completed_with_model_failures | 0 | 12 | 4 | 6 | 2/2 | 2/2 | 0/2 | - |
| CASE_14 | completed_with_model_failures | 0 | 9 | 3 | 4 | 2/2 | 2/2 | 0/2 | - |
| CASE_15 | completed_with_model_failures | 0 | 12 | 5 | 5 | 2/2 | 2/2 | 0/2 | - |
| CASE_16 | completed_with_model_failures | 0 | 13 | 4 | 7 | 2/2 | 2/2 | 0/2 | - |
| CASE_17 | completed_with_model_failures | 0 | 13 | 3 | 8 | 2/2 | 2/2 | 0/2 | - |
| CASE_18 | completed_with_model_failures | 0 | 12 | 5 | 5 | 2/2 | 2/2 | 0/2 | - |

## Modellausfälle

- **ProviderCallError** (35×): hetzner provider call failed with HTTP 504
  - betroffen: CASE_11/locate:22, CASE_11/locate:34, CASE_12/locate:6, CASE_12/locate:27, CASE_12/locate:30, CASE_12/extract[doc_3ab0e52064434aee994a5213d66756c2:werte]:72
  - … und 29 weitere
- **ProviderCallError** (6×): hetzner provider output was truncated
  - betroffen: CASE_11/locate:3, CASE_11/locate:21, CASE_11/locate:24, CASE_11/locate:27, CASE_12/locate:16, CASE_18/locate:38

### CASE_11

- ✅ `ERR_11_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Bewertung der Auswirkung auf die Produktqualität und Patientensicherheit, einschließlich aller potenziell betroffenen Chargen. Die vorliegenden Zitate und Dokumente belegen zwar die Feststellung der Abweichung (Zitat 0), die Einleitung der Untersuchung und die Quarantäne der spezifischen Charge OND-2026-F031 (Zitat 1 und 2). Es fehlt jedoch in den Auszügen eine explizite, dokumentierte Risiko- oder Auswirkungsbewertung (Impact Assessment), die die potenzielle Beeinträchtigung der Produktqualität und Patientensicherheit analysiert. Zudem wird keine Liste oder Bewertung anderer potenziell betroffener Chargen (z. B. durch denselben Filter oder Prozess) vorgelegt. Da der geforderte Nachweis der Auswirkungsbewertung in den Auszügen fehlt, während der auslösende Vorgang (Abweichung) belegt ist, liegt ein Verstoß vor. Die Maßnahme 'Umgebungsmonitoring der Abfüllung (Luftkeime, Sedimentationsplatten, Partikel) für den Zeitraum 05.06.2026 ausgewertet: alle Ergebnisse innerhalb der Aktionslimits (Partikel ≥0,5 µm: 1.120/m³ bei Limit 3.520/m³).' in 'Sofortmaßnahmen' hat keinen benannten Verantwortlichen. Im CAPA-Plan fehlt der regulatorisch geforderte Effectiveness Check (Wirksamkeitsprüfung) für 3 Maßnahme(n), z. B. 'Charge OND-2026-F031 in Quarantäne (Status 'Hold') gesetzt.'.
- ✅ `ERR_11_02` (high) — gefunden via evidence_substring (Score 1.0): 'QA-Review abgeschlossen' ist auf 03.06.2026 datiert, das zugehörige Ereignis 'Abweichung festgestellt und gemeldet.' erst auf 05.06.2026 14:20. Ein Schritt kann nicht vor dem Ereignis liegen, das er betrifft. 'QA-Review abgeschlossen' ist auf 03.06.2026 datiert, das zugehörige Ereignis 'Abweichung festgestellt und gemeldet.' erst auf 05.06.2026 14:20. Ein Schritt kann nicht vor dem Ereignis liegen, das er betrifft. 'QA-Review durchgeführt' ist auf 03.06.2026 datiert, das zugehörige Ereignis 'Abweichung festgestellt und gemeldet.' erst auf 05.06.2026 14:20. Ein Schritt kann nicht vor dem Ereignis liegen, das er betrifft.
- 🔁 8 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_12

- ❌ `ERR_12_01` (critical) — übersehen: Chargenfreigabe vor Abschluss der Risikobewertung und vor Vorliegen der relevanten Prüfergebnisse.
- ❌ `ERR_12_02` (high) — übersehen: Ersteller und Prüfer/Freigeber der Risikobewertung sind dieselbe Person; Vier-Augen-Prinzip verletzt.
- ℹ️ 11 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_13

- ✅ `ERR_13_01` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Dokumente belegen einen Verstoß gegen die zeitliche Reihenfolge der Schulung und Anwendung. Die Analyse (PB-2026-1147) wurde am 20.04.2026 unter Verwendung der neuen Methode PM-HPLC-044 Rev. 5 durchgeführt (Zitat 2 und 3). Die Schulung des betroffenen Personals auf diese Revision fand jedoch erst am 22.04.2026 statt (Zitat 0 und 1). Damit wurde die SOP-Version vor der geforderten Schulung angewendet. Zudem fehlt in den Auszügen eine begründete Einstufung als nicht trainingsrelevant, die diesen Widerspruch hätte rechtfertigen können.
- ✅ `ERR_13_02` (high) — gefunden via evidence_substring (Score 1.0): Das Zitat (Index 0) behauptet zwar, dass ein Audit-Trail-Review durchgeführt wurde und keine Auffälligkeiten vorlagen, es handelt sich dabei jedoch um eine nachträgliche Selbstauskunft im Rahmen der Änderungskontrolle. Gemäß den Review-Regeln belegt eine solche Behauptung ohne Primärevidenz (wie z. B. einen Auszug aus dem Audit Trail, eine signierte Checkliste oder Rohdaten) keine tatsächliche Durchführung. Da die geforderte Primärevidenz in den vorliegenden Auszügen fehlt, kann die Erfüllung der Anforderung nicht bestätigt werden. Da es sich um einen GxP-relevanten Vorgang handelt und der Nachweis fehlt, ist der Status 'unclear' mit der Schwere 'high' zu vergeben, da die Anforderung eine hohe Kritikalität besitzt.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_14

- ✅ `ERR_14_01` (high) — gefunden via evidence_fuzzy (Score 0.55): Die Maßnahme 'Aussortierte Faltschachteln zur Vernichtung vorgesehen.' in 'Sofortmaßnahmen' hat keinen benannten Verantwortlichen. Die Maßnahme 'Aussortierte Faltschachteln zur Vernichtung vorgesehen.' in 'Sofortmaßnahmen' hat keinen benannten Verantwortlichen. Die Maßnahme 'Vernichtung der aussortierten Faltschachteln' in 'Entscheidung' hat keinen benannten Verantwortlichen.
- ✅ `ERR_14_02` (high) — gefunden via evidence_fuzzy (Score 0.438): Die Maßnahme 'CAPA CAPA-VP-2026-031' in 'Entscheidung' hat keinen benannten Verantwortlichen. Die Zitate belegen, dass für jede der drei CAPA-Maßnahmen ein konkreter Verantwortlicher (Leitung Technik, Linienführer, QA-Schulung) und ein spezifischer Umsetzungstermin (25.07.2026, 04.07.2026, 10.07.2026) benannt ist. Die Termine sind chronologisch plausibel (interne Maßnahme vor der technischen Schnittstelle) und erfüllen die Anforderung an einen benannten Verantwortlichen und einen realisierbaren Terminplan. Die Maßnahme 'CAPA CAPA-VP-2026-031' in 'Entscheidung' hat keinen benannten Verantwortlichen. Die Maßnahme 'Linie gestoppt, Druckbild korrigiert, Freigabe des Neustarts durch IPC nach Erstmusterprüfung.' in 'Sofortmaßnahmen' hat keinen benannten Verantwortlichen.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 4 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_15

- ✅ `ERR_15_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt die vollständige Erfassung aller potenziell betroffenen Chargen, einschließlich Vorgänger- und Folgechargen, sowie die Begründung der Auswahl. Die vorliegenden Auszüge nennen zwar die Stabilitätscharge LEV-2025-S007 und die Marktcharge LEV-2025-M041, enthalten jedoch keine umfassende Chargenliste und keine explizite Begründung, warum genau diese Chargen ausgewählt wurden oder warum andere (z. B. Vorgänger/Folge) nicht betroffen sind. Da der geforderte Nachweis der Vollständigkeit und Begründung in den Auszügen fehlt, ist die Anforderung nicht erfüllt.
- ✅ `ERR_15_02` (medium) — gefunden via evidence_substring (Score 1.0): Die Maßnahme 'Prüfung der Blisterdichtigkeit an Rückstellmustern' in 'Maßnahmen' hat keinen benannten Verantwortlichen. Die Maßnahme 'Prüfung der Blisterdichtigkeit an Rückstellmustern' in 'Maßnahmen' hat keinen benannten Verantwortlichen.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_16

- ✅ `ERR_16_01` (critical) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Dokumente belegen zwar die Feststellung der Abweichung (erhöhter Rückstandswert an P3) und die Durchführung einer Nachreinigung, jedoch fehlt in den Auszügen eine explizite, dokumentierte Bewertung der Auswirkungen auf die Produktqualität und die Patientensicherheit. Insbesondere ist keine Auflistung potenziell betroffener Chargen (Chargenliste) oder eine Risikoanalyse zu finden, die die Sicherheit der Freigabe der Charge MET-2026-G014 und möglicher Vorchargen wissenschaftlich untermauert. Die bloße Feststellung, dass die Anlage freigegeben wurde, ersetzt nicht die geforderte dokumentierte Auswirkungsbewertung. Die Maßnahme 'Anlage gesperrt' in 'Sofortmaßnahmen' hat keinen benannten Verantwortlichen. Im CAPA-Plan fehlt der regulatorisch geforderte Effectiveness Check (Wirksamkeitsprüfung) für 3 Maßnahme(n), z. B. 'Anlage gesperrt'.
- ✅ `ERR_16_02` (high) — gefunden via evidence_substring (Score 1.0): Die Zitate belegen, dass die Anlage am 15.05.2026 zur Herstellung freigegeben wurde (Zitat 1), während die QA-Prüfung im Reinigungsverifizierungsbericht am 14.05.2026 noch leer war (Zitat 0). Der Abweichungsbericht (Zitat 2) bestätigt die Meldung am 14.05.2026. Es fehlt jedoch der Nachweis, dass die Bewertung der Abweichung DEV-CLN-2026-0057 und das Impact Assessment vor der Freigabe am 15.05.2026 abgeschlossen waren. Da die Freigabe vor dem Nachweis der abgeschlossenen Bewertung erfolgte, liegt ein Verstoß vor.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 7 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_17

- ✅ `ERR_17_01` (critical) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Dokumente belegen, dass das LIMS-System am 02.02.2026 für den GMP-Betrieb freigegeben wurde (Zitat 0), während die Qualifizierung (IQ/OQ) erst am 09.02.2026 abgeschlossen wurde (Zitat 1). Zudem wird in Zitat 2 bestätigt, dass ab dem 02.02.2026 Prüfaufträge im System bearbeitet wurden. Dies stellt einen Verstoß gegen die Anforderung dar, da die Freigabe (bzw. Inbetriebnahme für GMP-relevante Tätigkeiten) vor der abgeschlossenen Bewertung (Qualifizierung) erfolgte. Die QA-Prüfung am 10.02.2026 (Zitat 3) bestätigt den zeitlichen Ablauf, bei dem die Nutzung vor der vollständigen Qualifizierung begann.
- ✅ `ERR_17_02` (high) — gefunden via evidence_fuzzy (Score 0.549): Es liegt ein schwerwiegender Widerspruch in der zeitlichen Abfolge der Dokumente vor. Das Freigabeprotokoll (Dokument 3) besagt, dass das System am 02.02.2026 um 08:00 Uhr für den GMP-Betrieb freigegeben wurde. Der Qualifizierungsbericht (Dokument 2) dokumentiert jedoch, dass die IQ/OQ-Tests erst am 09.02.2026 abgeschlossen wurden und die Freigabeempfehlung erst zu diesem Datum erteilt wurde. Zudem bestätigt das Freigabeprotokoll, dass die Tests parallel im Produktivsystem liefen. Die Freigabe für den GMP-Betrieb vor Abschluss der obligatorischen Qualifizierung (OQ) stellt einen Verstoß gegen die GMP-Anforderungen an die Systemfreigabe dar. Die Datenkonsistenz (Record Counts) ist zwar gegeben, aber der Statuswiderspruch bezüglich der Freigabe ist ein klarer Verstoß.
- 🔁 3 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_18

- ✅ `ERR_18_01` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Out-of-Specification- (OOS) und Out-of-Trend-Ergebnisse vollständig untersucht und bewertet sein müssen, bevor eine Disposition erfolgt. In den vorliegenden Dokumenten wird im Lieferanten-CoA (Zitat 2) ein Wassergehalt von 0,62 % angegeben, der die Spezifikation von NMT 0,50 % überschreitet, obwohl die Bewertung fälschlicherweise als 'entspricht' markiert ist. Dies stellt ein OOS-Ergebnis dar. Im Wareneingangsprüfbericht (Zitat 1) wird behauptet, der CoA-Abgleich sei 'vollständig geprüft' und 'konform', was das OOS-Ergebnis ignoriert oder übergeht. Es gibt keine Dokumentation einer OOS-Untersuchung, keine Bewertung des Risikos und keine spezifische Dispositionsentscheidung, die auf der Untersuchung dieses Abweichungswerts basiert. Die Freigabe des Materials (im Chunk 2 erwähnt) erfolgte ohne den geforderten Nachweis einer abgeschlossenen OOS-Untersuchung. Daher liegt ein Verstoß vor, da der geforderte Nachweis (OOS-Untersuchungsbericht) fehlt, während ein OOS-Ergebnis vorliegt.
- ✅ `ERR_18_02` (high) — gefunden via evidence_substring (Score 1.0): Die vorliegenden Auszüge belegen zwar die Dispositionsentscheidung (Freigabe am 06.08.2026 und Sperrung am 09.08.2026) sowie die Begründung (Wareneingangsprüfung, Transportschaden), jedoch fehlt der explizite Nachweis der Verknüpfung mit den zugehörigen Batch Records. Die Anforderung verlangt zwingend die Verknüpfung der Disposition mit den Batch Records, was in den Zitat 0-3 nicht dokumentiert ist. Da die geforderte Evidenz (Batch Record) in den Auszügen fehlt, liegt ein Verstoß vor.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
