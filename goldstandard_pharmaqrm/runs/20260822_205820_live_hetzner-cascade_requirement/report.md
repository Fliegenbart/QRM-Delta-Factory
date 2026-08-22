# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hetzner-cascade` | Engine: `requirement`
- Zeitpunkt: 2026-08-22T20:58:20+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `-`
- Hetzner-Modell: `Qwen3.8-27B`

## Gesamtergebnis

- **Sensitivität:** 7 von 25 versteckten Fehlern gefunden (28%)
- **In Prüfmappe sichtbar:** 6 von 25 versteckten Fehlern (24%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 13 von 205 (6%) — 6 als Treffer gewertet, 7 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 192 von 205 (94%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 20.5 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 46 von 205 Findings mit verifiziertem Zitat (22%)

## Qualitätsmetriken

- Must-detect Recall: `0.28`
- Wiederholungen: `7` (Redundanzrate `0.5385`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `3/3/1`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 20 | 32,322 | 5,688 | 38,010 |
| hetzner | 164 | 680,657 | 107,609 | 788,266 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 22 | 0 | 22 | 0/2 | 0/2 | 0/1 | - |
| CASE_02 | completed | 0 | 20 | 0 | 20 | 0/2 | 0/2 | 0/1 | - |
| CASE_03 | completed | 0 | 21 | 0 | 21 | 0/2 | 0/2 | 0/2 | - |
| CASE_04 | completed | 0 | 22 | 5 | 14 | 3/3 | 3/3 | 0/1 | - |
| CASE_05 | completed | 0 | 18 | 0 | 18 | 0/3 | 0/3 | 0/1 | - |
| CASE_06 | completed | 0 | 19 | 1 | 17 | 1/2 | 1/2 | 0/1 | - |
| CASE_07 | completed_with_model_failures | 0 | 21 | 0 | 21 | 0/2 | 0/2 | 0/1 | - |
| CASE_08 | completed | 0 | 21 | 1 | 19 | 2/3 | 1/3 | 0/1 | - |
| CASE_09 | completed | 0 | 22 | 0 | 22 | 0/3 | 0/3 | 0/1 | - |
| CASE_10 | completed | 0 | 19 | 0 | 18 | 1/3 | 1/3 | 0/1 | - |

## Modellausfälle

- **ProviderCallError** (1×): hetzner provider returned invalid JSON
  - betroffen: CASE_07/extract[doc_284b333d3416413abffd8b836f81276f:werte]:18

### CASE_01

- ❌ `ERR_01_01` (medium) — übersehen: Ungültiges, in der Zukunft liegendes Signaturdatum der QS-Prüfung.
- ❌ `ERR_01_02` (high) — übersehen: Fehlklassifizierung einer kritischen Prozessparameter-Abweichung.
- ℹ️ 22 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ❌ `ERR_02_01` (high) — übersehen: Undokumentierte und nicht gegengezeichnete manuelle Datenkorrektur im Ausbeuteprotokoll.
- ❌ `ERR_02_02` (medium) — übersehen: Yield außerhalb der Toleranzgrenze ohne Einleitung einer OOS/Abweichungsuntersuchung.
- ℹ️ 20 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ❌ `ERR_03_01` (high) — übersehen: Anachronistische Zeitstempel zwischen Raum-Logbuch und Probenahme-Protokoll.
- ❌ `ERR_03_02` (medium) — übersehen: Referenzierung einer veralteten, potenziell ungültigen SOP-Version im CAPA-Plan.
- ℹ️ 21 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Es besteht ein Widerspruch zwischen dem manuellen Herstellprotokoll (48,2 °C) und dem SCADA-Protokoll (max. 44,5 °C). Die QS-Freigabe stützt sich auf die SCADA-Daten, ignoriert aber die höhere manuelle Messung. Es fehlt eine Begründung für diese Diskrepanz oder eine Erklärung, warum die manuelle Aufzeichnung als unzuverlässig eingestuft wurde. Die Konsistenz und Vollständigkeit der Aufzeichnungen (ALCOA+) ist nicht gegeben, da die Daten nicht übereinstimmen und keine Klärung dokumentiert ist.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass CAPA-Maßnahmen mit einem definierten und dokumentierten Effectiveness Check abgeschlossen werden können. Die vorliegenden Dokumente beschreiben nur die Planung der Maßnahme (Re-Training), enthalten aber keinerlei Definition, Planung oder Nachweis einer Wirksamkeitsprüfung (Effectiveness Check). Da die Maßnahme mit einem Qualitätsrisiko (Temperaturüberschreitung) verknüpft ist, ist der fehlende Nachweis der Wirksamkeitsprüfung ein Verstoß gegen die Anforderung, da der Auslöser (die CAPA-Maßnahme) belegt ist, der geforderte Nachweis aber fehlt.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Dispositionsentscheidung (Freigabe) ist in der Quality Approval Note dokumentiert und begründet ('qualitätskonform'). Die Charge PAR-2026-H102 wird in der Approval Note explizit genannt und ist mit dem Batch Record (Auszug Herstellprotokoll) verknüpft, das dieselbe Chargennummer und den Prozessschritt (Trocknung/WS-03) bestätigt. Die Verknüpfung ist nachvollziehbar.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 14 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ❌ `ERR_05_01` (medium) — übersehen: Verweis auf ein nicht vorhandenes bzw. fehlendes Dokumentenelement (Anhang 4).
- ❌ `ERR_05_02` (high) — übersehen: Kritischer Zeitkonflikt zwischen manuellem Prozess-Logbuch und automatisiertem Zutrittskontrollsystem.
- ❌ `ERR_05_03` (medium) — übersehen: Mangelnde Zuordnungsgenauigkeit von Unterschrift/Initialen zur Personalnummer.
- ℹ️ 18 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_fuzzy (Score 0.679): Der Laborbericht (document_02) dokumentiert, dass der Wassergehalt des Rohstoffs (13,2%) das definierte Akzeptanzkriterium (11,5% - 12,8%) überschreitet. Dies ist eine Überschreitung eines kritischen Parameters (Reinheit/Qualität des Wirkstoffs). Die Anforderung besagt, dass eine Überschreitung als Abweichung zu bewerten ist. Zwar wurde eine Abweichung eröffnet, aber die QA-Freigabe (document_03) autorisiert den Einsatz des Rohstoffs, obwohl der Parameter außerhalb der Grenzen liegt und die Abweichung noch offen ist ('In Untersuchung'). Die Freigabe eines Rohstoffs, der die Spezifikation nicht erfüllt, stellt einen Verstoß gegen die Einhaltung der Prozessparameter/Qualitätsanforderungen dar, da die Abweichung nicht als 'abgeschlossen' oder 'akzeptiert' dokumentiert ist, bevor die Freigabe erfolgte.
- ❌ `ERR_06_02` (critical) — übersehen: Wirkstofffreigabe durch QA trotz ungelöster und aktive Laborabweichung.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 17 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ❌ `ERR_07_01` (high) — übersehen: Yield-Unterschreitung wird fälschlicherweise als konform deklariert.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 21 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine nachvollziehbare Risikobewertung zur Begründung der Einstufung. Der Abweichungsbericht stuft das Ereignis als 'isoliertes Einzelereignis' ein und behauptet, es habe keinen systematischen Charakter. Der Logbuchauszug (document_02) belegt jedoch, dass es in den letzten zwei Monaten bereits zwei ähnliche Vorfälle (Oberstempel-Beschädigung, Mikrorisse) an derselben Anlage TAB-02 gab. Dies widerspricht der Behauptung des 'isolierten Einzelereignisses' und deutet auf ein systematisches Problem hin. Es fehlen physikalisch-chemische oder labortechnische Daten, die die geringe Schwere oder den Ausschluss von Kontaminationen belegen. Die Einstufung ist daher nicht durch eine belastbare Risikobewertung belegt, sondern basiert auf einer falschen Prämisse.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.458): Die Anforderung verlangt eine nachvollziehbare Risikobewertung zur Begründung der Einstufung. Der Abweichungsbericht stuft das Ereignis als 'isoliertes Einzelereignis' ein und behauptet, es habe keinen systematischen Charakter. Der Logbuchauszug (document_02) belegt jedoch, dass es in den letzten zwei Monaten bereits zwei ähnliche Vorfälle (Oberstempel-Beschädigung, Mikrorisse) an derselben Anlage TAB-02 gab. Dies widerspricht der Behauptung des 'isolierten Einzelereignisses' und deutet auf ein systematisches Problem hin. Es fehlen physikalisch-chemische oder labortechnische Daten, die die geringe Schwere oder den Ausschluss von Kontaminationen belegen. Die Einstufung ist daher nicht durch eine belastbare Risikobewertung belegt, sondern basiert auf einer falschen Prämisse.
- ❌ `ERR_08_03` (medium) — übersehen: Unrealistisches, nicht plausibles CAPA-Zieldatum ohne adäquate Projektrealisierungszeit.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 19 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ❌ `ERR_09_01` (critical) — übersehen: Intentionale Falschdokumentation im Batch Record im Widerspruch zum SCADA-Audit-Trail.
- ❌ `ERR_09_02` (high) — übersehen: Fehlerhafte Root-Cause-Ermittlung durch Ignorieren der System-Logfiles.
- ❌ `ERR_09_03` (medium) — übersehen: Unvollständig genehmigtes Change-Control-Dokument ohne finale QK-Freigabe.
- ℹ️ 22 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan (document_02) weist das Feld 'Verantwortlich' als '[Kein Eintrag / Offen]' aus. Die Anforderung verlangt einen benannten Maßnahmenverantwortlichen. Da dieses Pflichtfeld leer ist, liegt ein Verstoß vor.
- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- ❌ `ERR_10_03` (critical) — übersehen: Grob fehlerhafte, verharmlosende QS-Bewertung eines kritischen Marktwaren-Stabilitätsausfalls.
- ℹ️ 18 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
