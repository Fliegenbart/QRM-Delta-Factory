# Spezifikation Blindkorpus-1 („PharmaQRM Blind Evaluation Set")

## Zweck und Rollentrennung

Dieses Dokument ist der vollständige Arbeitsauftrag für die **Generierung** eines
Blindkorpus zur Bewertung eines automatisierten GMP-Review-Systems. Es ist als
Prompt für eine frische Session gedacht, die **keinen Zugriff auf bestehende
Testfälle, Systemcode oder frühere Auswertungen** hat und auch nicht danach
suchen soll. Genau diese Unkenntnis ist der Wert des Korpus: Das zu testende
System wurde auf früheren Fällen nachjustiert; nur ein von einer unbeteiligten
Instanz gebauter Korpus misst noch etwas.

Regeln für die generierende Session:

- Lies **keine** vorhandenen Ordner mit Testfällen, Lösungsschlüsseln oder
  Auswertungen. Alles Nötige steht hier.
- Erfinde sämtliche Firmen-, Produkt-, Personen- und Chargenbezeichnungen neu.
  Keine realen Firmen, keine realen Personen.
- Nach der Generierung: Ausgabeordner benennen, fertig. Keine Selbstauswertung,
  keine Zusammenfassung der versteckten Fehler im Chat (die stünde sonst im
  Kontextfenster späterer Arbeiten).

## Lieferumfang

Zielordner: `/Users/davidwegener/Desktop/Apps/Grünewald-Tool/Blindkorpus-1/`

```
Blindkorpus-1/
  case_01/ … case_10/
    case_summary.md
    document_01_<slug>.md
    document_02_<slug>.md
    …
    hidden_errors_answer_key.json
  README.md          (Kurzbeschreibung, Nutzungshinweis, Warnung vor dem Schlüssel)
```

