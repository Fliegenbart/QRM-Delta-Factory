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
| Status | `cd /opt/qrm-delta && docker compose -f docker-compose.hetzner.yml ps` |
| Logs | `docker compose -f docker-compose.hetzner.yml logs -f app` |
| Update einspielen | `git pull && docker compose -f docker-compose.hetzner.yml up -d --build` |
| Neustart | `docker compose -f docker-compose.hetzner.yml restart app` |
| Health | `curl -s https://compliance.labpulse.ai/health` |

## Backup & Restore

Nächtlicher Dump per Cron (läuft als root, 03:17 Uhr):

```
17 3 * * * docker exec qrm-delta-postgres-1 pg_dump -U qrm_app qrm_orchestration | gzip > /opt/qrm-delta/backups/qrm_$(date +\%F).sql.gz && find /opt/qrm-delta/backups -name "qrm_*.sql.gz" -mtime +14 -delete
```

Restore (geprobt bei Erstinstallation):

```bash
gunzip -c /opt/qrm-delta/backups/qrm_<datum>.sql.gz | \
  docker exec -i qrm-delta-postgres-1 psql -U qrm_app -d qrm_orchestration
```

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

## Vercel-Anbindung

Environment-Variablen im Vercel-Projekt:

```
QRM_BACKEND_URL=https://compliance.labpulse.ai
QRM_BACKEND_API_KEY=<der Key aus QRM_API_KEYS>
QRM_BACKEND_TENANT_ID=tenant_gruenewald
```
