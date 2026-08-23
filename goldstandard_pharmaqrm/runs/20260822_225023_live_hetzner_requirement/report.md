# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hetzner` | Engine: `requirement`
- Zeitpunkt: 2026-08-22T22:50:23+00:00
- Anthropic-Modell: `-`
- OpenAI-Modell: `-`
- Hetzner-Modell: `Qwen3.8-27B`

## Gesamtergebnis

- **Sensitivität:** 12 von 25 versteckten Fehlern gefunden (48%)
- **In Prüfmappe sichtbar:** 11 von 25 versteckten Fehlern (44%)
- **Spezifität (Decoys):** 11 von 11 Decoys korrekt nicht beanstandet (100%) — deckt nur die gepflanzten Decoys ab, nicht die übrigen Findings
- **Findings mit Bezug zu echten Fehlern:** 28 von 202 (14%) — 11 als Treffer gewertet, 17 Wiederholungen bereits gemeldeter Fehler
- **Ohne Bezug zum Lösungsschlüssel:** 174 von 202 (86%) — ungeprüft, kann Fehlalarm oder echter, nicht gepflanzter Befund sein
- **Findings pro Fall:** 20.2 — so lang ist die Liste, die ein Prüfer durchgeht
- **Belegtreue:** 98 von 202 Findings mit verifiziertem Zitat (48%)

## Qualitätsmetriken

- Must-detect Recall: `0.48`
- Wiederholungen: `17` (Redundanzrate `0.6071`)
- Unsupported Findings: `1.0`
- False-positive-Grenzverletzungen: `0`
- Severity exact/under/over: `8/4/0`
- Auto-clear mit blockierendem Gold: `0`

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| hetzner | 225 | 981,829 | 209,924 | 1,191,753 |

## Fälle

| Fall | Status | Claims | Findings | Wiederholungen | ohne Bezug | Fehler gefunden | In Prüfmappe | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|
| CASE_01 | completed | 0 | 20 | 0 | 19 | 1/2 | 1/2 | 0/1 | - |
| CASE_02 | completed | 0 | 21 | 4 | 16 | 1/2 | 1/2 | 0/1 | - |
| CASE_03 | completed_with_model_failures | 0 | 22 | 0 | 22 | 0/2 | 0/2 | 0/2 | - |
| CASE_04 | completed_with_model_failures | 0 | 18 | 5 | 10 | 3/3 | 3/3 | 0/1 | - |
| CASE_05 | completed | 0 | 17 | 0 | 17 | 0/3 | 0/3 | 0/1 | - |
| CASE_06 | completed_with_model_failures | 0 | 22 | 1 | 20 | 1/2 | 1/2 | 0/1 | - |
| CASE_07 | completed_with_model_failures | 0 | 21 | 0 | 21 | 0/2 | 0/2 | 0/1 | - |
| CASE_08 | completed | 0 | 20 | 1 | 18 | 2/3 | 1/3 | 0/1 | - |
| CASE_09 | completed_with_model_failures | 0 | 21 | 4 | 15 | 2/3 | 2/3 | 0/1 | - |
| CASE_10 | completed | 0 | 20 | 2 | 16 | 2/3 | 2/3 | 0/1 | - |

## Modellausfälle

- **ProviderCallError** (4×): hetzner provider call failed with HTTP 504
  - betroffen: CASE_03/entailment:14, CASE_04/assess:1, CASE_06/extract[doc_40ed30e502a34eb08037e684c7e4b246:felder]:19, CASE_09/entailment:19
- **ProviderCallError** (1×): hetzner provider returned invalid JSON
  - betroffen: CASE_07/extract[doc_53cba3abff1e4f3f8f5ccab9478d2052:werte]:18

### CASE_01

