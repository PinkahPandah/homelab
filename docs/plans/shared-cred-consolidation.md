# Shared Credential Consolidation Plan

## Ziel

Shared Cred Store (`store.json`) als **Single Source of Truth** für alle Secrets,
wo es architektonisch sinnvoll ist. Secrets aus individuellen `.env`-Files eliminieren,
Duplikate beseitigen.

## Realistischer Scope

| Kategorie | Anteil Secrets | Shared-Cred-tauglich? |
|---|---|---|
| **API-Services** (HTTP-API von außen aufrufbar) | ~25% | ✅ Proxy-Pattern |
| **Datenbanken** (postgres, influxdb, qdrant, redis) | ~15% | ❌ Brauchen Passwort beim Boot |
| **Infra/Middleware** (traefik, authelia, lldap) | ~25% | ❌ Statische Config, Boot-Secrets |
| **LLM-Provider-Keys** (litellm, openwebui, speakr) | ~20% | ❌ Direkte API-Calls brauchen Key im Prozess |
| **Interne Secrets** (JWT_SECRET, ENCRYPTION_KEY) | ~15% | ❌ App-intern, nie extern |

**Fazit**: ~25% der Secrets sind über Shared-Cred+Proxy konsolidierbar.
Das sind genau die, die heute am stärksten dupliziert sind.

---

## Phase 1: Bestehende Integrationen vervollständigen

### 1.1 Katalog-Lücken schließen

Diese Meridian-Services haben HTTP-APIs, sind aber **nicht** im Shared-Integration-Katalog:

| Service | API? | Credential-Typ | Priorität |
|---|---|---|---|
| `crawlab` | Ja (REST) | `api_key` oder Basic Auth | Hoch — bereits von Mercato genutzt |
| `dockhand` | Ja (REST) | `api_key` | Mittel |
| `fireshare` | Ja (REST) | `api_key` | Niedrig |
| `glances` | Ja (REST) | Keine Auth nötig | Niedrig |
| `hcgateway` | Ja (REST) | `api_key` | Mittel |
| `influxdb` | Ja (REST) | `token` | Hoch — von vielen genutzt |
| `litellm` | Ja (REST) | `api_key` (master key) | Hoch — 4-fach dupliziert |
| `metamcp` | Ja (REST) | `api_key` | Mittel |
| `metube` | Ja (REST) | Keine Auth | Niedrig |
| `paperless-gpt` | Ja (REST) | `api_key` | Mittel |
| `postiz` | Ja (REST) | `api_key` | Niedrig |
| `speakr` | Ja (REST) | `api_key` | Mittel |
| `trek` | Ja (REST) | `api_key` | Niedrig |

**Aktion**: IntegrationDefs in `shared/integrations/connectors.py` ergänzen.

### 1.2 Duplizierte Secrets in den Store migrieren

Diese Keys sind heute in 3-4 `.env`-Files identisch — einmalig in `store.json` ablegen:

| Secret | Heutige Orte | Store-Key |
|---|---|---|
| LiteLLM Master Key | litellm, mealie, cronicle, telegraf | `litellm:__global__` |
| SMTP-Passwort | sparkyfitness, mealie, crawlab, authelia | `smtp:__global__` |
| LLDAP-Passwort | lldap, cronicle, authelia | `lldap:__global__` |
| InfluxDB Token | crawlab, telegraf, mercato | `influxdb:__global__` |
| Qdrant API Key | qdrant, openwebui | ❌ Qdrant braucht Key beim Boot |
| OpenRouter Key | speakr, telegraf | `openrouter:__global__` |

**Aktion**: Admin-API (`PUT /api/admin/credentials/{name}`) nutzen, um globale Creds zu setzen.

---

## Phase 2: Nexus-Proxy erweitern

Nexus hat mit `meridian.py` schon das Pattern für 4 Services (mealie, ourgroceries, sparkyfitness, yazio). Erweiterbar auf:

### Priorität Hoch

| Endpoint | Upstream | Credential | Nutzen |
|---|---|---|---|
| `GET /meridian/influxdb-query?q=...` | InfluxDB API | `influxdb:__global__` | Ersetzt 3 `.env`-Files |
| `GET /meridian/paperless-search?q=...` | Paperless API | `paperless:user` | Personal |
| `GET /meridian/immich-search?q=...` | Immich API | `immich:user` | Personal |
| `GET /meridian/grocy-stock` | Grocy API | `grocy:__global__` | Shared |

### Priorität Mittel

| Endpoint | Upstream | Nutzen |
|---|---|---|
| `GET /meridian/glances-status` | Glances API | Server-Monitoring |
| `GET /meridian/homeassistant-states` | HA API | Smart-Home-Dashboard |
| `GET /meridian/dawarich-locations` | Dawarich API | Travel-Dashboard |
| `GET /meridian/karakeep-bookmarks` | Karakeep API | Lesezeichen-Suche |

**Pattern** (aus `meridian.py:26-33` kopierbar):
```python
def _resolve_creds(connector_name: str, user_id: str) -> dict | None:
    try:
        creds = shared_creds.resolve_credentials(connector_name, user_id=user_id)
        if isinstance(creds, dict):
            return creds
    except shared_creds.CredentialError:
        pass
    return None
```

