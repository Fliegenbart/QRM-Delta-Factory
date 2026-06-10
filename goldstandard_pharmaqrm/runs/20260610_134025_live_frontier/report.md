# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `frontier`
- Zeitpunkt: 2026-06-10T13:40:25+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `-`

## Gesamtergebnis

- **Sensitivität:** 9 von 11 versteckten Fehlern gefunden (82%)
- **Spezifität (Decoys):** 4 von 4 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 115 von 136 Findings mit verifiziertem Zitat (85%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 20 | 225,487 | 120,581 | 346,068 |
| extraction:anthropic | 4 | 0 | 0 | 0 |
| openai | 8 | 76,170 | 22,210 | 98,380 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_07 | completed | 25 | 33 | 1/2 | 0/1 | human_review_required |
| CASE_08 | completed | 29 | 34 | 3/3 | 0/1 | human_review_required |
| CASE_09 | completed | 10 | 30 | 2/3 | 0/1 | human_review_required |
| CASE_10 | completed | 29 | 39 | 3/3 | 0/1 | human_review_required |

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.566): Deviation DEV-MET-09 was classified as 'Minor', but the batch yield for MET-2026-C09 is 92.4%, which is below the validated lower acceptance limit of 95.0%. The batch record entry was manually marked 'Pass' despite the out-of-specification yield. This inconsistency raises the question of whether the Minor classification of the deviation adequately accounts for the yield OOS result, and whether the CAPA scope is sufficient. Per req_gs_deviation_classification, classification without substantiated physicochemical data is not permissible; per req_gs_spec_limits, out-of-specification results must be treated as deviations.
- ❌ `ERR_07_02` (medium) — übersehen: Fehlen des regulatorisch geforderten Effectiveness Checks im CAPA-Dokument.
- ℹ️ 32 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_08

- ✅ `ERR_08_01` (critical) — gefunden via evidence_substring (Score 1.0): The trend analysis document (doc_445fb6233bdc448bb06a49c71a0647bb) identifies three separate tooling damage events on press TAB-02 within approximately two months (DEV-IBU-2026-042 on 14.03.2026, DEV-IBU-2026-081 on 18.04.2026, DEV-IBU-2026-112 on 10.05.2026), each affecting a different batch. However, the deviation report DEV-IBU-2026-112 classifies the event as an 'isolated single event without systematic character'. This classification directly contradicts the trend data and represents an inadequate impact and root cause assessment. The CAPA-112-IBU does not appear to address the systematic tooling failure pattern or the potential impact on batches IBU-2026-P01 and IBU-2026-P02 from prior events.
- ✅ `ERR_08_02` (high) — gefunden via evidence_fuzzy (Score 0.697): The impact assessment concludes that other batches or preceding production steps are absolutely excluded, but the provided history shows similar tooling-related deviations on the same press TAB-02 across batches IBU-2026-P01, IBU-2026-P02, and IBU-2026-P03. Without a documented all-batch assessment and charge list, cross-batch impact exclusion is insufficiently supported.
- ✅ `ERR_08_03` (medium) — gefunden via evidence_substring (Score 1.0): The CAPA-112-IBU validation deadline is set to 11.05.2026, which is only one day after the incident date of 10.05.2026. Completing full procurement, qualification, software integration, and validation of an inline metal detector within one day is physically implausible. This constitutes a data integrity concern under req_gs_data_integrity_signatures (ALCOA+ plausibility requirement) and raises serious doubt about the credibility of the CAPA timeline and the adequacy of the corrective action.
- ℹ️ 31 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_09

- ✅ `ERR_09_01` (critical) — gefunden via evidence_substring (Score 1.0): Adversarial review found required evidence missing or not clearly present in the claim ledger.
- ✅ `ERR_09_02` (high) — gefunden via evidence_substring (Score 1.0): The technical root cause of the pH drift remains unresolved, which leaves residual uncertainty in the batch impact conclusion and supports escalation for human review before closure.
- ❌ `ERR_09_03` (medium) — übersehen: Unvollständig genehmigtes Change-Control-Dokument ohne finale QK-Freigabe.
- ℹ️ 28 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): The deviation record states that regular stability testing will continue at the 18-month timepoint, while the OOS impurity finding and its root cause remain unresolved. Continuing stability testing without resolving the OOS finding may generate further data of uncertain validity and does not address the underlying quality issue. This is a gap in deviation management process control.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): QA approval and final closure are not evidenced because the records state that re-testing is still pending and only provisional fulfillment is concluded, which is insufficient for documented approval before completion.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): The batch-impact package does not evidence a batch-specific disposition or release rationale linked to batch records for INS-GLA-2025-05, so batch impact cannot be considered fully closed.
- ℹ️ 36 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
