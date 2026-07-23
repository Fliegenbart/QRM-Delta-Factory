# Betrieb auf dem Hetzner-Server (5.9.106.75)

Das QRM-Backend läuft als isoliertes Docker-Compose-Projekt unter `/opt/qrm-delta`,
erreichbar über `https://compliance.labpulse.ai` (zentraler Proxy: Container
`voxdrop-nginx-1`). Das Vercel-Frontend spricht das Backend über
`QRM_BACKEND_URL` an; der Browser sieht den API-Key nie.

```
Vercel (Next.js)  ──HTTPS──▶  compliance.labpulse.ai (voxdrop-nginx-1)
                                  │  proxy_pass http://172.17.0.1:8100
                                  ▼
                      /opt/qrm-delta  (eigenes Compose-Projekt)
                      app (FastAPI) ── postgres:16 (nur intern) ── redis
```

## Architektur-Entscheidungen

- **Port 8100 auf 172.17.0.1**: 8000/8080 sind auf dem Host belegt (Virusradar,
  Belegsync). Bindung an die Docker-Bridge, damit nur der Proxy-Container den
  Dienst erreicht — nicht das öffentliche Internet.
- **Eigene Postgres-Instanz** statt Mitnutzung anderer Projekte: saubere
  Isolation, eigenes Backup, kein Risiko für VoxDrop/ViralFlux.
- **Persistenz aktiv** (`QRM_PERSISTENCE_ENABLED=true`): Review-Entscheidungen,
  Findings und Audit-Trail überleben Neustarts (PersistentSnapshotRepository).
- **Vhost-Datei außerhalb des VoxDrop-Repos**: Die zentrale nginx.conf wird vom
  VoxDrop-Deployment verwaltet. Unser Vhost liegt deshalb unter
  `/etc/letsencrypt/vhosts.d/compliance.labpulse.ai.conf` (im Proxy-Container
  als `/etc/nginx/ssl/vhosts.d/` gemountet); in der nginx.conf steht nur eine
  Include-Zeile. **Wichtig:** Diese Include-Zeile gehört dauerhaft in das
  VoxDrop-Repo (`deploy/nginx.conf`), sonst entfernt sie das nächste
  VoxDrop-Deployment — siehe unten.

## Erstinstallation (bereits erfolgt)

```bash
git clone https://github.com/Fliegenbart/QRM-Delta-Factory.git /opt/qrm-delta
cd /opt/qrm-delta
# .env anlegen (siehe unten), dann:
docker compose -f docker-compose.hetzner.yml up -d --build
```

`.env` (niemals committen) — Werte im Passwortmanager:

```
POSTGRES_PASSWORD=<openssl rand -hex 24>
QRM_API_KEYS=tenant_gruenewald=<openssl rand -hex 24>
MISTRAL_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

## Wiederkehrende Handgriffe

| Aufgabe | Befehl |
|---|---|
| Status | `cd /opt/qrm-delta && docker compose -f docker-compose.hetzner.yml ps` (App muss `healthy` sein) |
| Logs | `docker compose -f docker-compose.hetzner.yml logs -f app` |
| Update einspielen | `git pull && docker compose -f docker-compose.hetzner.yml up -d --build` |
| Neustart | `docker compose -f docker-compose.hetzner.yml restart app` |
| Health | `curl -s https://compliance.labpulse.ai/health` |

Der Compose-Healthcheck ruft im App-Container `/health` auf. Er bestätigt die
laufende FastAPI-App, nicht die fachliche Verfügbarkeit externer Modellanbieter.

## Backup & Restore

Nächtliche Sicherung per Cron (läuft als root): Datenbank um 03:17 Uhr,
hochgeladene Originaldokumente um 03:23 Uhr. Beide Sicherungen werden 14 Tage
aufbewahrt und müssen gemeinsam restauriert werden.

```
17 3 * * * docker exec qrm-delta-postgres-1 pg_dump -U qrm_app qrm_orchestration | gzip > /opt/qrm-delta/backups/qrm_$(date +\%F).sql.gz && find /opt/qrm-delta/backups -name "qrm_*.sql.gz" -mtime +14 -delete
23 3 * * * tar -C /var/lib/docker/volumes/qrm-delta_qrm_app_documents/_data -czf /opt/qrm-delta/backups/qrm_documents_$(date +\%F).tar.gz . && find /opt/qrm-delta/backups -name "qrm_documents_*.tar.gz" -mtime +14 -delete
```

Restore (geprobt bei Erstinstallation):

```bash
gunzip -c /opt/qrm-delta/backups/qrm_<datum>.sql.gz | \
  docker exec -i qrm-delta-postgres-1 psql -U qrm_app -d qrm_orchestration

tar -C /var/lib/docker/volumes/qrm-delta_qrm_app_documents/_data \
  -xzf /opt/qrm-delta/backups/qrm_documents_<datum>.tar.gz
```

Vor dem Restore die App stoppen, damit Snapshot-Metadaten und Dokumentvolume
konsistent eingespielt werden. Danach App starten und einen vorhandenen Fall
inklusive Originaldokument und Prüfmappe kontrollieren.

## Proxy / TLS

- Vhost: `/etc/letsencrypt/vhosts.d/compliance.labpulse.ai.conf`
- Nach Vhost-Änderungen: `docker exec voxdrop-nginx-1 nginx -t && docker exec voxdrop-nginx-1 nginx -s reload`
- Zertifikat: vorhandenes Let's-Encrypt-Zertifikat `compliance.labpulse.ai`
  (Erneuerung läuft über den bestehenden certbot-Mechanismus des Servers).

### ⚠️ Offener Punkt für das VoxDrop-Repo

In `/srv/voxdrop/current/deploy/nginx.conf` wurde im `http {}`-Block ergänzt:

```
include /etc/nginx/ssl/vhosts.d/*.conf;
```

Diese Zeile bitte in das VoxDrop-Repository (`deploy/nginx.conf`) übernehmen,
damit sie ein künftiges VoxDrop-Deployment nicht entfernt. Falls sie doch
verloren geht: Zeile wieder einfügen, `nginx -t`, Reload — der Vhost selbst
bleibt erhalten.

## Frontend auf `qrm.labpulse.ai`

Das Next.js-Frontend läuft als eigenes Compose-Projekt unter
`/opt/qrm-delta-frontend` und spricht das Backend nur über das Docker-Host-Gateway
an. Der Browser erhält weder den Backend-API-Key noch direkten Zugriff auf das
Backend.

```bash
cd /opt/qrm-delta-frontend
git fetch origin codex/pharmaqrm-production
git checkout --detach origin/codex/pharmaqrm-production
./ops/deploy-frontend-hetzner.sh
```

`.env.frontend` bleibt ausschließlich auf dem Server und enthält:

```
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=...
QRM_BACKEND_API_KEY=...
QRM_BACKEND_TENANT_ID=tenant_gruenewald
```

**Wichtig:** Die beiden `NEXT_PUBLIC_SUPABASE_*` Werte müssen beim Docker-Build
als Compose-Variablen vorliegen. Deshalb immer das obige Skript verwenden; ein
bloßes `docker compose ... up --build` übernimmt nur die Runtime-Variablen und
würde die Login-Konfiguration nicht in das Browser-Bundle einbauen.

Zugriff wird im Frontend aus signierten Supabase-`app_metadata`-Claims abgeleitet.
Für einen System-Owner sind mindestens diese Werte erforderlich:

```json
{
  "qrm_role": "system-owner",
  "qrm_tenant_id": "tenant_gruenewald"
}
```
