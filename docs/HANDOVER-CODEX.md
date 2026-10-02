# Übergabe an Codex — Stand 2026-10-02

Dieses Dokument übergibt die Arbeit am PharmaQRM-Delta-Tool. Es sagt, was das
Produkt kann, was gemessen ist (und wie ehrlich die jeweilige Zahl ist), wie
deployt wird, und welche Fäden offen sind. Die Arbeitsregeln stehen in
[`AGENTS.md`](../AGENTS.md); Engine-Details in [`backend/README.md`](../backend/README.md).

## Das Produkt in drei Sätzen

Ein QA-Reviewer lädt GMP-Unterlagen hoch (Abweichung, CAPA, Change Control)
und bekommt eine **Anforderungsabdeckung**: jede Anforderung des aktiven
Regelwerks genau einmal beantwortet — erfüllt, verletzt, unklar, nicht
anwendbar — jedes entschiedene Urteil mit wörtlichem, serverseitig geerdetem
Zitat samt Dateiname und Seite. Kernversprechen: **Das Ganze läuft auf einem
Modell unter Kundenkontrolle** (Qwen3.8-27B, heute Hetzner Inference in
Deutschland, Ziel: vLLM auf Kunden-Hardware). Die KI entscheidet nicht — hohe
und kritische Risiken werden nie automatisch geschlossen.

## Architektur: Evidence-first in drei Schichten

1. **Fakten** (`evidence_extraction.py`): Das Modell transkribiert Messwerte,
   Grenzwerte, Daten, Signaturfelder, Maßnahmen als typisierte Zeilen, jede
   mit Quellzitat. Nicht auffindbare Zitate ⇒ Zeile verworfen und gezählt.
2. **Regeln** (`deterministic_validators.py`): 12 deterministische Prüfungen
   (Wert gegen Grenze, Datumsfolge, Vier-Augen, CAPA ohne Wirksamkeitsprüfung,
   leere Pflichtfelder …), jede mit regulatorischer Grundlage. Ein Regelbefund
   hebt nur an, senkt nie.
3. **Urteil** (`requirement_review.py`): Das Modell beantwortet nur den Rest.
   Zwei Formen: `grouped` (6 Anforderungen/Aufruf — Frontier-Modelle) und
   `narrow` (pro Anforderung: erst Belege suchen, dann nur über diese Zitate
   urteilen — die Form, die ein 27B trägt). Danach: Entailment-Check +
   skeptische Zweitprüfung; Verifikation stuft nur herab.

Der Umbau von „ein großer Prompt“ auf diese Kette hat dieselbe Qwen-Instanz
von 32 % auf 92 % (Regression) gehoben — Architektur, kein Modellwechsel.

## Messstand (die wichtigste Tabelle)

| Lauf | Korpus | Ergebnis | Täuschstellen | Zitatpräzision |
|---|---|---|---|---|
| Qwen3.8 lokal, narrow | **Blindkorpus 3** (8 Fälle, nie gesehen) | **14/16** | 16/16 sauber | 82,7 % |
| Claude+GPT, narrow | **Blindkorpus 3** | **14/16** | 16/16 sauber | 97,2 % |
| Claude+GPT, grouped | Goldstandard (Regression) | 24/25 | 11/11 | 96,7 % |
| Qwen3.8 lokal, narrow | Goldstandard (Regression) | 23/25 | 11/11 | 92,5 % |

Beide Blind-Misses waren **Infrastruktur, nicht Erkennung**: Qwen verlor in
Fall 12 exakt die vier relevanten Belegsuche-Aufrufe in einem Hetzner-504-
Schub (Zeilen als `needs_retry` markiert — in der UI ein Klick „Erneut
prüfen“); der Mixed-Stack verlor Fall 18 ans erschöpfte Anthropic-Monatslimit.
Auf beantworteten Fällen: beide 14/14. Rohdaten: `goldstandard_pharmaqrm/runs/`,
sichtbar im Tool unter **Ringversuch**.

**Ehrlichkeitsregeln:** Goldstandard = Regressionskorpus (beim Bauen
angeschaut). `blind3` ist seit dem Lauf vom 24.08. verbraucht. Die nächste
Engine-Änderung, die Erkennungsqualität berühren kann, braucht **Blindkorpus 4**
(Spezifikation: `docs/blindkorpus-spezifikation.md`) — erst Engine einfrieren
und committen, dann messen.

## Betrieb

- **Server:** Hetzner 5.9.106.75 (SSH-Alias `labpulse-server`, Port 2222,
  root). Backend `/opt/qrm-delta`, Frontend `/opt/qrm-delta-frontend`, beide
  Checkouts auf dem Branch-Tip. Proxy: Container `voxdrop-nginx-1`
  (Vhost-Datei außerhalb des Repos, siehe `ops/HETZNER.md`).