10 Fälle, je **4–6 Dokumente** (Markdown), je **3–5 versteckte Fehler** und je
**mindestens 3 Decoys**. Sprache: Deutsch mit korrekten Umlauten (ä, ö, ü, ß —
niemals ae/oe/ue/ss als Ersatz). Wörtliche englische Einsprengsel (Systemmeldungen,
Statusfelder wie „pending", Software-Labels) sind realistisch und erlaubt.

## Fachlicher Rahmen (verbindlich)

Jeder Fall ist eine **Abweichungs-Fallmappe aus der Arzneimittelherstellung**
(Deviation im Bereich Drug Product Manufacturing). Typischer Dokumentsatz:

- Abweichungsbericht (Deviation Report) mit Klassifizierung und Root Cause
- Auszug aus dem Batch Manufacturing Record (Prozessparameter-Tabellen,
  Signaturfelder, Materialeinträge)
- CAPA-Plan mit Maßnahmenliste, Verantwortlichen, Terminen, Wirksamkeitsprüfung
- QA-Bewertung / Freigabevermerk
- optional: SOP-Auszug, Prüfprotokoll, Trendbericht, Lieferantenzertifikat,
  Schulungsnachweis, Change-Control-Auszug

Die versteckten Fehler müssen Pflichten aus dem **allgemeinen GMP-Kanon**
verletzen — Signaturen und Datumsangaben, Audit-Trail-Nachweise, Chargen-Impact,
CAPA-Vollständigkeit (Verantwortliche, Termine, Wirksamkeit), Schulung vor
Anwendung, Spezifikationsgrenzen, Freigabe vor Nutzung,
Dokumentenquerkonsistenz. Keine exotischen Spezialregularien, deren Kenntnis
man dem System nicht unterstellen kann.

## Pflicht-Fehlerklassen

Über den Korpus verteilt (nicht jede Klasse in jedem Fall) müssen vorkommen:

1. **Neue Zahlenbereiche und Einheiten.** Grenzwertverletzungen mit frei
   erfundenen, in sich stimmigen Spezifikationen. Bewusst gemischte Darstellungen:
   mg/ml neben %, Temperatur in °C mit Komma- und Punktschreibweise, „NLT/NMT",
   „≤", ausgeschriebene Bereiche. Mindestens ein Fall, in dem Wert und Grenze in
   **verschiedenen Dokumenten** stehen.
2. **Subtile leere Pflichtfelder.** Ein Signatur- oder Pflichtfeld, das leer,
   nur mit Datum ohne Namen, oder mit „siehe oben" gefüllt ist — eingebettet in
   einen ansonsten vollständig ausgefüllten Block. Mindestens einmal: eine von
   mehreren gleichartigen Positionen betroffen (z. B. Maßnahme 3 von 4 ohne
   Verantwortlichen), während die übrigen korrekt sind.
3. **Selbstauskunft ohne Primärevidenz.** Ein Dokument behauptet die Durchführung
   einer Tätigkeit („Review durchgeführt, keine Auffälligkeiten"), ohne dass
   irgendein referenzierbarer Nachweis (Auszug, Checkliste, Rohdaten, signiertes
   Protokoll) im Paket existiert.
4. **Widersprüchliche Initialen, Personen oder Zeitstempel.** Dieselbe Handlung
   von verschiedenen Kürzeln gezeichnet, ein Review vor dem Ereignis datiert,
   das es prüft, oder identische Uhrzeiten für unvereinbare Ereignisse — stets
   über mindestens zwei Stellen verteilt.
5. **Mindestens 4 Fehler eines Typs, der oben nicht aufgezählt ist.** Freie
   Wahl, z. B.: falsche Querverweis-Nummern, Einheitenfehler in einer Umrechnung,
   eine Charge im Verteiler vergessen, Widerspruch zwischen Zusammenfassung und
   Tabelle, überschrittene Meldefrist. Kreativität ausdrücklich erwünscht — diese
   Position misst, was das System bei *unerwarteten* Fehlerarten leistet.

Schwierigkeitsstaffelung wie üblich: Fälle 1–3 mit dokumentlokalen Fehlern,
4–7 mit Zwei-Dokument-Abgleich, 8–10 mit Mehrfachverknüpfung.

## Pflicht-Decoys (pro Fall mindestens 3, davon:)

1. **Mindestens 1 legitime Selbstauskunft.** Eine Anforderung, deren Gegenstand
   die *dokumentierte Erklärung selbst* ist (z. B. eine signierte
   QA-Freigabeerklärung, eine dokumentierte Risikoakzeptanz mit Begründung) —
   vollständig, signiert, datiert. **Das ist kein Fehler.** Ein übervorsichtiges
   System, das hier „unklar" meldet, soll dafür messbar bestraft werden.
2. **Mindestens 1 auffällige, aber begründete Abweichung** — z. B. ein Wert nahe
   der Grenze mit dokumentierter, plausibler Bewertung; eine Nachtrags-Signatur
   mit korrektem Begründungsvermerk.
3. **Mindestens 1 „riecht nach Fehlerklasse, ist aber sauber"** — z. B. zwei
   verschiedene Initialen, die laut Unterschriftenliste schlicht zwei
   verschiedene berechtigte Personen sind; eine scheinbar fehlende Angabe, die
   in einem anderen Dokument regulär steht.

## Lösungsschlüssel: exaktes Format

Pro Fall `hidden_errors_answer_key.json`:

```json
{
  "case_id": "case_01",
  "fall_id": "PQRM-BLIND-001",
  "difficulty": "easy | medium | hard",
  "hidden_errors": [
    {
      "case_id": "case_01",
      "document_name": "document_01_deviation_report.md",
      "error_id": "BLIND01-E001",
      "error_type": "kurze Klassifikation",
      "severity": "critical | high | medium | low",
      "exact_evidence_text": [
        { "document_name": "document_01_deviation_report.md",
          "text": "WÖRTLICHES Zitat aus dem Dokument" }
      ],
      "why_it_is_a_problem": "fachliche Begründung",
      "expected_reviewer_finding": "der Satz, den ein Prüfer schreiben würde",
      "expected_action": "erwartete Maßnahme",
      "whether_error_is_direct_or_requires_cross_document_comparison": "direct | cross_document"
    }
  ],
  "non_error_decoys": [
    {
      "decoy_id": "BLIND01-D001",
      "document_name": "document_02_….md",
      "exact_evidence_text": [
        { "document_name": "document_02_….md", "text": "WÖRTLICHES Zitat" }
      ],
      "why_not_an_error": "Begründung, warum das korrekt/akzeptabel ist"
    }
  ]
}
```

**Kritische Formatregeln** (die Auswertung hängt daran):

- Jeder `text` in `exact_evidence_text` muss **zeichengenau als
  zusammenhängender Substring** im genannten Dokument stehen (Markdown-Fettung
  `**…**` darf Teil des Zitats sein). Kein Paraphrasieren. Nach dem Schreiben
  jedes Falls: jeden Zitat-String programmatisch gegen die Dokumentdatei prüfen.
- Jeder Fehler braucht mindestens ein Zitat; bei `cross_document` je ein Zitat
  aus jedem beteiligten Dokument.
- Jeder Fall braucht mindestens 1 versteckten Fehler (die Auswertung verweigert
  leere Schlüssel). Fälle mit nur 1 leichten Fehler und vielen Decoys sind
  ausdrücklich erwünscht, um Übervorsicht zu messen.
- `severity` ehrlich vergeben — sie wird gegen die Systemeinstufung verglichen.

## Qualitätssicherung vor Abgabe

1. Skriptgestützte Prüfung: alle Zitate substring-exakt, JSON valide, jede
   Datei UTF-8, keine ae/oe/ue/ss-Ersatzschreibungen in deutschem Fließtext.
2. Selbsttest der Plausibilität: Ein Fachfremder darf die Fehler beim ersten
   Lesen **nicht** sofort sehen; ein QA-Profi soll sie beim gründlichen Abgleich
   finden können. Fehler, die im Dokument durch Formulierung „markiert" sind
   („auffälligerweise fehlt…"), sind wertlos — streichen und neutral einbetten.
3. Die Dokumente müssen auch **ohne** Kenntnis des Schlüssels als stimmige,
   professionelle GMP-Dokumente lesbar sein.

## Nutzungsregeln nach der Generierung (für das Projektteam)

- Der Korpus wird **einmal** pro Systemvariante blind ausgewertet. Zwischen
  erster Sichtung und erstem Lauf keine Systemänderungen.
- Nach der ersten gezielten Fehleranalyse auf diesem Korpus wechselt er seinen
  Status von „Blindkorpus" zu „Regressionskorpus" und wird im Reporting nicht
  mehr als unabhängige Validierung geführt.
- Lösungsschlüssel niemals als Systeminput verwenden.