- ✅ `ERR_01_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt eine dokumentierte Auswirkungsbewertung (Change-Impact-Assessment) und eine Validierungsbewertung. Der Abweichungsbericht enthält lediglich eine initiale Risikobewertung, die den Einfluss auf die Produktqualität ausschließt, basierend auf der visuellen Homogenität. Es fehlt jedoch ein expliziter Nachweis, dass eine formale Auswirkungsbewertung auf die Validierung durchgeführt wurde oder dass die Validierung überprüft/aktualisiert wurde. Die Aussage 'Einfluss ausgeschlossen' ist eine Behauptung ohne den geforderten Beleg für die Validierungsabdeckung.
- ❌ `ERR_01_01` (medium) — übersehen: Ungültiges, in der Zukunft liegendes Signaturdatum der QS-Prüfung.
- ℹ️ 19 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_02

- ✅ `ERR_02_01` (high) — gefunden via evidence_substring (Score 1.0): Die Freigabeentscheidung ist im Freigabe-Zertifikat dokumentiert und auf die Charge CPH-2026-991 bezogen. Das Chargenprotokoll enthält jedoch eine nachträgliche Korrektur der Ausbeute, die auf eine Abweichung hinweist. Es fehlt eine explizite, begründete Dispositionsentscheidung, die diese Abweichung adressiert und die Freigabe trotz der Abweichung rechtfertigt. Die bloße Freigabe ohne Bezugnahme auf die Abweichung und deren Bewertung ist nicht nachvollziehbar begründet im Sinne der Anforderung.
- ❌ `ERR_02_02` (medium) — übersehen: Yield außerhalb der Toleranzgrenze ohne Einleitung einer OOS/Abweichungsuntersuchung.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 16 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_03

- ❌ `ERR_03_01` (high) — übersehen: Anachronistische Zeitstempel zwischen Raum-Logbuch und Probenahme-Protokoll.
- ❌ `ERR_03_02` (medium) — übersehen: Referenzierung einer veralteten, potenziell ungültigen SOP-Version im CAPA-Plan.
- ℹ️ 22 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_04

- ✅ `ERR_04_01` (high) — gefunden via evidence_substring (Score 1.0): Die Unterlagen belegen den Einsatz eines automatisierten SCADA-Systems, das die Temperaturdaten erfasst. Es liegt jedoch kein Nachweis vor, dass ein Audit Trail existiert, regelmäßig geprüft wird oder dass sicherheitsrelevante Einträge nicht ausgeschlossen wurden. Die bloße Existenz des Protokolls belegt nicht die Erfüllung der Review-Pflicht.
- ✅ `ERR_04_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan definiert ein Re-Training als Maßnahme. Es fehlt jedoch jegliche Dokumentation einer definierten und dokumentierten Wirksamkeitsprüfung (Effectiveness Check), die nach Durchführung des Trainings zu erfolgen hat. Die Anforderung verlangt, dass CAPAs nur mit definierter Wirksamkeitsprüfung abgeschlossen werden dürfen. Da der Nachweis für die Definition oder Durchführung dieser Prüfung fehlt, ist die Anforderung nicht erfüllt.
- ✅ `ERR_04_03` (critical) — gefunden via evidence_substring (Score 1.0): Die QS-Chargenbewertung begründet die Freigabe der Charge PAR-2026-H102 explizit mit der Bewertung der Abweichung DEV-P-2026-092. Die Dispositionsentscheidung ist somit begründet und im Dokument verknüpft. Die Verknüpfung zum Batch Record ist implizit durch die Chargennummer und den Kontext der Abweichung gegeben, da die Bewertung auf den in der Abweichung dokumentierten Werten basiert.
- 🔁 5 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 10 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_05

- ❌ `ERR_05_01` (medium) — übersehen: Verweis auf ein nicht vorhandenes bzw. fehlendes Dokumentenelement (Anhang 4).
- ❌ `ERR_05_02` (high) — übersehen: Kritischer Zeitkonflikt zwischen manuellem Prozess-Logbuch und automatisiertem Zutrittskontrollsystem.
- ❌ `ERR_05_03` (medium) — übersehen: Mangelnde Zuordnungsgenauigkeit von Unterschrift/Initialen zur Personalnummer.
- ℹ️ 17 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_06

- ✅ `ERR_06_01` (high) — gefunden via evidence_fuzzy (Score 0.679): Die Unterlagen belegen einen Verstoß gegen die Prozessparameter. Der interne Prüfplan definiert ein striktes Akzeptanzkriterium für den Wassergehalt von 11,5% bis 12,8%. Die interne Re-Analyse ergab jedoch einen Wassergehalt von 13,2%, was die obere Grenze überschreitet. Dies ist als Abweichung zu bewerten, auch wenn die Charge freigegeben wurde.
- ❌ `ERR_06_02` (critical) — übersehen: Wirkstofffreigabe durch QA trotz ungelöster und aktive Laborabweichung.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 20 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_07

