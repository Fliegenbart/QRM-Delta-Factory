# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-07-25T17:08:18+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 25 von 25 versteckten Fehlern gefunden (100%)
- **In Prüfmappe sichtbar:** 23 von 25 versteckten Fehlern (92%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Trefferquote der Ausgabe:** 25 von 263 Findings zeigen auf einen echten Fehler (10%)
- **Findings pro Fall:** 26.3 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 228 von 263 Findings mit verifiziertem Zitat (87%)

## Qualitätsmetriken

- Must-detect Recall: `10.0`
- Duplikate: `137`
- Unsupported Findings: `9.7678`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `8/6/11`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 10 | 123,135 | 33,692 | 156,827 |
| mistral | 70 | 1,081,190 | 222,883 | 1,304,073 |
| openai | 10 | 153,022 | 29,236 | 182,258 |

## Fälle

| Fall | Status | Claims | Findings | ohne Fehlerbezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|
| CASE_01 | needs_human_review | 18 | 27 | 25 | 2/2 | 2/2 | 0/1 | human_review_required |
| CASE_02 | needs_human_review | 4 | 16 | 14 | 2/2 | 1/2 | 0/1 | human_review_required |
| CASE_03 | completed | 7 | 27 | 25 | 2/2 | 2/2 | 0/2 | human_review_required |
| CASE_04 | completed | 7 | 36 | 33 | 3/3 | 3/3 | 0/1 | human_review_required |
| CASE_05 | completed | 2 | 15 | 13 | 3/3 | 3/3 | 0/1 | human_review_required |
| CASE_06 | needs_human_review | 3 | 18 | 16 | 2/2 | 2/2 | 0/1 | human_review_required |
| CASE_07 | completed | 6 | 32 | 30 | 2/2 | 1/2 | 0/1 | human_review_required |
| CASE_08 | completed | 14 | 38 | 35 | 3/3 | 3/3 | 0/1 | human_review_required |
| CASE_09 | needs_human_review | 5 | 29 | 26 | 3/3 | 3/3 | 0/1 | human_review_required |
| CASE_10 | completed | 5 | 25 | 22 | 3/3 | 3/3 | 0/1 | human_review_required |

## Modellausfälle

- **ProviderCallError** (3×): anthropic provider call failed
  - betroffen: CASE_01/RedTeamCriticAnthropic, CASE_02/RedTeamCriticAnthropic, CASE_09/RedTeamCriticAnthropic
- **ProviderStructuredOutputError** (1×): findings must be a valid list of objects
  - betroffen: CASE_06/RedTeamCriticAnthropic

### CASE_01

- ✅ `ERR_01_01` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Signatur im Abweichungsbericht DEV-2026-891 datiert auf den 14.12.2026, was in der Zukunft liegt und damit gegen die Plausibilität von Signaturdaten gemäß 21 CFR Part 11 11.50 verstößt. Dies stellt ein Datenintegritätsrisiko dar.
- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-2026-891 wurde als 'Minor' eingestuft, ohne dass belastbare physikalisch-chemische oder labortechnische Daten zur Begründung der Einstufung vorliegen. Die visuelle Homogenität allein ist kein ausreichender Nachweis für die Produktqualität.
- ℹ️ 25 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Die Charge CPH-2026-991 wurde freigegeben, obwohl die Ausbeute von 96,47% auf 98,1% korrigiert wurde, ohne dass eine dokumentierte Begründung für die Korrektur oder eine Bewertung der Auswirkung auf die Produktqualität vorliegt. Dies stellt ein Datenintegritätsrisiko dar.
- ✅ `ERR_02_02` (medium) — gefunden via evidence_substring (Score 1.0): Spezifikationsverletzung/Yield-Unterschreitung: Ausbeute berechnet sich außerhalb der zulässigen Spezifikationsgrenzen; Ausbeute 96.47% liegt außerhalb des spezifizierten Bereichs 98% bis 101%. Yield-Unterschreitung wird fälschlicherweise als Freigabe deklariert; OOS/Abweichungsuntersuchung erforderlich.
- ℹ️ 14 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_03

- ✅ `ERR_03_01` (high) — gefunden via evidence_substring (Score 1.0): Widersprüchliche zeitliche Angaben im Deviation Report: Der Peak-Zeitstempel (14:15 Uhr) liegt vor dem Eintritt des Mitarbeiters in Raum R-202 (14:35 Uhr), was auf eine mögliche Fehlfunktion des Partikelzählers oder eine falsche Dokumentation hindeutet.
- ✅ `ERR_03_02` (medium) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme CAPA-2026-014 zur Anpassung des Reinigungsverfahrens für Raum R-202 enthält keinen dokumentierten Effectiveness Check zur Überprüfung der Wirksamkeit der Maßnahme.
- ℹ️ 25 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Die Charge PAR-2026-H102 wird freigegeben, obwohl die Abweichungsbewertung (DEV-P-2026-092) und das Impact Assessment nicht abgeschlossen sind. Die Freigabe erfolgte vor Abschluss der QA-Disposition, was gegen die Anforderung verstößt, dass keine Freigabe vor abgeschlossener Bewertung erfolgen darf.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-P-2026-092 wird als 'Bedienerfehler' klassifiziert, ohne dass technische Ursachen (z. B. Equipment, Kalibrierung, Alarme) dokumentiert ausgeschlossen wurden. Dies verstößt gegen die Anforderung, dass eine Zuschreibung als 'Bedienerfehler' nur zulässig ist, wenn technische Ursachen ausgeschlossen sind.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge PAR-2026-H102 wird in der QS Chargenbewertung als qualitätskonform freigegeben, obwohl die Dispositionsentscheidung nicht explizit mit dem Batch Record verknüpft oder begründet ist. Es fehlt eine nachvollziehbare Verknüpfung zwischen der Freigabeentscheidung und den Batch-Record-Daten.
- ℹ️ 33 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_05

- ✅ `ERR_05_01` (medium) — gefunden via evidence_substring (Score 1.0): Die Validierungsabdeckung für den Autoklav AT-442 ist nicht eindeutig auf die aktuelle Charge OXA-2026-088 übertragbar, da die Validierungsnote VAL-NOTE-AT-442 zwar die Freigabe für das Programm 'Standard-Zubehör-121' bestätigt, jedoch keine explizite Aussage zur Beladungskonfiguration oder zum spezifischen Produktkontaktmaterial der Charge OXA-2026-088 enthält.
- ✅ `ERR_05_02` (high) — gefunden via evidence_substring (Score 1.0): Die Sterilitätsassurance für den Autoklavierungsprozess der Charge OXA-2026-088 ist nicht ausreichend dokumentiert, da der Mitarbeiter P.M. (PNN-8812) laut Autoklavierungs-Logbuch die Sterilgüter um 09:00 Uhr entnommen hat, jedoch erst um 08:45 Uhr den Vorbereitungsraum betrat. Dies deutet auf eine mögliche Diskrepanz in der zeitlichen Abfolge hin, die die Sterilität der Charge gefährden könnte.
- ✅ `ERR_05_03` (medium) — gefunden via evidence_substring (Score 1.0): Die Sterilitätsassurance für den Autoklavierungsprozess der Charge OXA-2026-088 ist nicht ausreichend dokumentiert, da der Mitarbeiter P.M. (PNN-8812) laut Autoklavierungs-Logbuch die Sterilgüter um 09:00 Uhr entnommen hat, jedoch erst um 08:45 Uhr den Vorbereitungsraum betrat. Dies deutet auf eine mögliche Diskrepanz in der zeitlichen Abfolge hin, die die Sterilität der Charge gefährden könnte.
- ℹ️ 13 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_substring (Score 1.0): Spezifikationsverletzung: Wassergehalt 13.2% verletzt das Akzeptanzkriterium der internen Spezifikation; das Lieferanten-Zertifikat beziehungsweise Analysenzertifikat wird trotzdem als konform/Freigabe behandelt. Wirkstofffreigabe durch QA trotz ungelöster und aktiver Laborabweichung.
- ✅ `ERR_06_02` (critical) — gefunden via evidence_substring (Score 1.0): Die Freigabeentscheidung für den Rohstoff CS-AMX-9982 (QA-REL-AMO-01) erfolgte am 18.05.2026, obwohl die Abweichung LAB-DEV-2026-031 (Wassergehalt außerhalb der Spezifikation) zum Zeitpunkt der Freigabe nicht abgeschlossen oder bewertet war. Es fehlt ein dokumentierter Audit-Trail-Review, der die Datenintegrität und die Einhaltung der GMP-Anforderungen für diese Freigabe bestätigt.
- ℹ️ 16 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): Die Abweichung DEV-MET-09 ist als "Minor" eingestuft, obwohl der Batch Record fuer die Charge MET-2026-C09 eine reale Netto-Ausbeute von 92,4% bei einem spezifizierten Toleranzbereich von 95.0% bis 102.0% zeigt; damit ist die geringe Einstufung ohne belegte Risikobewertung bzw. stuetzende Daten nicht ausreichend begruendet.
- ✅ `ERR_07_02` (medium) — gefunden via evidence_fuzzy (Score 0.484): Die CAPA-Maßnahme CAPA-MET-2026-09 benennt zwar einen Verantwortlichen (Leitung Instandhaltung) und eine Deadline (15.06.2026), jedoch fehlt ein dokumentierter Effectiveness Check zur Überprüfung der Wirksamkeit der verkürzten Wartungsintervalle.
- ℹ️ 30 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Batch-Impact-Bewertung für die Charge IBU-2026-P03 berücksichtigt nicht die Vorgängerschargen IBU-2026-P01 und IBU-2026-P02, die auf derselben Anlage (Rundläuferpresse TAB-02) mit ähnlichen Abweichungen (Oberstempel-Beschädigung, Mikrorisse) produziert wurden. Eine systematische Bewertung des Risikos für diese Chargen fehlt.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.692): Die Batch-Impact-Bewertung für die Charge IBU-2026-P03 enthält keine dokumentierte Erfassung aller potenziell betroffenen Chargen (Vorgänger- und Folgechargen). Die Historie der Prozessabweichungen an Presse TAB-02 zeigt zwei vorangegangene Einträge (14.03.2026: Charge IBU-2026-P01; 18.04.2026: Charge IBU-2026-P02), die nicht in der Bewertung berücksichtigt wurden. (Zitat: '- **14.03.2026:** Stopp wegen Oberstempel-Beschädigung bei Charge IBU-2026-P01. Werkzeug getauscht. (DEV-IBU-2026-042)
- **18.04.2026:** Mikrorisse an Unterstempel Station 5 bei Charge IBU-2026-P02 detektiert. Werkzeugset komplett gereinigt.')
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): Die Charge IBU-2026-P03 wurde trotz des Vorfalls (Werkzeugbruch) und der damit verbundenen potenziellen Kontamination mit metallischen Mikrofragmenten freigegeben, ohne dass eine CAPA-Maßnahme (CAPA-112-IBU) zur Risikominimierung abgeschlossen oder validiert wurde. Die Freigabe erfolgte vor dem Abschluss der Validierung des Inline-Metalldetektors (Deadline: 11.05.2026).
- ℹ️ 35 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Abweichung DEV-CEF-77 (pH-Wert Drift am 05.05.2026) wird im Schichtbuch als 'keine besonderen Vorkommnisse' dokumentiert (Chunk_b8b4675cea114babaaf9f75feed4bd1c), obwohl der pH-Wert für 6 Stunden außerhalb der spezifizierten Obergrenze (pH 7,40) lag und Spitzenwerte von pH 7,85 erreichte (Chunk_1de204b3b6d44e0cae87eafbf3a6d836). Dies widerspricht der Pflicht zur vollständigen und korrekten Dokumentation von Abweichungen.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Manueller Override des pH-Sollwerts im Bioreaktor BIO-10 (Charge CEF-BIOR-2026-77) wurde ohne dokumentierte Begruendung oder Autorisierung im Audit Trail durchgefuehrt. Dies stellt einen nicht autorisierten Admin-Eingriff dar.
- ✅ `ERR_09_03` (medium) — gefunden via evidence_substring (Score 1.0): Die QA-Freigabe im Change-Control-Antrag (CC-2026-104) ist nicht dokumentiert (Feld 'Leitung Qualitätskontrolle' leer). Eine geplante, aber nicht dokumentierte Freigabe ist nicht ausreichend.
- ℹ️ 26 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Die betroffene Charge INS-GLA-2025-05 wird in den Dokumenten referenziert, jedoch fehlt eine explizite und nachvollziehbare Dispositionsentscheidung mit Verknüpfung zum Batch Record. Die QA-Freigabe ist nicht dokumentiert, obwohl die Charge bereits in den Handel überführt wurde.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme 'CAPA-OOS-INS' benennt keinen verantwortlichen Massnahmenverantwortlichen für die Sofortmaßnahme (Re-Testing). Dies verstößt gegen die Anforderung, dass jede CAPA-Maßnahme einen benannten Verantwortlichen haben muss.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Sicherheitseinstufung vom 19.05.2026 erklärt, dass für Charge INS-GLA-2025-05 keine marktregulierenden Maßnahmen erforderlich seien und alle Analytikvorlagen als 'vorläufig erfüllt' gelten – obwohl das Labor-Re-Testing (CAPA-OOS-INS) zum Zeitpunkt dieser Erklärung noch nicht abgeschlossen war. Dies stellt eine Disposition von Marktware vor Abschluss der OOS-Untersuchung dar und verletzt req_dev_oos_before_disposition sowie req_batch_no_release_before_assessment.
- ℹ️ 22 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
