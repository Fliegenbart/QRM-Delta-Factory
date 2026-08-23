# Lokaler Modell-Stack: Qwen statt Cloud

Ziel: Das Tool prüft vollständig mit einem Modell, das unter eigener Kontrolle
läuft. Kein Dokument geht an Anthropic oder OpenAI. Zwei Ausbaustufen:

| Stufe | Wo rechnet das Modell | Was verlässt das Haus |
|---|---|---|
| **EU-Hosting** (heute) | Hetzner Inference API, Rechenzentrum in Deutschland | Dokumenttext an Hetzner (Auftragsverarbeitung) |
| **Eigene Hardware** (Ziel) | vLLM auf einem GPU-Server des Kunden | nichts |

Beide Stufen benutzen denselben Provider (`hetzner`), dieselben Prompts und
dieselbe Engine — nur die URL unterscheidet sich. Ein Ergebnis, das auf Stufe 1
gemessen wurde, gilt deshalb mit demselben Modell auch auf Stufe 2.

## Die eine Einstellung

```
QRM_MODEL_STACK=local
```

Das Preset setzt alle Rollen auf den lokalen Endpunkt und schaltet den
Assessor auf den **narrow**-Modus (pro Anforderung erst Belege suchen, dann
über die Belege urteilen). Das ist die Form, die ein 27B-Modell trägt: dieselbe
Qwen-Instanz lag im gruppierten Cloud-Modus bei 32 % Erkennungsrate und im
narrow-Modus bei 88 % (22/25, Goldstandard-Korpus, 2026-08-23 — Regression,
nicht blind; die Blindkorpus-3-Zahlen folgen).

Presets (`backend/app/core/config.py`, `MODEL_STACK_PRESETS`):

| Preset | liest Dokumente | prüft Urteile nach | Kritiker | Assessor |
|---|---|---|---|---|
| `cloud` | Claude + GPT (Rollen verteilt) | GPT | beide | grouped |
| `local` | lokal | lokal | lokal | narrow |
| `cascade` | lokal | Claude (nur Zitat + Begründung, nie das Dokument) | lokal | narrow |

Jede einzelne `QRM_*`-Variable gewinnt gegen ihr Preset. Wer `local` fährt,
aber die Nachprüfung bei Anthropic haben will, setzt zusätzlich
`QRM_REQUIREMENT_REVIEW_ENTAILMENT_PROVIDER=anthropic` — oder nimmt gleich
`cascade`.

`GET /health` zeigt, was tatsächlich läuft:

```json
"model_roles": {
  "stack": "local",
  "finding_reviewers": "hetzner",
  "requirement_assessor": "hetzner",
  "requirement_assessor_mode": "narrow",
  "entailment_checker": "hetzner",
  "critics": "hetzner"
}
```

Steht dort etwas anderes als erwartet, ist der Stack falsch konfiguriert —
**vor** dem ersten Kundendokument prüfen.

## Stufe 1: Hetzner Inference

`.env` auf dem Server (nie committen):

```
POSTGRES_PASSWORD=<openssl rand -hex 24>
QRM_API_KEYS=tenant_<kunde>=<openssl rand -hex 24>
HETZNER_API_KEY=<Schlüssel aus der Hetzner-Konsole>
```

Start mit dem Overlay:

```bash
cd /opt/qrm-delta
docker compose -f docker-compose.hetzner.yml -f docker-compose.local-stack.yml up -d --build
curl -s http://172.17.0.1:8100/health | python3 -m json.tool
```

Die Anthropic- und OpenAI-Schlüssel dürfen in der `.env` fehlen; der Overlay
macht sie optional. Steht der Hetzner-Schlüssel irgendwo im Klartext (Chat,
Ticket, Log): rotieren.

Was Hetzner Inference im August 2026 gezeigt hat:

- 13–23 Token/s pro Anfrage. Ein Prüffall mit 26 Anforderungen dauert im
  narrow-Modus 20–30 Minuten (Suchen + Urteilen + Nachprüfung, zwei parallele
  Aufrufe). Deshalb `QRM_PIPELINE_RUN_LEASE_SECONDS=3600`.
- An einem Nachmittag 68 upstream 5xx (503/504). Die Engine verkraftet das
  (Retry, Circuit-Breaker, Regelbefunde ohne Modell), aber mehr als zwei
  parallele Aufrufe provozieren es. `QRM_MODEL_PROVIDER_MAX_CONCURRENCY=2`
  lassen.
- Öffnet ein Breaker, steht es im Log (`ERROR qrm.providers`) und geht an
  `QRM_ALERT_WEBHOOK_URL`, wenn gesetzt.
- Stirbt ein einzelner Modellaufruf, bleibt die betroffene Anforderung als
  Platzhalter („Beurteilung fehlgeschlagen“, `needs_retry`) im Bericht. Der
  Bericht bietet **Erneut prüfen** an: Nur diese Zeilen werden neu beurteilt,
  alles andere bleibt stehen — zwei Minuten statt eines neuen 25-Minuten-Laufs.