- ❌ `ERR_07_01` (high) — übersehen: Yield-Unterschreitung wird fälschlicherweise als konform deklariert.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 21 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass die Einstufung einer Abweichung durch eine nachvollziehbare Risikobewertung belegt ist und dass eine Einstufung als geringfügig ohne belastbare physikalisch-chemische oder labortechnische Daten unzulässig ist. Der Abweichungsbericht stuft das Ereignis implizit als geringfügig/isoliert ein ('isoliertes Einzelereignis', 'absolut ausgeschlossen'). Es werden jedoch keine labortechnischen oder physikalisch-chemischen Daten (z. B. Metallspurenanalyse, Partikelzählung) zitiert, die diese Einstufung stützen. Die Behauptung 'absolut ausgeschlossen' ist eine qualitative Aussage ohne quantitative Belege. Da die Anforderung explizit verbietet, eine geringfügige Einstufung ohne belastbare Labordaten vorzunehmen, und solche Daten in den Chunks fehlen, liegt ein Verstoß vor.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.458): Die Anforderung verlangt, dass die Einstufung einer Abweichung durch eine nachvollziehbare Risikobewertung belegt ist und dass eine Einstufung als geringfügig ohne belastbare physikalisch-chemische oder labortechnische Daten unzulässig ist. Der Abweichungsbericht stuft das Ereignis implizit als geringfügig/isoliert ein ('isoliertes Einzelereignis', 'absolut ausgeschlossen'). Es werden jedoch keine labortechnischen oder physikalisch-chemischen Daten (z. B. Metallspurenanalyse, Partikelzählung) zitiert, die diese Einstufung stützen. Die Behauptung 'absolut ausgeschlossen' ist eine qualitative Aussage ohne quantitative Belege. Da die Anforderung explizit verbietet, eine geringfügige Einstufung ohne belastbare Labordaten vorzunehmen, und solche Daten in den Chunks fehlen, liegt ein Verstoß vor.
- ❌ `ERR_08_03` (medium) — übersehen: Unrealistisches, nicht plausibles CAPA-Zieldatum ohne adäquate Projektrealisierungszeit.
- 🔁 1 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 18 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Es besteht ein direkter Widerspruch zwischen dem Batch Record und dem Abweichungsbericht. Das Batch Record behauptet, es gÃ¤be 'Keine besonderen Vorkommnisse' und die 'Werte [seien] stabil', wÃ¤hrend der Abweichungsbericht eine erhebliche pH-Drift mit Spitzenwerten von 7,85 (Grenze 7,40) fÃ¼r 6 Stunden dokumentiert. Diese WidersprÃ¼che wurden nicht aufgeklÃ¤rt.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): Die Anforderung verlangt, dass die Dispositionsentscheidung jeder betroffenen Charge begründet und mit den Batch Records verknüpft ist. Der Abweichungsbericht DEV-CEF-77 erwähnt, dass die 'Aufarbeitung fortgesetzt wurde', was auf eine Disposition hinweist, die Charge weiterzuverarbeiten. Es wird jedoch keine explizite, begründete Dispositionsentscheidung (z. B. 'Freigabe trotz Abweichung', 'Quarantäne', 'Rückruf') dokumentiert, die klar mit dem Batch Record verknüpft ist. Der Batch Record-Auszug (document_02) erwähnt 'Keine besonderen Vorkommnisse in der Schicht. Werte stabil', was im Widerspruch zur dokumentierten Abweichung (pH-Drift bis 7,85) steht und keine Dispositionsentscheidung enthält. Die Begründung für die Fortsetzung der Aufarbeitung ist im Abweichungsbericht nur knapp ('Biomasse-Entwicklung blieb im Akzeptanzkorridor') und nicht als formale Dispositionsentscheidung mit Verknüpfung zum Batch Record ausgearbeitet. Daher ist die Anforderung nicht erfüllt.
- ❌ `ERR_09_03` (medium) — übersehen: Unvollständig genehmigtes Change-Control-Dokument ohne finale QK-Freigabe.
- 🔁 4 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 15 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)

### CASE_10

- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Der CAPA-Plan weist im Feld 'Verantwortlich' explizit '[Kein Eintrag / Offen]' aus. Die Anforderung verlangt einen benannten Maßnahmenverantwortlichen. Da dieses Pflichtfeld leer ist, liegt ein Verstoß vor.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die QA-Note behauptet, dass 'Sämtliche Analytikvorgaben ... vorläufig erfüllt' sind, obwohl der Stabilitätsbericht (doc_01) einen klaren OOS-Befund (0,32% > 0,20%) dokumentiert. Zudem wird im CAPA-Plan eine Re-Analyse angeordnet, was bedeutet, dass die Bewertung noch nicht abgeschlossen ist. Die Behauptung der Erfüllung trotz offener Abweichung und fehlender finaler Bewertung stellt einen Verstoß gegen die Regel dar, keine Freigabe/Disposition vor abgeschlossener Bewertung vorzunehmen. Die Charge ist bereits im Handel, aber die QA-Note suggeriert eine Konformität, die durch den OOS-Befund widerlegt wird, ohne dass die Abweichungsbewertung abgeschlossen ist.
- ❌ `ERR_10_01` (critical) — übersehen: Unzulässiges Aufschieben von Folgemaßnahmen bei einem manifesten OOS-Stabilitätsfehler.
- 🔁 2 weitere Findings zu bereits gemeldeten Fehlern (Wiederholungen)
- ℹ️ 16 Findings ohne Bezug zum Lösungsschlüssel (manuell prüfen)
