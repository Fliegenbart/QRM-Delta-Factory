# Briefing: Knifflige synthetische GMP-Testdaten erzeugen

Ziel: synthetische Dokumentpakete erzeugen, mit denen wir prüfen, ob die QRM Delta Engine versteckte GMP-/QRM-Risiken findet. Die Fälle sollen schwer genug sein, dass auch menschliche Experten genau lesen müssen.

Wichtig: Keine echten Firmen-, Produkt-, Patienten- oder Personendaten verwenden. Alles muss synthetisch sein.

## Copy-Paste Prompt für ChatGPT

```text
Du bist ein erfahrener GMP Quality Risk Manager, QA Auditor, Data-Integrity Reviewer und Validierungs-SME.

Erzeuge synthetische Testdaten für ein AI-assisted pharmazeutisches Risk-Orchestration-System.

Ziel:
Die Testdaten sollen realistisch wirken und mehrere versteckte Fehler enthalten. Die Fehler sollen nicht offensichtlich in einer einzelnen Zeile stehen, sondern aus Widersprüchen, alten Anhängen, unpassender Evidenz, Scope-Lücken oder fehlenden Pflichtnachweisen entstehen.

Wichtige Regeln:
- Keine echten Firmen-, Produkt-, Patienten- oder Personendaten.
- Alle Dokumente müssen synthetisch sein.
- Keine Behauptung soll regulatorische Akzeptanz oder Compliance garantieren.
- Die Dokumente sollen als .md, .txt oder .csv nutzbar sein.
- Jedes Dokument soll Dokument-ID, Version, Datum, Dokumenttyp, Prozessbereich und Seiten-/Abschnittsplatzhalter enthalten.
- Baue absichtlich subtile Fehler ein, aber verrate sie nicht im Dokument selbst.
- Erzeuge zusätzlich eine separate GOLD_STANDARD.json, die die versteckten Findings enthält. Diese Datei ist nur für die Auswertung gedacht und darf nicht in das Tool hochgeladen werden.

Erzeuge 5 unabhängige Dokumentpakete.

Jedes Paket soll enthalten:
1. change_control.md oder deviation_record.md oder capa_record.md
2. baseline_risk_assessment.md oder fmea.csv
3. sop_excerpt.md
4. validation_or_test_evidence.md
5. batch_record_or_execution_record.md
6. optional: audit_trail_review.md, training_record.md, supplier_change.md, cleaning_validation.md oder method_validation.md
7. GOLD_STANDARD.json

Jedes Paket soll 3 bis 6 versteckte Findings enthalten.

Finding-Typen, aus denen du mischen sollst:
- alte Validierung deckt den aktuellen Change nicht ab
- SOP wurde aktualisiert, Training fehlt oder ist nicht wirksam
- CAPA geschlossen, aber Effectiveness Check fehlt
- Batch Impact Assessment erwähnt nicht alle betroffenen Chargen
- QA Approval ist geplant, aber nicht dokumentiert
- Root Cause "Operator Error" ist nicht ausreichend belegt
- Audit Trail Review schließt relevante Events aus
- Datenintegritätsrisiko durch manuelle Override-/Admin-Aktion
- widersprüchliche Aussagen zwischen Summary, Tabelle und Anhang
- falsche Entwarnung wegen ungeeignetem Vergleichsstandort oder anderem Equipment
- Methode/Prüfung ist für den aktuellen Grenzwert nicht geeignet
- Cleaning- oder Sterilitätsrisiko wird nur indirekt erwähnt
- Supplier-/Materialänderung wird als "no impact" gewertet, obwohl Spezifikation, Methode oder Quelle geändert wurde
- fehlende Pflichtanhänge
- Out-of-scope-Dokument oder falscher Prozessbereich

Schwierigkeitsgrad:
- Mindestens 2 Findings pro Paket sollen nur durch Vergleich mehrerer Dokumente erkennbar sein.
- Mindestens 1 Finding pro Paket soll auf veralteter Evidenz beruhen.
- Mindestens 1 Finding pro Paket soll wie "no issue found" aussehen, aber nicht ausreichend belegt sein.
- Mindestens 1 Paket soll schlechte Dokumentqualität simulieren: leere Abschnitte, fehlender Anhang, OCR-Artefakte oder unklare Tabellenwerte.

GOLD_STANDARD.json Schema:
{
  "package_id": "...",
  "package_title": "...",
  "document_type": "...",
  "process_area": "...",
  "must_detect_findings": [
    {
      "finding_id": "...",
      "severity": "critical | high | medium | low",
      "risk_category": "...",
      "risk_statement": "...",
      "why_it_is_hard": "...",
      "expected_evidence_refs": [
        {
          "document_id": "...",
          "page_or_section": "...",
          "quote": "..."
        }
      ],
      "expected_requirement_theme": "...",
      "should_block_auto_clear": true
    }
  ],
  "acceptable_false_positive_boundaries": [
    "..."
  ],
  "notes_for_evaluator": "..."
}

Outputformat:
- Gib pro Paket zuerst eine Dateiliste aus.
- Danach jede Datei einzeln in einem Markdown-Codeblock mit Dateiname als Überschrift.
- GOLD_STANDARD.json jeweils separat und deutlich als NICHT HOCHLADEN markieren.
- Verwende realistische, aber knappe Dokumente. Keine Romane. Pro Datei 300 bis 900 Wörter.
```

## Gute Testfälle für die erste Runde

1. Change Control: neuer Prüfgrenzwert, alte Validierung, anderes Equipment als Vergleichsbasis.
2. Deviation: "Operator Error" als Root Cause, aber Alarmhistorie und Wartungsnotiz widersprechen.
3. CAPA: formell geschlossen, aber Effectiveness Check fehlt oder misst das falsche Signal.
4. Batch Impact: Summary sagt "no impact", Anhang nennt weitere Chargen oder Rework.
5. Data Integrity: Audit Trail Review erwähnt keine Änderungen, schließt aber Admin-Events aus.
6. Supplier Change: Material bleibt "gleichwertig", aber Prüfmethode oder Spezifikation ändert sich.
7. Cleaning Validation: neue Produktmatrix wird nicht vom Worst-Case abgedeckt.
8. Aseptic Processing: Interventionen und EM-Hinweise sind verteilt, aber nicht im Impact Assessment bewertet.

## Wie wir die Pakete auswerten

Für jedes Paket vor dem Upload festlegen:
- Welche Findings müssen gefunden werden?
- Welche Evidenzstellen müssen zitiert werden?
- Welche Findings dürfen nicht automatisch geschlossen werden?
- Welche Reviewer-Rolle ist erforderlich?

Nach dem Toollauf je Finding markieren:
- gefunden
- teilweise gefunden
- übersehen
- falscher Alarm
- falsche Evidenz
- falsche Severity
- falsche Reviewer-Route

Jedes übersehene High/Critical Finding wird danach ein neuer Regressionstest oder eine neue Guardrail.
