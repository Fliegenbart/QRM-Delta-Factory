# Ringversuch-Report: Goldstandard PharmaQRM

- Modus: `live` | Stack: `hybrid`
- Zeitpunkt: 2026-06-13T20:22:50+00:00
- Anthropic-Modell: `claude-sonnet-4-6`
- OpenAI-Modell: `gpt-5.4`
- Mistral-Modell: `mistral-large-latest`

## Gesamtergebnis

- **Sensitivität:** 6 von 7 versteckten Fehlern gefunden (86%)
- **Spezifität (Decoys):** 3 von 3 Decoys korrekt nicht beanstandet (100%)
- **Belegtreue:** 61 von 62 Findings mit verifiziertem Zitat (98%)

## Token-Verbrauch

| Provider | Calls | Input | Output | Total |
|---|---|---|---|---|
| anthropic | 3 | 57,878 | 23,070 | 80,948 |
| extraction:mistral | 3 | 9,721 | 6,918 | 16,639 |
| mistral | 21 | 360,383 | 57,612 | 417,995 |
| openai | 3 | 48,842 | 9,522 | 58,364 |

## Fälle

| Fall | Status | Claims | Findings | Fehler gefunden | Decoy-Fehlalarme | Entscheidung |
|---|---|---|---|---|---|---|
| CASE_06 | completed | 22 | 22 | 1/2 | 0/1 | human_review_required |
| CASE_07 | completed | 19 | 23 | 2/2 | 0/1 | human_review_required |
| CASE_10 | needs_human_review | 20 | 17 | 3/3 | 0/1 | blocked_due_to_model_failure |

### CASE_06

- ✅ `ERR_06_02` (critical) — gefunden via evidence_fuzzy (Score 0.718): Die Vollständigkeit der Originaldaten gemäß ALCOA+ für die Abweichung LAB-DEV-2026-031 und die Freigabe der Charge AMO-SUP-2026-01 ist nicht vollständig nachgewiesen. Es fehlen Nachweise, dass alle Aufzeichnungen zurechenbar, lesbar, zeitgleich, original und korrekt sind.
- ❌ `ERR_06_01` (high) — übersehen: Akzeptanzkriterium der internen Spezifikation wird durch das Lieferanten-Zertifikat verletzt.
- ℹ️ 21 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_07

- ✅ `ERR_07_01` (high) — gefunden via evidence_fuzzy (Score 0.459): Die Charge MET-2026-C09 weist eine Ausbeute von 92,4% auf, die außerhalb des spezifizierten Toleranzbereichs von 95,0% bis 102,0% liegt. Die Abweichung DEV-MET-09 wurde als 'Minor' eingestuft, jedoch fehlt eine detaillierte Bewertung der Auswirkungen dieser Unterschreitung auf die Produktqualität und Patientensicherheit.
- ✅ `ERR_07_02` (medium) — gefunden via evidence_fuzzy (Score 0.667): Für die CAPA-MET-2026-09 (Verkürzung der Wartungsintervalle für Sprühdüsen von 6 auf 3 Monate) ist kein Effectiveness-Check-Claim vorhanden. Die CAPA adressiert ein wiederkehrendes Ausrüstungsrisiko (Düsenverstopfung), das direkte Auswirkungen auf die Produktqualität hat. Ohne definierten und dokumentierten Wirksamkeitsnachweis darf die CAPA nicht als abgeschlossen gelten.
- ℹ️ 21 weitere Findings ohne Gold-Zuordnung (manuell prüfen)

### CASE_10

- ✅ `ERR_10_01` (critical) — gefunden via evidence_substring (Score 1.0): Die unbekannte Verunreinigung in der Charge INS-GLA-2025-05 (0,32% bei Spezifikationsgrenze von max. 0,20%) wurde als temporärer Ausreißer bewertet, ohne dass eine dokumentierte Bewertung der Auswirkungen auf die Sterilitätsassurance oder Reinigungsvalidierung vorliegt. Dies stellt ein Risiko für die Produktqualität und Patientensicherheit dar.
- ✅ `ERR_10_02` (high) — gefunden via evidence_substring (Score 1.0): Die CAPA-Maßnahme (CAPA-OOS-INS) zur Untersuchung der unbekannten Verunreinigung in der Charge INS-GLA-2025-05 ist unvollständig. Es fehlt die Benennung eines verantwortlichen Mitarbeiters, und die Wirksamkeitsprüfung der Maßnahme ist nicht dokumentiert.
- ✅ `ERR_10_03` (critical) — gefunden via evidence_substring (Score 1.0): Die Charge INS-GLA-2025-05 wurde vorläufig freigegeben, obwohl die OOS-Untersuchung der unbekannten Verunreinigung nicht abgeschlossen ist. Dies verstößt gegen die Anforderung, dass OOS-Ergebnisse vollständig untersucht sein müssen, bevor eine Disposition erfolgt.
- ℹ️ 14 weitere Findings ohne Gold-Zuordnung (manuell prüfen)
