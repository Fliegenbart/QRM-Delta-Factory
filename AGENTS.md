# PharmaQRM Delta — Agent-Anweisungen

GMP-Dokumentenprüfung für Pharma-QA: Aus hochgeladenen Unterlagen (Abweichung,
CAPA, Change Control) wird eine belegte Prüfmappe plus eine
**Anforderungsabdeckung** — ein Urteil pro Anforderung des aktiven Regelwerks
(erfüllt / verletzt / unklar / nicht anwendbar), jedes mit wörtlich gegen den
Quelltext geerdetem Zitat. Die KI bereitet vor; freigeben darf nur ein Mensch.

Vollständige Übergabe mit Stand, Messwerten und offenen Fäden:
**`docs/HANDOVER-CODEX.md`** — zuerst lesen.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `backend/app/services/requirement_review.py` | Kern-Engine: narrow/grouped Assessor, Entailment, Challenge, `rerun_failed` |
| `backend/app/services/evidence_extraction.py` | Fakten-Extraktion (Messwerte, Grenzen, Daten, Signaturen) mit Zitat-Grounding |
| `backend/app/services/deterministic_validators.py` | 12 Regeln, die ohne Modell entscheiden; Katalog via `GET /validators` |
| `backend/app/services/pipeline.py` | 13-Schritte-Pipeline, Fortschritt via `app/services/progress.py` |
| `backend/app/agents/providers/` | Anthropic/OpenAI/Hetzner-Adapter: Breaker, Retry, Hard-Deadline, String-Decode |
| `backend/app/core/config.py` | `MODEL_STACK_PRESETS` (`cloud`/`local`/`cascade`), alle `QRM_*`-Variablen |
| `backend/app/evals/run_goldstandard.py` | Ringversuch-Harness (`--stack`, `--assessor-mode`, `--cases-dir`) |
| `goldstandard_pharmaqrm/` | Korpora: `case_01–10` (Regression), `blind3/` (verbraucht), `runs/` (Ergebnisse) |
| `app/` + `src/` | Next.js 15 App Router; Review-UI unter `app/review-ui/`, Server-Proxys unter `app/api/review-ui/` |
| `ops/LOCAL-STACK.md`, `ops/HETZNER.md` | Deploy-Runbooks (Server, Compose, vLLM) |
| `backend/README.md` | Engine- und Stack-Dokumentation (Abschnitte „Requirement Coverage Review“, „Model Stacks“) |

## Befehle

```bash
# Backend (Python ≥ 3.12)
cd backend && python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m pytest                      # muss grün sein (≈444 Tests)

# Frontend (Node ≥ 20)
npm ci
npx vitest run                                    # ≈82 Tests
npx tsc --noEmit -p . && npx next build           # Build-Gate

# Engine end-to-end ohne API-Schlüssel (Mock-Provider):
cd backend && ./.venv/bin/python -m app.evals.run_goldstandard --mode mock --engine requirement
```

Dev-Server: `npm run dev` (Frontend) + `cd backend && ./.venv/bin/python -m uvicorn app.main:app --port 8000`.
Frontend→Backend via `QRM_BACKEND_URL` (Default `http://localhost:8000`).

## Eiserne Regeln

1. **Messdisziplin.** Es gibt Regressionskorpora (angeschaut beim Bauen) und
   Blindkorpora (nie angeschaut). Eine Zahl heißt nur dann „blind“, wenn die
   Engine vor dem Lauf eingefroren und committed war und niemand beim Bauen auf
   die Fälle geschaut hat. `blind3` ist seit 2026-08-24 verbraucht (= jetzt
   Regression). Vor dem nächsten Engine-Tuning: neuen Blindkorpus nach
   `docs/blindkorpus-spezifikation.md` bauen, Tuning abschließen, committen,
   DANN messen. Niemals auf einem Blindkorpus nachtunen und ihn weiter „blind“
   nennen.
2. **Fail-secure ist unverhandelbar.** Verifikation stuft Urteile nur herab,
   nie herauf. Ein Regelbefund hebt auf „verletzt“, senkt nie. Ein Urteil ohne
   geerdetes Zitat wird „unklar“ publiziert. Tote Modellaufrufe werden als
   `needs_retry`-Platzhalter sichtbar, nie als sauberes Ergebnis.
3. **Zitat-Grounding ist heilig.** Jedes publizierte Zitat muss Zeichen für
   Zeichen in den gespeicherten Chunks stehen (`_check_provenance` /
   `_ground_quote`). Nichts daran „lockern“, um Zahlen zu verbessern.
4. **Keine Geheimnisse ins Repo.** API-Schlüssel nur in `.env` (gitignored)
   bzw. Server-`.env`. Auch nicht in Testfixtures, Logs oder Commit-Messages.
5. **Beide Suiten + tsc + next build grün vor jedem Push.** Der Ringversuch im
   Mock-Modus muss durchlaufen, wenn die Engine angefasst wurde.
6. **Produktsprache ist Deutsch** (UI-Texte, Prüfberichte, Fehlermeldungen für
   Reviewer). Code, Kommentare und Commit-Messages: Englisch.
7. **Branch:** Gearbeitet wird auf `codex/pharmaqrm-production` (das ist die
   deployte Linie). `main` ist veraltet (Stand 18cdd2b) — nicht darauf mergen,
   ohne dass der Owner das entscheidet.

## Modell-Stacks (eine Variable)

`QRM_MODEL_STACK=cloud|local|cascade` setzt alle Rollen konsistent; explizite
`QRM_*`-Variablen gewinnen gegen das Preset. `local` = alles auf dem
OpenAI-kompatiblen `hetzner`-Provider (Hetzner Inference heute, eigener
vLLM-Server via `QRM_HETZNER_ENDPOINT` morgen) im **narrow**-Assessor-Modus.
`GET /health` → `model_roles` zeigt, was wirklich läuft.

Hetzner/Qwen-Eigenheiten (gemessen, nicht vermutet): `chat_template_kwargs:
{enable_thinking: false}` ist Pflicht (sonst leere Antworten), 13–23 Token/s,
Parallelität ≤ 2 (sonst 503/504), Hard-Deadline im Adapter gegen tröpfelnde
Verbindungen. Ein Prüffall dauert auf dem lokalen Stack 20–30 Minuten.
