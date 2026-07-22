# Pharma QRM: Minimale SaaS-Informationsarchitektur und Designsprache

Datum: 22.07.2026  
Status: Freigegebene Designrichtung

## Ziel

Pharma QRM soll für neue Besucher sofort verständlich und für QA-Prüfer effizient bedienbar sein.

Das Produkt trennt zwei Kontexte:

1. Öffentliche Produktvorstellung mit Demo und Nachweis.
2. Geschützter QA-Arbeitsbereich.

Die Oberfläche wirkt präzise, ruhig und modern. Derselbe Sachverhalt darf nicht über mehrere Routen, Karten, Labels oder konkurrierende Handlungsaufforderungen erklärt werden.

## Produktbegriffe

Die normale Oberfläche verwendet fünf Produktbegriffe:

- **Prüffall**: der zu bearbeitende Vorgang.
- **Befund**: eine erkannte Auffälligkeit.
- **Quelle**: der Beleg für einen Befund.
- **Entscheidung**: das Ergebnis der menschlichen Prüfung.
- **Prüfmappe**: das erzeugte Prüfergebnis.

Begriffe wie Pipeline, Agent, Orchestrierung, Modellposition, Coverage und Architektur erscheinen nicht im normalen Arbeitsablauf. Technische Begriffe sind ausschließlich in der Administration oder in detaillierten Audit-Metadaten zulässig.

## Informationsarchitektur

### Öffentlicher Bereich

```text
Start                    /
Demo                     /demo
Nachweis                 /nachweis
Anmelden                 /login
```

### Geschützter Arbeitsbereich

```text
Prüffälle                /app/faelle
Neuer Prüffall           /app/faelle/neu
Prüffall                 /app/faelle/:id
Regelwerk                /app/regelwerk
```

`Regelwerk` ist über das Profil- oder Administrationsmenü erreichbar und gehört nicht zur primären QA-Navigation.

## Navigation

### Öffentliche Navigation

```text
Pharma QRM        Demo    Nachweis             Anmelden
```

Das Logo führt zu `/`. Es gibt keine separaten Menüpunkte `Start` oder `Überblick`.

### Navigation im Arbeitsbereich

```text
Pharma QRM        Prüffälle                    + Neuer Fall    Profil
```

Solange der Arbeitsbereich nur einen primären Objekttyp besitzt, gibt es keine Sidebar. Administration und `Regelwerk` liegen im Profilmenü.

## Seitendesign

### Start `/`

Zweck: Das Produkt auf einen Blick vermitteln und einen klaren öffentlichen nächsten Schritt anbieten.

```text
GMP-Unterlagen prüfen.
Entscheidungen nachvollziehbar vorbereiten.

[Demo öffnen]  [Anmelden]
```

Unterhalb des Einstiegs stehen ausschließlich:

1. Eine große Produktansicht.
2. Eine Nachweiszeile: `24/25 Fehler erkannt`, `0 Fehlalarme`, `93 % belegt`.

Kein Feature-Raster, keine Prozesskarten, kein Architekturabschnitt und keine wiederholten Handlungsaufforderungen.

### Demo `/demo`

Zweck: Den Arbeitsablauf anhand eines realistischen Beispiels verständlich machen.

Alle drei Demofälle liegen auf einer Seite und werden über einen kompakten Fallumschalter gewählt. Der aktive Fall verwendet eine zweigeteilte Ansicht:

```text
┌──────────────────────┬─────────────────────────────┐
│ Befunde              │ Quelle                     │
│                      │                             │
│ Ausgewählter Befund  │ Originaltext               │
│ Weitere Befunde      │ Anforderung                │
│                      │ Fehlender Nachweis         │
│                      │                             │
│                      │ [Bestätigen] [Nachfordern] │
└──────────────────────┴─────────────────────────────┘
```

Die Aktionen heißen `Bestätigen`, `Nachfordern` und `Eskalieren`. Eine Demoentscheidung bleibt ausdrücklich ein nicht auditierbarer Browserzustand.

### Nachweis `/nachweis`

Zweck: Gemessene Leistung und ihre Grenzen ohne Marketingnarrativ zeigen.

Die Seite enthält:

1. Drei primäre Kennzahlen.
2. Die Laufhistorie.
3. Einen kurzen Hinweis, dass synthetische Fälle keine Leistung auf Kundendokumenten belegen.

Ringversuch und Systemmethode sind Abschnitte dieser Seite. Es gibt keine separate öffentliche Architekturseite.

### Prüffälle `/app/faelle`

Zweck: Einen echten Fall finden und öffnen.

Die Seite enthält eine Überschrift, die Aktion `+ Neuer Fall`, ein Suchfeld und eine Tabelle:

```text
Fall              Typ          Status              Aktualisiert
DEV-2025-014      Abweichung    Entscheidung offen  heute
CAPA-2025-082     CAPA          Nachweis fehlt      gestern
CC-2025-211       Change        Bereit              18.07.
```

Oberhalb oder unterhalb der Fallliste stehen weder Dashboard-Kennzahlen noch Kalibrierungsfunktionen.

### Neuer Prüffall `/app/faelle/neu`

Zweck: Einen Prüffall anlegen und starten.

Die Seite enthält ausschließlich:

```text
Anlass
Bereich
Dokumente

                                      [Analyse starten]
```

Validierung erscheint direkt am betroffenen Feld. Der Analysefortschritt erscheint erst nach dem Absenden.

### Prüffall `/app/faelle/:id`

Zweck: Befunde prüfen, Quellen verifizieren, die menschliche Entscheidung dokumentieren und die Prüfmappe exportieren.