- Während eines Laufs zeigt der Prüffall, wo er steht: Schritt x von 13 und
  „Anforderung 12 von 26 beurteilt“ (Polling alle 5 Sekunden).

## Stufe 2: Eigener GPU-Server (vLLM)

Der Provider spricht das OpenAI-Chat-Completions-Format mit zwei Besonderheiten,
die vLLM beide unterstützt: `response_format: {type: json_schema, strict: true}`
(Schema wird beim Dekodieren erzwungen) und
`chat_template_kwargs: {enable_thinking: false}` (sonst verbraucht Qwen das
gesamte Ausgabebudget im Denkteil und liefert leeren Inhalt).

### Hardware

| Variante | Speicherbedarf Gewichte | Karten |
|---|---|---|
| bf16 | ~54 GB + KV-Cache | 1× H100/H200 80 GB, oder 2× 48 GB (L40S, RTX 6000 Ada) mit `--tensor-parallel-size 2` |
| FP8 | ~27 GB + KV-Cache | 1× 48-GB-Karte |

Der KV-Cache für 32k Kontext bei zwei parallelen Anfragen braucht
zusätzlich zweistellige GB; lieber eine Karte mehr als eine zu wenig.
Durchsatz auf eigener Hardware vor dem Go-live messen — die Hetzner-Zahlen
oben sind eine Untergrenze, keine Prognose.

### Serverstart

```bash
vllm serve <HF-Repo des Modells, z. B. Qwen/Qwen3.8-27B> \
  --host 0.0.0.0 --port 8000 \
  --api-key "$LOCAL_INFERENCE_KEY" \
  --max-model-len 32768 \
  --reasoning-parser qwen3 \
  --served-model-name Qwen3.8-27B
```

`--served-model-name` sorgt dafür, dass `QRM_HETZNER_MODEL_ID=Qwen3.8-27B`
unverändert weiterverwendet werden kann. Die genaue HF-Repo-Kennung und die
vLLM-Version vor dem Aufsetzen prüfen; die Flags oben sind der Stand von 2026.

### Rauchtest vor dem ersten Prüffall

```bash
curl -s http://gpu-01.intern:8000/v1/chat/completions \
  -H "Authorization: Bearer $LOCAL_INFERENCE_KEY" -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.8-27B", "temperature": 0, "max_tokens": 200,
    "chat_template_kwargs": {"enable_thinking": false},
    "response_format": {"type": "json_schema", "json_schema": {"name": "t", "strict": true,
      "schema": {"type": "object", "properties": {"quote": {"type": "string"}}, "required": ["quote"], "additionalProperties": false}}},
    "messages": [{"role": "user", "content": "Zitiere wörtlich: Die Prüfung wurde am 12.03.2026 durchgeführt."}]
  }'
```

Erwartet: `content` ist `{"quote": "Die Prüfung wurde am 12.03.2026 durchgeführt."}`,
`finish_reason` ist `stop`, Umlaute intakt. Liefert der Server `reasoning_content`
statt `content`, greift `enable_thinking` nicht — das Chat-Template des
Modells prüfen.

### Umschalten

In der `.env`:

```
QRM_HETZNER_ENDPOINT=http://gpu-01.intern:8000/v1/chat/completions
HETZNER_API_KEY=<LOCAL_INFERENCE_KEY>
QRM_MODEL_PROVIDER_MAX_CONCURRENCY=4
```

dann `docker compose ... up -d`. Der Variablenname bleibt `HETZNER_*`, weil der
Provider derselbe ist; nur die URL wandert.

## Abnahme: Ringversuch gegen den eigenen Endpunkt

Bevor ein Kunde den lokalen Stack benutzt, muss er dieselbe Messung bestehen
wie die Cloud — derselbe Korpus, dieselbe Engine, dasselbe Preset:

```bash
cd backend
QRM_HETZNER_ENDPOINT=http://gpu-01.intern:8000/v1/chat/completions \
./.venv/bin/python -m app.evals.run_goldstandard --mode live --engine requirement \
  --stack hetzner --cases-dir ../goldstandard_pharmaqrm/blind3 --pipeline-timeout-seconds 2400
```

`--stack hetzner` ist das Preset `local`; `hetzner-cascade` ist `cascade`. Das
Ergebnis landet unter `goldstandard_pharmaqrm/runs/…_live_hetzner_narrow_requirement`
und erscheint im Tool unter **Ringversuch**. Maßstab ist die Cloud-Zahl auf
demselben Korpus, nicht ein absoluter Wert.

## Was der lokale Stack (noch) nicht hat

- Keine zweite Modellfamilie als Gegenprüfer. Der Entailment-Check läuft
  auf demselben Modell, das geurteilt hat; er fängt Zitatfehler, aber keine
  gemeinsamen blinden Flecken. Wer das braucht, fährt `cascade`.
- Die deterministischen Regeln (Rechenprüfung, Datumsfolge, Vier-Augen,
  Wirksamkeitsprüfung, leere Pflichtfelder) laufen in jedem Stack gleich —
  sie brauchen kein Modell, nur die extrahierten Fakten.
