# Miss-Taxonomie Blindkorpus-2 (Nachmessung 2026-08-08)

Stand der Messung: 26/38 (68 %) Sensitivität, 41/42 Decoys, Lauf
`20260808_144737_live_hybrid_requirement` gegen `f73af45`. Mit dieser Analyse
ist Blindkorpus-2 vereinbarungsgemäß **Regressionskorpus**; die nächste
unabhängige Zahl braucht Blindkorpus-3.

Jeder der 12 Misses wurde von einem eigenen Analyse-Agenten gegen Verdicts,
Model-Calls, Evidenzen und Answer-Key geprüft (adversariale Verifikation, wo
die API sie nicht abbrach). Mechanismus-Verteilung:

| Mechanismus | Anzahl | Fälle |
|---|---|---|
| Assessor-Urteil | 7 | 203-E002, 205-E002, 206-E004, 209-E002/-E003/-E005, 210-E002 |
| Fehlende Requirement | 2 | 204-E004 (Meldefrist), 209-E004 (Einsatz vor CC-Freigabe) |
| **Gefunden, aber verloren** | 2 | 201-E002 (Matcher-Artefakt), 210-E003 (Gate-Demotion) |
| Extraktions-Trunkierung | 1 | 203-E001 (werte-Pass) |

## Die wichtigste Einzelerkenntnis: 2 Misses waren Treffer

- **201-E002**: Das Verdict beschreibt den gepflanzten Fehler nahezu wortgleich
  mit dem Answer-Key. Sein Belegzitat enthielt aber **fehlkodierte Umlaute**
  (Steuerzeichen statt ä/ü), fiel durch die Provenienzprüfung, und ohne
  Zitat-Anker blieb das Fuzzy-Matching unter der Schwelle.
- **210-E003**: `model_status=violated`, Rationale benennt exakt die fehlende
  Charge — aber beide Zitate trugen **halluzinierte Chunk-IDs**, wurden
  verworfen, das Verdict demotete zu `unclear`.

Effektiv erkannt hat die Engine also 28/38 (74 %). Die Reparatur ist in beiden
Fällen dieselbe Baustelle: Zitat-Rettung vor der Verwerfung (Mojibake-
Normalisierung; bei nicht auflösbarer Chunk-ID Textabgleich gegen den
Volltext des genannten Dokuments).

## Substruktur der 7 Urteils-Misses

1. **Arithmetik nicht nachgerechnet (3)** — der größte Block, und alle drei
   deterministisch prüfbar:
   - 205-E002: Faktor-10-Umrechnungsfehler (113.190 µg → „11,32 mg"); der
     Assessor prüfte nur Konsistenz *zwischen* Dokumenten — der falsche Wert
     war konsistent weitergetragen.
   - 206-E004: Summenzeile widerspricht Einzelpositionen (62,144 vs. 62,24x kg);
     Rationale behauptet aktiv Übereinstimmung.
   - 209-E002: „14 von 320 (2,8 %)" — tatsächlich 4,4 %; beide Belegstellen
     lagen wörtlich in der Evidenzliste des `fulfilled`-Verdicts.
2. **Zeitliche Reihenfolge (2)**: Review vor dem geprüften Ereignis datiert
   (209-E003); Freigabevermerk referenziert später abgeschlossene Prüfung
   (210-E002). Deckungsgleich mit der Blind-1-Klasse.
3. **Dokumentinterner Personen-Widerspruch (1)**: dieselbe Handlung TMB bzw.
   KOH zugeschrieben; beide Stellen wurden zitiert, „keine Widersprüche"
   publiziert (203-E002).
4. **Selbstauskunft (1)**: 209-E005 — die Skepsis-Regel griff nicht.

## Abgeleiteter Fix-Stack (Reihenfolge = erwarteter Ertrag)

1. **Zitat-Rettung** (Mojibake + Chunk-ID-Fallback) — holt 2 bereits erkannte
   Fehler zurück, verbessert zugleich die Evidenzqualität in Produktion.
2. **Arithmetik-Validator** — Umrechnungen, Summen-/Bilanzzeilen und
   „X von Y (Z %)"-Muster nachrechnen; 3 Misses, rein deterministisch.
3. **Reihenfolge-Validator** — typisierte Datumsrollen (Freigabe, Prüfung,
   Nutzung, Review) mit Ordnungsregeln; 2 Misses plus die Blind-1-Klasse.
4. **Library-Erweiterung** — `req_dev_timely_notification`; Scope von
   `req_qc_qa_approval_before_first_gmp_use` auf Herstellung/Change-Control.
   Längerfristig: dynamische Requirement-Aufnahme aus Paket-SOPs.
5. **Trunkierungs-Rest** — der werte-Pass eines tabellendichten Dokuments kann
   weiterhin am Output-Limit reißen; nächste Stufe wäre tabellenweise Batches.