Die Ansicht verwendet dasselbe zweigeteilte Interaktionsmodell wie die Demo:

- Links: Befunde und Status.
- Rechts: Quelle, Anforderung, fehlender Nachweis und Entscheidung.
- Im Kopf: Fallidentität und Gesamtstatus.
- Abschließende Aktion: `Prüfmappe exportieren`.

Befunddetails und Inhalte der Prüfmappe bleiben für Audit-Deep-Links adressierbar, sind aber keine eigenständigen Navigationsziele.

### Regelwerk `/app/regelwerk`

Zweck: Das aktive Regelwerk verwalten.

Aktive Anforderungen stehen zuerst. Daneben gibt es eine nachrangige Importaktion. Kalibrierung und technische Providerdetails gehören in die Administration, nicht auf diese Seite.

## Visuelles System

Richtung: Präzision im Stil moderner Linear-/Vercel-Produkte, ohne eines der Produkte zu kopieren.

- Schrift: Geist Sans.
- Maximale Inhaltsbreite: 1120 px.
- Höhe der Navigation: 56 px.
- Grundfläche: Weiß oder nahezu Weiß.
- Primärtext: nahezu Schwarz.
- Sekundärtext: neutrales Grau.
- Akzent: ein klares Blau.
- Linien: 1 px, neutrales Grau.
- Ecken: 6-8 px.
- Schatten: ausschließlich für Dialoge und temporäre Ebenen.
- Bewegung: maximal 150 ms und nur bei Zustandswechseln.
- Statusfarben: ausschließlich für Erfolg, Warnung und Blockierung.

Keine Verläufe, dekorativen Illustrationen, verschachtelten Karten, großen Icon-Sammlungen oder Pill-Badges für gewöhnliche Metadaten.

## Layoutregeln

- Eine H1 pro Seite.
- Eine Primäraktion pro Seite.
- Weißraum, Ausrichtung und Typografie vor zusätzlichen Containern einsetzen.
- Karten nur für eigenständige Objekte verwenden.
- Listen als Zeilen mit Trennlinien darstellen.
- Erklärungstext auf einen kurzen Satz unter der Überschrift begrenzen.
- Dieselbe Anleitung nicht in Hero, Karten, Bannern und Leerzuständen wiederholen.
- Demo und Arbeitsbereich verwenden dasselbe Interaktionsmodell für Prüffälle.

## Responsives Verhalten

- Desktop: zweigeteilte Fallprüfung.
- Mobil: eine Spalte; zuerst der Befund, direkt darunter Quelle und Entscheidung.
- Öffentliche und interne Navigation klappen in ein kompaktes Menü ein, ohne ihre Begriffe zu ändern.
- Tabellen werden auf kleinen Bildschirmen zu kompakten Fallzeilen, nicht zu einer Sammlung fachfremder Dashboard-Karten.

## Barrierefreiheit

- Tastaturfokus bleibt deutlich sichtbar.
- Überschriften und Seitenbereiche verwenden semantische Elemente.
- Entscheidungselemente bilden ihren Auswahlzustand über `aria-pressed` oder native Formularsemantik ab.
- Status wird nie allein durch Farbe vermittelt.
- Fließtext ist mindestens 14 px groß und besitzt eine lesbare Zeilenhöhe.
- Reduzierte Bewegungseinstellungen werden berücksichtigt.

## Zusammenführung der Routen

| Bestehende Route | Ziel |
| --- | --- |
| `/ueberblick` | `/` |
| `/` mit Dashboard und Upload | Öffentliche Startseite plus `/app/faelle/neu` |
| `/prueffaelle` | `/app/faelle` |
| `/review-ui` | `/app/faelle` |
| `/review-ui/demo/:id` | `/demo` mit ausgewähltem Fall |
| `/ringversuch` | `/nachweis` |
| `/ai-architecture` | Methodenabschnitt auf `/nachweis` |
| `/risk-library` | `/app/regelwerk` |

Alte URLs leiten auf ihre Zielroute weiter. Bestehende Deep Links für Befunde und Prüfmappe dürfen als interne Routen erhalten bleiben.

## Nicht-Ziele

- Kein Umbau des Backends oder der Modellpipeline.
- Keine Änderung an der Fail-closed-Regel für menschliche Prüfung.
- Kein neues Dashboard, Analytics-Modul oder Kollaborationsfeature.
- Keine öffentliche Freigabe geschützter Fälle oder Backenddaten.
- Kein Verlust adressierbarer Audit-Deep-Links.

## Abnahmekriterien

Das Redesign ist erfolgreich, wenn:

1. Ein neuer Besucher das Produkt erkennt, die Demo öffnet und den Nachweis über die öffentliche Navigation erreicht.
2. Ein angemeldeter QA-Nutzer direkt die Fallliste erreicht und über eine Primäraktion einen Fall startet.
3. Keine Primärnavigation gleichzeitig `Start` und `Überblick` oder `Prüffälle` und `Review UI` enthält.
4. Demo und echte Fallprüfung dieselbe Informationshierarchie verwenden.
5. Die Fallliste keine fachfremden Kalibrierungs- oder Dashboardinhalte enthält.
6. Die öffentliche Produktgeschichte nicht mehr als die vier definierten Routen benötigt.
7. Der normale Arbeitsablauf ausschließlich die fünf definierten Produktbegriffe verwendet.
8. Bestehende Authentifizierung, Mandantentrennung, Reviewentscheidungen, Exporte und Audit-Deep-Links weiterhin funktionieren.

