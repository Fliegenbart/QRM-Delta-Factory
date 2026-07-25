# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-07-25T19:40:32+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 25 von 25 versteckten Fehlern gefunden (100%)
- **In Prüfmappe sichtbar:** 22 von 25 versteckten Fehlern (88%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 133 von 244 (55%) — 20 als Treffer gewertet, 113 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 111 von 244 (45%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 24.4 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 216 von 244 Findings mit verifiziertem Zitat (88%)

## Qualitätsmetriken

- Must-detect Recall: `1.0`
- Wiederholungen: `113` (Redundanzrate `0.8496`)
- Unsupported Findings: `0.9795`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `11/5/9`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 10 | 81,847 | 19,349 | 101,196 |
| mistral | 70 | 1,082,109 | 222,694 | 1,304,803 |
| openai | 10 | 153,166 | 27,778 | 180,944 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 18 | 28 | 16 | 10 | 2/2 | 2/2 | 0/1 | human_review_required |
| CASE_02 | completed | 4 | 6 | 0 | 5 | 2/2 | 1/2 | 0/1 | human_review_required |
| CASE_03 | completed | 7 | 28 | 11 | 15 | 2/2 | 2/2 | 0/2 | human_review_required |
| CASE_04 | needs_human_review | 7 | 27 | 22 | 3 | 3/3 | 3/3 | 0/1 | human_review_required |
| CASE_05 | needs_human_review | 2 | 15 | 8 | 5 | 3/3 | 2/3 | 0/1 | human_review_required |
| CASE_06 | needs_human_review | 3 | 27 | 12 | 14 | 2/2 | 2/2 | 0/1 | human_review_required |
| CASE_07 | needs_human_review | 6 | 27 | 0 | 25 | 2/2 | 1/2 | 0/1 | human_review_required |
| CASE_08 | completed | 14 | 31 | 16 | 12 | 3/3 | 3/3 | 0/1 | human_review_required |
| CASE_09 | needs_human_review | 5 | 27 | 16 | 8 | 3/3 | 3/3 | 0/1 | human_review_required |
| CASE_10 | completed | 5 | 28 | 12 | 14 | 3/3 | 3/3 | 0/1 | human_review_required |

## Modellausfälle

- **ProviderCallError** (6×): anthropic provider call failed
  - betroffen: CASE_01/RedTeamCriticAnthropic, CASE_04/RedTeamCriticAnthropic, CASE_05/RedTeamCriticAnthropic, CASE_06/RedTeamCriticAnthropic, CASE_07/RedTeamCriticAnthropic, CASE_09/RedTeamCriticAnthropic

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Signatur im Abweichungsbericht (DEV-2026-891) ist mit dem Datum 14.12.2026 datiert, was in der Zukunft liegt und die Plausibilität der Signaturdaten infrage stellt. Dies stellt ein Datenintegritätsrisiko dar.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2026-891 wurde als 'Minor' eingestuft, ohne dass eine belastbare physikalisch-chemische oder labortechnische Bewertung der Auswirkung auf die Produktqualität vorliegt. Die visuelle Homogenität allein ist kein ausreichender Nachweis für die Einstufung.
- 🔁 16 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Spezifikationsverletzung/Yield-Unterschreitung: Ausbeute berechnet sich außerhalb der zulässigen Spezifikationsgrenzen; Ausbeute 96.47% liegt außerhalb des spezifizierten Bereichs 98% bis 101%. Yield-Unterschreitung wird fälschlicherweise als Freigabe deklariert; OOS/Abweichungsuntersuchung erforderlich.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_substring (Score 1.0): Spezifikationsverletzung/Yield-Unterschreitung: Ausbeute berechnet sich außerhalb der zulässigen Spezifikationsgrenzen; Ausbeute 96.47% liegt außerhalb des spezifizierten Bereichs 98% bis 101%. Yield-Unterschreitung wird fälschlicherweise als Freigabe deklariert; OOS/Abweichungsuntersuchung erforderlich.
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Es gibt keine dokumentierte Evidenz für einen durchgeführten Audit-Trail-Review zu den elektronischen Daten des Partikelzählers während der Abfüllung der Charge LPO-2026-11A. Der Vorfall DEV-QS-2026-014 betrifft GxP-relevante Daten, für die ein Audit-Trail-Review gemäß EU GMP Annex 11, Abschnitt 9, erforderlich ist.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme CAPA-2026-014 verweist auf die SOP-QS-REIN-001, Version 2.0, jedoch fehlt eine dokumentierte Bewertung, ob die betroffene Charge LPO-2026-11A von der aktualisierten Reinigungsvalidierung abgedeckt ist. Eine Freigabe der Charge ohne Validierungsnachweis ist nicht zulässig.
- 🔁 11 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 15 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Die Charge PAR-2026-H102 wurde freigegeben, obwohl die Abweichungsbewertung (DEV-P-2026-092) und das Impact Assessment nicht abgeschlossen sind. Dies verstößt gegen die Anforderung, dass keine Freigabe vor abgeschlossener Bewertung erfolgen darf.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme CAPA-DEV-092 verweist auf die Abweichung DEV-P-2026-092 und plant ein Re-Training für den Operator J.K. bis zum 15.06.2026. Die QS-Chargenbewertung gibt jedoch an, dass die Charge PAR-2026-H102 trotz der Abweichung DEV-P-2026-092 als qualitätskonform freigegeben wurde, ohne die Durchführung oder Wirksamkeit des Re-Trainings zu erwähnen oder zu belegen.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme CAPA-DEV-092 verweist auf die Abweichung DEV-P-2026-092 und plant ein Re-Training für den Operator J.K. bis zum 15.06.2026. Die QS-Chargenbewertung gibt jedoch an, dass die Charge PAR-2026-H102 trotz der Abweichung DEV-P-2026-092 als qualitätskonform freigegeben wurde, ohne die Durchführung oder Wirksamkeit des Re-Trainings zu erwähnen oder zu belegen.
- 🔁 22 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 3 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Validierungsabdeckung des Autoklaven AT-442 für das Programm 'Standard-Zubehör-121' ist unklar, da die Validierungsnote VAL-NOTE-AT-442 zwar im Januar 2026 freigegeben wurde, jedoch keine explizite Evidenz vorliegt, dass die spezifischen Beladungsmuster und maximalen Gesamtgewichte für Glaswaren (Anhang 4) auf die aktuelle Charge OXA-2026-088 anwendbar sind.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Im Autoklavierungs-Logbuch wird der Mitarbeiter P.M. (Personalnummer: PNN-8812) als ausführender Mitarbeiter genannt, während im Reinraum-Sicherungsbericht derselbe Mitarbeiter unter den Initialen A.S. geführt wird. Es fehlt ein dokumentierter Audit-Trail-Review, der diese Diskrepanz aufklärt und sicherstellt, dass keine sicherheits- oder qualitätsrelevanten Einträge ausgeschlossen wurden (req_di_audit_trail_review).
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Im Autoklavierungs-Logbuch wird der Mitarbeiter P.M. (Personalnummer: PNN-8812) als ausführender Mitarbeiter genannt, während im Reinraum-Sicherungsbericht derselbe Mitarbeiter unter den Initialen A.S. geführt wird. Es fehlt ein dokumentierter Audit-Trail-Review, der diese Diskrepanz aufklärt und sicherstellt, dass keine sicherheits- oder qualitätsrelevanten Einträge ausgeschlossen wurden (req_di_audit_trail_review).
- 🔁 8 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 5 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Die interne Spezifikation für Amoxicillin Trihydrat (Wassergehalt 11,5%–12,8%) wurde mit einem gemessenen Wert von 13,2% verletzt, obwohl das Analysenzertifikat des Lieferanten (CS-AMX-9982) Konformität ausweist. Die Freigabe der Charge AMO-SUP-2026-01 erfolgte ohne dokumentierte Bewertung der Abweichung von der internen Spezifikation.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_substring (Score 1.0): Die interne Spezifikation für Amoxicillin Trihydrat (Wassergehalt 11,5%–12,8%) wurde mit einem gemessenen Wert von 13,2% verletzt, obwohl das Analysenzertifikat des Lieferanten (CS-AMX-9982) Konformität ausweist. Die Freigabe der Charge AMO-SUP-2026-01 erfolgte ohne dokumentierte Bewertung der Abweichung von der internen Spezifikation.
- 🔁 12 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): Spezifikationsverletzung/Yield-Unterschreitung: Ausbeute berechnet sich außerhalb der zulässigen Spezifikationsgrenzen; Ausbeute 92.4% liegt außerhalb des spezifizierten Bereichs 95% bis 102%. Yield-Unterschreitung wird fälschlicherweise als Pass deklariert; OOS/Abweichungsuntersuchung erforderlich.
- ✅ `ERR_07_02` (medium) — gefunden via evidence_fuzzy (Score 0.43): Die Abweichung DEV-MET-09 wurde als 'Minor' eingestuft, ohne dass eine nachvollziehbare Risikobewertung oder stützende Labordaten zur Begründung der Einstufung vorliegen. Dies widerspricht den Anforderungen an eine belegte Schweregradeinstufung.
- ℹ️ 25 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Sterilitätsrisikobewertung für den Werkzeugbruch an Station 12 (DEV-IBU-2026-112) bei Charge IBU-2026-P03 ist nicht explizit durch eine Reinigungsvalidierung oder Kontaminationskontrollstrategie belegt. Die Aussage, dass es sich um ein isoliertes Einzelereignis handelt, reicht ohne dokumentierte Sterilitätsbewertung nicht aus.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): Die Aussage im Abweichungsbericht (DEV-IBU-2026-112), dass 'ein Einfluss auf andere Chargen oder vorangegangene Produktionsschritte absolut ausgeschlossen' ist, steht im Widerspruch zur Anforderung einer vollständigen Batch-Impact-Bewertung gemäß EU GMP Kapitel 5. Die betroffenen Chargen (Vorgänger- und Folgechargen) wurden nicht explizit bewertet oder dokumentiert.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme (CAPA-112-IBU) zur Nachrüstung eines Inline-Metalldetektors ist mit einer Deadline am 11.05.2026 terminiert, ohne dass eine dokumentierte Wirksamkeitsprüfung (Effectiveness Check) oder Validierungsabdeckung des aktuellen Zustands vorliegt.
- 🔁 16 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 12 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Der manuelle Eingriff in den pH-Regelkreis am 05.05.2026 (Bioreaktor BIO-10, Charge CEF-BIOR-2026-77) wurde ohne dokumentierte Autorisierung oder Begruendung im Audit Trail durchgeführt, was gegen die Anforderungen an Zugriffskontrolle und manuelle Overrides verstößt.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Die Root Cause für die pH-Wert-Drift im Bioreaktor BIO-10 (DEV-CEF-77) wurde als 'technisch nicht final aufgeklärt' dokumentiert, ohne dass technische Ursachen (z. B. Equipment, Kalibrierung, Alarme) systematisch ausgeschlossen wurden.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Freigabe für die betroffene Charge CEF-BIOR-2026-77 ist nicht dokumentiert, obwohl die Aufarbeitung fortgesetzt wurde. Das Feld für die Leitung Qualitätskontrolle im Change-Control-Antrag ist leer.
- 🔁 16 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 8 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge INS-GLA-2025-05 weist eine unbekannte Verunreinigung von 0,32% auf, die die Spezifikationsgrenze von maximal 0,20% überschreitet. Die OOS-Untersuchung ist nicht abgeschlossen, und die Dispositionsentscheidung erfolgte ohne vollständige Bewertung der Auswirkung auf Produktqualität und Patientensicherheit.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Die betroffene Charge INS-GLA-2025-05 wird in den Dokumenten referenziert, jedoch fehlt eine explizite und dokumentierte Dispositionsentscheidung mit Verknüpfung zum Batch Record. Die QA-Freigabe ist nicht eindeutig belegt.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die betroffene Charge INS-GLA-2025-05 wird in den Dokumenten referenziert, jedoch fehlt eine explizite und dokumentierte Dispositionsentscheidung mit Verknüpfung zum Batch Record. Die QA-Freigabe ist nicht eindeutig belegt.
- 🔁 12 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