- **Domains:** `qrm.labpulse.ai` (UI), `compliance.labpulse.ai` (API;
  `/health` zeigt `model_roles` — nach jedem Deploy prüfen).
- **Stack:** Produktion läuft mit `QRM_MODEL_STACK=local` über das Overlay
  `docker-compose.local-stack.yml` (alles Qwen, narrow). Runbook:
  `ops/LOCAL-STACK.md` (inkl. vLLM-Anleitung für Kunden-Hardware).
- **⚠️ Stand 2026-10-02:** Alle vier QRM-Container wurden am ~26.09. sauber
  gestoppt (`Exited (0)`) und laufen seitdem nicht; beide Domains antworten
  nicht. Neustart wäre:
  `cd /opt/qrm-delta && docker compose -f docker-compose.hetzner.yml -f docker-compose.local-stack.yml up -d`
  und `cd /opt/qrm-delta-frontend && ./ops/deploy-frontend-hetzner.sh`.
  Ob der Stopp Absicht war, weiß nur der Owner — vorher fragen.

## Git-Lage

- **Arbeits-/Deploy-Branch: `codex/pharmaqrm-production`.** `main` ist alt
  (18cdd2b) und wird nicht benutzt; ein Merge nach main ist eine
  Owner-Entscheidung.
- Der Commit `bd399a5` ist ein **rekonstruierter Snapshot**: iCloud hatte im
  August Objekte aus dem lokalen Repo evakuiert, 26 granulare Commits waren
  vorübergehend nicht pushbar und stecken in diesem einen Commit (alle
  Original-Messages im Commit-Text). Der Store ist inzwischen geheilt; die
  granulare Historie kann als Lese-Branch `history/qwen-rebuild-aug2026`
  veröffentlicht werden (gleicher Inhalt, echte Einzelschritte).
- Lokale Checkouts auf dem Mac des Owners haben teils andere SHAs bei
  identischem Inhalt (Folge der Rekonstruktion) — für Codex irrelevant, wenn
  von GitHub geklont wird.

## Offene Fäden (priorisiert)

1. **Produktion wieder hochfahren** (falls der Stopp nicht Absicht war) und
   `/health` → `stack: local` verifizieren.
2. **Assessor-Modi konsolidieren:** `narrow` hat blind für beide Stacks
   bewiesen, dass es trägt. Kandidat: `narrow` als einziger Pfad, `grouped`
   entfernen (Config, Engine, Tests, Doku) — reduziert die Engine deutlich.
   Danach Blindkorpus 4 messen.
3. **Präzision:** 9–16 „verletzt“-Zeilen pro Fall sind fachlich meist
   vertretbar (fehlende Nachweise SIND Lücken), aber viele Zeilen zitieren
   dieselbe Grundlücke. Ideen: Dedupe über Anforderungen hinweg,
   Schweregrad-Sortierung, „Hauptbefund + Folgebefunde“-Gruppierung. Jede
   Änderung hier = erkennungsrelevant ⇒ Blindkorpus-4-Regel.
4. **Befundweg (7 Fach-Reviewer) auf dem lokalen Stack ist unvermessen** und
   kostet ~10 min/Fall extra. Kandidat: im `local`-Preset abschaltbar machen
   oder ganz hinter die Anforderungsabdeckung zurückziehen.
5. **Fall-12/18-Nachmessung:** `--cases case_12` bzw. `case_18` mit
   `--cases-dir ../goldstandard_pharmaqrm/blind3` nachziehen (Anthropic-Limit
   ist seit 01.09. zurückgesetzt), Ergebnis als Anmerkung zum Run
   dokumentieren — nicht als neue Blindzahl verkaufen.
6. **Schlüsselhygiene:** Anthropic-, OpenAI- und Hetzner-Keys standen im
   August in Chat/Logs; falls noch nicht rotiert: rotieren. Mistral-Key
   widerrufen (Provider ist entfernt). Server-`.env` entsprechend
   aktualisieren.
7. **Grünewald-Zielbild:** vLLM auf Kunden-GPU nach `ops/LOCAL-STACK.md`
   Stufe 2; Abnahme = Ringversuch gegen den eigenen Endpunkt mit
   `QRM_HETZNER_ENDPOINT=…`.

## Was Codex ohne den Owner NICHT kann

- Produktions-Deploys und Server-Zugriff (SSH-Key liegt nur lokal beim Owner).
- Live-Evals (brauchen `HETZNER_API_KEY` bzw. Cloud-Keys — als Secrets in der
  Codex-Umgebung hinterlegen oder lokal via Codex CLI arbeiten).
- Merges nach `main`, Löschen/Umbenennen von Branches, Schlüsselrotation.

Alles andere — Engine, UI, Tests, Mock-Ringversuch — läuft ohne Secrets.