---

## Phase 3: Vanguard-Connector-API als universelles Gateway

Vanguards `POST /api/connectors/execute` (`skills.py:161`) ist der Key-freie
Execution-Pfad. Credentials werden serverside resolved, Caller sieht nur Output.

### 3.1 Agent-Dokumentation

Root-`AGENTS.md` um diesen Block ergänzen:

```markdown
## Homelab-Connectors auslösen (key-frei)

Nutze Vanguards Connector-API statt `.env`-Files oder `docker exec`:

    curl -s -H "Remote-User: $USER_EMAIL" \
      -X POST http://vanguard:8000/api/connectors/execute \
      -d '{"connector_name":"ntfy","action":"send","params":{"topic":"test","message":"hello"}}'

Verfügbare Connectoren: `GET http://vanguard:8000/api/skills?type=connector`
Credentials werden serverseitig aufgelöst — du siehst NIE API-Keys.
```

### 3.2 CLI-Wrapper für Agenten

`shared/scripts/trigger_connector.sh`:
```bash
#!/bin/bash
# Usage: trigger_connector.sh <connector> <action> [key=val ...]
# Beispiel: trigger_connector.sh ntfy send topic=alerts message="Server down"
CONNECTOR=$1; ACTION=$2; shift 2
# Build JSON params from remaining args
# Call Vanguard API
```

---

## Phase 4: `.env`-Files reduzieren

Services, deren Secrets komplett in den Shared Store migriert wurden,
können ihre entsprechenden `.env`-Einträge entfernen.

### Beispiel: `crawlab/.env`

**Vorher:**
```
INFLUXDB_TOKEN=qVNEKf5yeU...
NTFY_TOKEN=...
OPENAI_API_KEY=sk-...
SMTP_PASSWORD=MS@rd20x2!?
```

**Nachher:**
```
# Credentials jetzt in shared/credentials/store.json
# Crawlab-API-Calls laufen über Nexus-Proxy oder Vanguard-Connector
```

Der Crawlab-**Container** braucht die Secrets weiterhin wenn er SELBST die APIs aufruft —
also vollständige Entfernung nur wenn der Service UMSTEIGT auf externen Proxy.
Für die meisten Services realistischer: Secrets bleiben im Container, aber der
WERT kommt aus EINER Quelle (Store), nicht 4-fach kopiert.

---

## Phase 5: Secret-Generator für Container (Nice-to-have)

Problem: Container brauchen Secrets als env vars beim Boot. Lösung:

```
store.json (Single Source)
    │
    ▼
generate_envs.py  ← liest store.json, entschlüsselt mit SHARED_CREDENTIALS_SECRET
    │
    ▼
meridian/<service>/.env  ← generated, .gitignore'd
```

```python
# generate_envs.py — erzeugt .env-Files aus dem Shared Store
# Mapping: connector_name → env var name (aus shared/credentials/fallback.py)

import shared.credentials as creds
from shared.credentials.fallback import FALLBACK_MAP

for connector_name, env_map in FALLBACK_MAP.items():
    creds = creds.resolve_credentials(connector_name, user_id=None)
    if creds:
        for key, env_var in env_map.items():
            value = creds.get(key)
            if value:
                print(f"{env_var}={value}")
```

Das eliminiert die Duplikate: Ein Secret wird EINMAL im Store geändert,
`generate_envs.py` propagiert es in alle `.env`-Files.

---

## Nicht machbar (akzeptierte Ausnahme)

Diese Secrets MÜSSEN weiterhin direkt im Container leben:

| Typ | Beispiele | Grund |
|---|---|---|
| Datenbank-Passwörter | `POSTGRES_PASSWORD`, `INFLUXDB_PASSWORD` | Werden beim ersten Boot gesetzt, danach von der DB selbst verwaltet |
| Auth-Secrets | `JWT_SECRET`, `SESSION_SECRET`, `STORAGE_ENCRYPTION_KEY` | App-interne Krypto, nie nach außen gegeben |
| Traefik/Authelia | `TRAEFIK_AUTH`, Zertifikate | Statische Middleware-Config |
| LLM-Provider-Keys | `OPENAI_API_KEY` in litellm | Litellm ruft Provider DIREKT auf, Key muss im Prozess sein |

---

## Zusammenfassung

| Phase | Was | Aufwand | Impact |
|---|---|---|---|
| 1 | Katalog-Lücken füllen + Duplikate in Store | 1-2h | 12 neue IntegrationDefs, 4 Secrets dedupliziert |
| 2 | Nexus-Proxy um 4-8 Endpoints erweitern | 2-4h | 6-10 `.env`-Einträge eliminierbar |
| 3 | Agent-Doku + CLI-Wrapper | 0.5h | Agenten nutzen Connector-API statt `.env` |
| 4 | `.env`-Files ausdünnen | 1h | Redundanz reduziert |
| 5 | `generate_envs.py` Generator | 1h | Single Source für alle Container-Secrets |
