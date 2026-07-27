# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid` | Engine: `requirement`
- Zeitpunkt: 2026-07-27T09:28:44+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 36 von 41 versteckten Fehlern gefunden (88%)
- **In Prüfmappe sichtbar:** 36 von 41 versteckten Fehlern (88%)
- **Spezifität (Decoys):** 20 von 20 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 79 von 143 (55%) — 35 als Treffer gewertet, 44 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 64 von 143 (45%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 14.3 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 115 von 143 Findings mit verifiziertem Zitat (80%)

## Qualitätsmetriken

- Must-detect Recall: `0.878`
- Wiederholungen: `44` (Redundanzrate `0.557`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `16/3/17`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 93 | 144,729 | 25,175 | 169,904 |
| mistral | 40 | 150,350 | 65,853 | 216,203 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 12 | 2 | 8 | 2/4 | 2/4 | 0/2 | - |
| CASE_02 | completed | 0 | 16 | 2 | 10 | 4/4 | 4/4 | 0/2 | - |
| CASE_03 | completed_with_model_failures | 0 | 17 | 1 | 12 | 4/4 | 4/4 | 0/2 | - |
| CASE_04 | completed | 0 | 15 | 6 | 6 | 3/4 | 3/4 | 0/2 | - |
| CASE_05 | completed_with_model_failures | 0 | 9 | 4 | 3 | 2/4 | 2/4 | 0/2 | - |
| CASE_06 | completed | 0 | 15 | 7 | 5 | 3/3 | 3/3 | 0/2 | - |
| CASE_07 | completed | 0 | 6 | 0 | 2 | 4/4 | 4/4 | 0/2 | - |
| CASE_08 | completed | 0 | 18 | 8 | 5 | 5/5 | 5/5 | 0/2 | - |
| CASE_09 | completed | 0 | 17 | 5 | 8 | 4/4 | 4/4 | 0/2 | - |
| CASE_10 | completed | 0 | 18 | 9 | 5 | 5/5 | 5/5 | 0/2 | - |

## Modellausfälle

- **ProviderCallError** (2×): Provider retry deadline exceeded for anthropic
  - betroffen: CASE_03/entailment:7, CASE_05/entailment:4

### CASE_01

- ✅ `CASE01-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Unterlagen enthalten keine Chargenliste oder Begründung zur Auswahl der betroffenen Charge QRM-AVR-2603-017. Es gibt keinen Hinweis auf die Prüfung von Vorgänger- oder Folgechargen, obwohl dies für eine vollständige Batch-Impact-Bewertung erforderlich wäre. Der Auslöser für diese Pflicht ist die dokumentierte Abweichung in DEV-2603-041, die eine Bewertung aller potenziell betroffenen Chargen erfordert.
- ✅ `CASE01-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2603-041 bezieht sich auf den Siebeinsatz S-18, und es gibt keine Dokumentation, die bestätigt, dass die Validierung des Siebeinsatzes den aktuellen Prozess- oder Equipmentzustand abdeckt. Die CAPA-Maßnahme Nr. 1 sieht eine Sichtkontrolle vor, aber keinen Nachweis der aktuellen Validierung.
- ❌ `CASE01-E001` (medium) — übersehen: Unterschrift der Produktionsleitung im Deviation Report fehlt.
- ❌ `CASE01-E003` (high) — übersehen: Ausbeute 91.2 % liegt außerhalb des Sollbereichs 95.0 - 101.0 %, wurde aber nicht bewertet.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `CASE02-E001` (medium) — gefunden via evidence_substring (Score 1.0): Das Datum der Feststellung im Deviation Report (2026-04-31) ist nicht plausibel, da der April nur 30 Tage hat. Dies stellt einen Datenintegritätsbefund dar. Zudem fehlt eine zeitliche Plausibilitätsprüfung der Signaturen in den Dokumenten.
- ✅ `CASE02-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Unterlagen enthalten keine dokumentierte Bewertung der Auswirkung der Partikelüberschreitung auf die Produktqualität oder Patientensicherheit. Der Deviation Report (DEV-2604-058) erwähnt lediglich eine vorläufige Produktbewertung mit Sperrstatus der Charge, aber keine detaillierte Impact Assessment oder Chargenliste. Der Auslöser (Partikelüberschreitung in Klasse-A-Zone) ist jedoch belegt.
- ✅ `CASE02-E003` (high) — gefunden via evidence_substring (Score 1.0): Das Füllvolumen-IPC (Stichprobe 12) lag mit 4.82 mL außerhalb des Akzeptanzkriteriums (4.90–5.10 mL). Dies stellt eine Überschreitung der spezifizierten Grenzen dar, die als Abweichung zu bewerten ist, auch wenn die Abfüllung fortgesetzt wurde.
- ✅ `CASE02-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahmen (CAPA-2604-037) sind mit einem Qualitätsrisiko verknüpft, jedoch fehlt eine definierte und dokumentierte Wirksamkeitsprüfung. Die Unterlagen belegen, dass keine Wirksamkeitsprüfung vorgesehen ist, obwohl dies für administrative Maßnahmen mit Risikobezug erforderlich wäre.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `CASE03-E001` (high) — gefunden via evidence_substring (Score 1.0): Es gibt keinen Nachweis über einen durchgeführten Audit-Trail-Review für die Korrektur des Restproteinwerts (Swab B2). Der korrigierte Eintrag im Cleaning Record (CR-2603-014) enthält keine dokumentierte Begründung, Datum oder initiale für die Änderung, was auf fehlende Audit-Trail-Prüfung hindeutet.
- ✅ `CASE03-E002` (medium) — gefunden via evidence_substring (Score 1.0): Die Grundursache wird als 'kurzzeitige Unaufmerksamkeit bei Sprühposition B' angegeben, ohne dass technische Ursachen (z. B. Equipment, Kalibrierung, Alarme) dokumentiert ausgeschlossen wurden. Eine Befragung des Reinigungspersonals wurde nicht protokolliert.
- ✅ `CASE03-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Korrektur des Swab-Werts ohne dokumentierte Begründung, Datum oder vollständige Initialen deutet auf eine unzureichende Schulung oder Wirksamkeit der Dokumentationspraxis hin. Die CAPA-Maßnahmen (Sensibilisierung und Erinnerung) bestätigen indirekt, dass kein wirksames Training vorlag, da sonst keine Nachschulung erforderlich wäre.
- ✅ `CASE03-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Quality Approval Note verweist auf Anhang 1 (Reinigungsprotokoll), Anhang 2 (Laborfreigabe) und Anhang 3 (Restproteinbewertung). Diese Anhänge sind jedoch in den bereitgestellten Chunks nicht enthalten, sodass die Vollständigkeit nicht überprüft werden kann.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `CASE04-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen im Batch Manufacturing Record (BMR) sind nicht vollständig und konsistent. Die Raumtemperatur im Kompressionsraum KR-2 wurde um 10:20 Uhr mit 31,2 °C dokumentiert (Grenzwertüberschreitung), während der Deviation Report für denselben Zeitraum eine maximale Raumtemperatur von 24,8 °C angibt. Diese Diskrepanz deutet auf fehlende oder nachträglich veränderte Originaldaten hin, ohne dass dies begründet wird.
- ✅ `CASE04-E003` (medium) — gefunden via evidence_fuzzy (Score 0.422): Die Charge QRM-SEL-2604-112 wurde vor Abschluss der technischen Sichtprüfung (Maßnahme 2 im CAPA-Plan) freigegeben. Der Quality Approval Note (QA-N-2604-083) empfiehlt die Fortsetzung in die Beschichtung, obwohl die technische Sichtprüfung als 'offen' markiert ist. Dies stellt einen Verstoß gegen die Anforderung dar, da die Freigabe vor Abschluss aller erforderlichen Bewertungen erfolgte.
- ✅ `CASE04-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Unterlagen enthalten keine Auflistung oder Bewertung von Vorgänger- oder Folgechargen der betroffenen Charge QRM-SEL-2604-112. Der Deviation Report (DEV-2604-071) und der CAPA-Plan (CAPA-2604-049) beziehen sich ausschließlich auf die Charge QRM-SEL-2604-112, ohne weitere Chargen zu erwähnen. Dies begründet den Verstoß, da die Anforderung eine vollständige Erfassung aller potenziell betroffenen Chargen fordert.
- ❌ `CASE04-E002` (medium) — übersehen: Gleiche Uhrzeit 10:30 dokumentiert widersprüchliche Ereignisse.
- 🔁 6 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 6 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `CASE05-E001` (high) — gefunden via evidence_substring (Score 1.0): Die interne Spezifikation (SPEC-RM-SX14 Rev.07) verlangt für den Gehalt der Hauptkomponente einen Akzeptanzbereich von 98,0 - 102,0 % (chunk_12f036f29213482aa46e45c8e950d647_p1). Das Lieferanten-CoA und das interne QC-Laborergebnis weisen jedoch einen Gehalt von 96,8 % bzw. 96,9 % aus (chunk_fe4dd9644dce4f1ab693dfbc50378726_p1 und chunk_27e07937774740e78d582b0a134128b0_p1), was unterhalb der internen Spezifikation liegt. Obwohl das Material als 'bestanden' bewertet und zur Produktion freigegeben wurde (chunk_27e07937774740e78d582b0a134128b0_p1), verstößt dies gegen die Anforderung, dass Mess- und Prüfergebnisse gegen die gültige interne Spezifikation bewertet werden müssen. Die Abweichung wurde zwar im Material Deviation Report (DEV-2604-063) dokumentiert, aber die Verletzung der internen Akzeptanzkriterien bleibt bestehen.
- ✅ `CASE05-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Unterlagen belegen, dass die Charge RM-SX14-2604-02 für zwei Nivoril-Ansätze (QRM-NIV-2604-031 und QRM-NIV-2604-033) verwendet wurde. Allerdings wird im Material Deviation Report (DEV-2604-063) und in der Quality Approval Note (QA-N-2604-094) nur die Bewertung der Charge QRM-NIV-2604-033 dokumentiert. Die bereits freigegebene Charge QRM-NIV-2604-031 wird nicht in die Impact-Bewertung einbezogen, obwohl sie potenziell betroffen ist. Dies verstößt gegen die Anforderung, alle potenziell betroffenen Chargen zu erfassen.
- ❌ `CASE05-E002` (medium) — übersehen: Abweichende Initialen QC-KM vs. QC-LT bei manueller Integration ohne Erklärung.
- ❌ `CASE05-E004` (medium) — übersehen: Audit-Trail-Review ist behauptet, aber bei manueller Integration nicht nachgewiesen/referenziert.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 3 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `CASE06-E001` (high) — gefunden via evidence_substring (Score 1.0): Der Differenzdruck während der Sterilfiltration überschritt den validierten maximalen Grenzwert von ≤3,2 bar (Peak 3,6 bar). Dies stellt eine Abweichung von den spezifizierten Prozessparametern dar, auch wenn der Post-use Integrity Test bestanden wurde.
- ✅ `CASE06-E002` (high) — gefunden via evidence_substring (Score 1.0): Der Pumpenwechsel von Typ LFP-120 auf LFP-200 wurde ohne dokumentierte Change-Control-Nummer oder technische Vergleichsbewertung durchgeführt. Die Validierungsnotiz (VAL-N-2603-018) fordert für Änderungen an Pumpentyp oder Pulsationscharakteristik eine Change-Control-Referenz und technische Bewertung: "Änderungen an Pumpentyp oder Pulsationscharakteristik erfordern Change Control und technische Vergleichsbewertung." (chunk_2c515b37f86244d583d16cc76bce3969_p1). Die Maintenance Note bestätigt das Fehlen einer Change-Control-Nummer: "Change-Control-Nummer im Wartungsauftrag: nicht eingetragen." (chunk_e84fe12d3a994df7b4fc519a52a4467c_p1).
- ✅ `CASE06-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2604-077 wurde nicht durch eine nachvollziehbare Risikobewertung mit belastbaren physikalisch-chemischen oder labortechnischen Daten eingestuft. Der Deviation Report nennt lediglich eine mögliche Root Cause (Pumpenpulsation) und eine visuelle Unauffälligkeit des Produkts, was keine ausreichende Risikobewertung darstellt. Eine Einstufung als geringfügig ohne entsprechende Daten ist unzulässig.
- 🔁 7 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `CASE07-E001` (high) — gefunden via evidence_substring (Score 1.0): Die Grundursache der Abweichung DEV-2604-081 wird nicht durch eine angemessene Untersuchung belegt. Der Deviation Report (Chunk: chunk_5c683dd659c643aa8ecbf9b1437d72c2_p1) beschreibt lediglich Sofortmaßnahmen und eine erste Bewertung, ohne technische Ursachen (z. B. Equipment, Kalibrierung, Alarme) dokumentiert auszuschließen. Eine Zuschreibung als 'Bedienerfehler' ist nicht ausreichend belegt.
- ✅ `CASE07-E002` (medium) — gefunden via evidence_fuzzy (Score 0.505): Die Anforderung verlangt, dass CAPA-Maßnahmen mit einem Qualitätsrisiko nur mit definierter und dokumentierter Wirksamkeitsprüfung abgeschlossen werden dürfen. Im CAPA-Plan (document_03_capa_plan.md) ist zwar eine Wirksamkeitsprüfung ('Review der nächsten fünf Aufträge auf PK-3 auf Etikettenfund') vorgesehen, jedoch fehlt der Nachweis, dass diese Wirksamkeitsprüfung tatsächlich durchgeführt und dokumentiert wurde. Der Status der Maßnahme Nr. 2 ('Checkliste Line Clearance um Sichtprüfung Abfallbehälter ergänzen') ist zudem als 'offen' gekennzeichnet, was bedeutet, dass die CAPA noch nicht vollständig abgeschlossen ist.
- ✅ `CASE07-E003` (medium) — gefunden via evidence_substring (Score 1.0): Die Einstufung der Abweichung DEV-2604-081 als 'erstmaliges Ereignis' (Chunk: chunk_5c683dd659c643aa8ecbf9b1437d72c2_p1) erfolgt ohne nachvollziehbare Risikobewertung oder belastbare physikalisch-chemische bzw. labortechnische Daten. Die QA-Note (Chunk: chunk_b13fee49b76d4324b78ecf2474ba1e8b_p1) erwähnt zwar ein ähnliches Ereignis (DEV-2601-019), liefert aber keine detaillierte Risikobewertung für den aktuellen Vorfall. Die Pflicht zur Risikobewertung ist durch den dokumentierten Vorfall belegt.
- ✅ `CASE07-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2604-081 beschreibt den Fund loser Etiketten im Abfallbehälter neben der Linie. Eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit fehlt. Insbesondere wird keine Chargenliste oder detaillierte Impact-Assessment-Dokumentation zitiert, obwohl der Vorfall während der Verpackung der Charge QRM-LUM-2604-080 stattfand. Der Auslöser für die Pflicht zur Impact-Assessment ist belegt durch den Fund der Etiketten (Chunk: chunk_5c683dd659c643aa8ecbf9b1437d72c2_p1).
- ℹ️ 2 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `CASE08-E001` (critical) — gefunden via evidence_substring (Score 1.0): Der Auto-Endpunkt Algorithmus AE-2 wurde für die Charge QRM-MER-2604-052 genutzt, obwohl die Implementierungsfreigabe zum Zeitpunkt der Nutzung noch ausstand. Die Change Control (CC-2604-011) bestätigt, dass die vorläufige Nutzung im Routinebetrieb nicht freigegeben war. Eine dokumentierte Auswirkungsbewertung oder Validierungsabdeckung fehlt.
- ✅ `CASE08-E002` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass Out-of-Specification- (OOS) oder Out-of-Trend- (OOT) Ergebnisse vollständig untersucht und bewertet sein müssen, bevor eine Chargen- oder Marktware-Disposition erfolgt. Die Charge QRM-MER-2604-052 weist einen LOD-Wert von 2,8 % auf, der über der Spezifikation von NMT 2,5 % liegt. Dieser OOS-Wert wurde zwar im Batch Record akzeptiert, jedoch fehlt eine dokumentierte OOS-Untersuchung oder eine vollständige Bewertung der Ursache und Auswirkungen vor der Freigabeentscheidung. Die Quality Approval Note empfiehlt die Charge zur Freigabe, ohne dass eine abgeschlossene OOS-Untersuchung vorliegt.
- ✅ `CASE08-E003` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit, einschließlich aller potenziell betroffenen Chargen. Zwar gibt es eine Stabilitätsbewertung (STAB-2604-027) für die Charge QRM-MER-2604-052, jedoch fehlt eine explizite Bewertung der potenziell betroffenen vorherigen Charge QRM-MER-2604-046, die im gleichen Zeitraum auf der Anlage D-17 getrocknet wurde. Der Deviation Report (DEV-2604-095) erwähnt zwar die vorherige Charge, aber eine dokumentierte Impact-Bewertung für diese Charge ist nicht vorhanden. Zudem ist der Status der Deviation als 'offen' markiert, was darauf hindeutet, dass die Bewertung noch nicht abgeschlossen ist.
- ✅ `CASE08-E004` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-MER-2604-052 wurde freigegeben, obwohl die Abweichungsbewertung (DEV-2604-095) zum Zeitpunkt der Freigabe noch nicht abgeschlossen war. Der Deviation Report erwähnt, dass der Produktimpact noch in Bearbeitung ist, und die Quality Approval Note bestätigt, dass DEV-2604-095 bis zum Abschluss der Sensorbewertung offen bleibt.
- ✅ `CASE08-E005` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Wirksamkeitsprüfung ist nicht ausreichend dokumentiert. Zwar wird eine Wirksamkeitsprüfung mit drei Folgechargen bis zum 2026-05-05 erwähnt, jedoch fehlt der Nachweis, dass diese tatsächlich durchgeführt wurde. Zudem ist die nächste geplante Charge erst für den 2026-07-14 terminiert, was die Durchführung der Wirksamkeitsprüfung bis zum genannten Termin infrage stellt.
- 🔁 8 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `CASE09-E001` (high) — gefunden via evidence_fuzzy (Score 0.45): Die Reinigung der Anlage FB-22/TL-22 wurde am 2026-03-12 durchgeführt, und die nächste geplante Nutzung war für den 2026-03-13 vorgesehen. Es gibt jedoch keine dokumentierte abgeschlossene Abweichungsbewertung oder QA-Freigabe vor der nächsten Nutzung. Die RCA/CAPA (RCA-CAPA-2603-057) wurde erst am 2026-03-13 erstellt, also *nach* der nächsten geplanten Nutzung.
- ✅ `CASE09-E002` (high) — gefunden via evidence_substring (Score 1.0): Es besteht ein Widerspruch zwischen der validierten Detergentkonzentration (1,0 % ±0,1 % laut Cleaning Validation Note) und der tatsächlich verwendeten Konzentration (0,5 % laut Cleaning Record). Dies wurde im RCA/CAPA-Report als nicht change-control-relevant bewertet, obwohl die Cleaning Validation Note eine Änderung der Detergentkonzentration als change-control-pflichtig einstuft.
- ✅ `CASE09-E003` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme Nr. 1 (Retraining OP-44) sieht als Wirksamkeitsprüfung lediglich den "Review der nächsten Reinigung" vor. Dies ist keine definierte und dokumentierte Wirksamkeitsprüfung (Effectiveness Check) im Sinne von GMP-Anforderungen, da kein klares Kriterium oder Verfahren für die Überprüfung der Wirksamkeit festgelegt ist.
- ✅ `CASE09-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Abweichung (Sprühverteilung und verspätete Dokumentation) wurde im RCA/CAPA-Bericht nicht durch eine nachvollziehbare Risikobewertung eingestuft. Es fehlen belastbare physikalisch-chemische oder labortechnische Daten zur Begründung der Einstufung. Die Aussage, dass alle analytischen Endwerte innerhalb der Grenzen lagen, ersetzt keine formale Risikobewertung.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `CASE10-E001` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ZEP-2604-014 wurde zur Freigabe empfohlen, obwohl die Abweichungsbewertung (DEV-2604-074) und das APS-Bridging für den Change Control (CC-2604-019) nicht abgeschlossen waren. Die EM-Abweichung DEV-2604-074 blieb offen, und die QA-Freigabe für die Implementierung des Change Control stand aus.
- ✅ `CASE10-E002` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge QRM-ZEP-2604-014 wurde zur Freigabe empfohlen, obwohl die Abweichungsbewertung (DEV-2604-074) und das APS-Bridging für den Change Control (CC-2604-019) nicht abgeschlossen waren. Die EM-Abweichung DEV-2604-074 blieb offen, und die QA-Freigabe für die Implementierung des Change Control stand aus.
- ✅ `CASE10-E003` (high) — gefunden via evidence_substring (Score 1.0): Die Grundursache der EM-Abweichung DEV-2604-074 (2 KBE im Stopfentrichter SB-9) ist nicht durch eine angemessene Untersuchung belegt. Es gibt keine Dokumentation, die technische Ursachen (z. B. Equipment, Kalibrierung) ausschließt. Der aseptische Eingriff zur Entfernung eines verklemmten Stopfens (Chunk chunk_ffb9bbc98c414d22b8a3b57298c113ef_p1) könnte eine mögliche Ursache sein, wurde aber nicht als solche untersucht.
- ✅ `CASE10-E004` (medium) — gefunden via evidence_substring (Score 1.0): Die Aufzeichnungen zur EM-Abweichung DEV-2604-074 und zum aseptischen Eingriff sind nicht vollständig im Sinne von ALCOA+. Es fehlt eine lückenlose Dokumentation der Grundursachenuntersuchung, der Risikobewertung und der Autorisierung des manuellen Eingriffs. Die QA-Note (Chunk chunk_f6e25d4165354390bad4b92ec706d5af_p1) bestätigt lediglich die Freigabeempfehlung, ohne die Vollständigkeit der Originalaufzeichnungen zu belegen.
- ✅ `CASE10-E005` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2604-074 (EM-Abweichung) ist belegt (Chunk chunk_ebdd3df34e754a3ea81cddc76758b279_p1), jedoch fehlt eine dokumentierte Bewertung der Auswirkung auf Produktqualität und Patientensicherheit sowie eine Chargenliste der potenziell betroffenen Chargen. Die QA-Note (Chunk chunk_f6e25d4165354390bad4b92ec706d5af_p1) bestätigt lediglich die Einstufung als 'low' ohne detaillierte Impact-Assessment-Dokumentation.
- 🔁 9 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
