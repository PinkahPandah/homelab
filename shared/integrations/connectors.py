"""Canonical connector catalog — single source of truth for all homelab integrations.

All 56 connectors defined with typed credential fields, categories, and default policies.
Add new connectors here — they'll be automatically discovered by Vanguard and Nexus.
"""

from __future__ import annotations

from shared.integrations.models import CredentialField, IntegrationDef

ALL: list[IntegrationDef] = [
    # ── automation ──────────────────────────────────────────────────
    IntegrationDef(
        id="n8n",
        display_name="n8n",
        description="Workflow automation platform. Execute, deploy, and debug automations.",
        category="automation",
        credential_fields=[
            CredentialField(key="url", label="n8n URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="disabled",
    ),
    IntegrationDef(
        id="docker",
        display_name="Docker",
        description="Container management. Inspect, restart, and monitor Docker services.",
        category="automation",
        credential_fields=[],
        default_policy="disabled",
    ),
    IntegrationDef(
        id="homeassistant",
        display_name="Home Assistant",
        description="Smart home automation. Control devices, check states, trigger automations.",
        category="automation",
        credential_fields=[
            CredentialField(key="url", label="Home Assistant URL", secret=False),
            CredentialField(key="token", label="Long-Lived Access Token"),
        ],
    ),
    IntegrationDef(
        id="ntfy",
        display_name="ntfy",
        description="Push notification service. Send notifications to desktop and mobile.",
        category="automation",
        credential_fields=[
            CredentialField(key="url", label="ntfy Server URL", secret=False),
            CredentialField(key="topic", label="Default Topic", secret=False),
        ],
    ),
    IntegrationDef(
        id="crawl4ai",
        display_name="Crawl4AI",
        description="Web crawling and scraping. Fetch and extract content from URLs via AI-powered crawler.",
        category="automation",
        credential_fields=[
            CredentialField(key="url", label="Crawl4AI URL", secret=False),
        ],
    ),
    IntegrationDef(
        id="crawl4ai_stealth",
        display_name="Crawl4AI Stealth",
        description="Stealth web crawling with proxy rotation. Bypass bot detection for sensitive targets.",
        category="automation",
        credential_fields=[
            CredentialField(key="url", label="Crawl4AI URL", secret=False),
        ],
    ),
    IntegrationDef(
        id="cronicle",
        display_name="Cronicle",
        description="Job scheduler and cron management. Create, run, and monitor scheduled jobs.",
        category="automation",
        credential_fields=[
            CredentialField(key="url", label="Cronicle URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
    ),

    # ── knowledge ───────────────────────────────────────────────────
    IntegrationDef(
        id="atlas",
        display_name="Atlas",
        description="RAG search and ingestion. Search knowledge base, ingest documents, reindex.",
        category="knowledge",
        credential_fields=[
            CredentialField(key="url", label="Atlas URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
    ),
    IntegrationDef(
        id="crisis_score",
        display_name="Crisis Score",
        description="Market crisis analysis. Score financial news for crisis signals.",
        category="knowledge",
        credential_fields=[
            CredentialField(key="url", label="Atlas URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
    ),
    IntegrationDef(
        id="nexus",
        display_name="Nexus",
        description="Personal data hub. Access daily check-ins, captures, health data, and entity graph.",
        category="knowledge",
        credential_fields=[
            CredentialField(key="url", label="Nexus URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="disabled",
    ),
    IntegrationDef(
        id="substack",
        display_name="Substack",
        description="Newsletter platform. Read and search Substack publications.",
        category="knowledge",
        credential_fields=[],
    ),
    IntegrationDef(
        id="searxng",
        display_name="SearXNG",
        description="Privacy-respecting meta search engine. Web search without tracking.",
        category="knowledge",
        credential_fields=[
            CredentialField(key="url", label="SearXNG URL", secret=False),
        ],
    ),
    IntegrationDef(
        id="booklore",
        display_name="Booklore",
        description="Book library manager. Search, browse, and manage your book collection.",
        category="knowledge",
        credential_fields=[
            CredentialField(key="url", label="Booklore URL", secret=False),
            CredentialField(key="username", label="Username", secret=False),
            CredentialField(key="password", label="Password"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="openwebui",
        display_name="Open WebUI",
        description="LLM chat interface. Search and browse chat history, manage conversations.",
        category="knowledge",
        credential_fields=[
            CredentialField(key="url", label="Open WebUI URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
    ),
    IntegrationDef(
        id="paperless",
        display_name="Paperless-ngx",
        description="Document management. Search, tag, and manage scanned documents.",
        category="knowledge",
        credential_fields=[
            CredentialField(key="url", label="Paperless URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="scholar",
        display_name="Scholar",
        description="Academic paper search via Semantic Scholar. Search publications by topic or author.",
        category="knowledge",
        credential_fields=[
            CredentialField(key="api_key", label="Semantic Scholar API Key"),
        ],
    ),
    IntegrationDef(
        id="web_search",
        display_name="Web Search",
        description="General web search capability via multiple backends (Tavily, Exa, SearXNG).",
        category="knowledge",
        credential_fields=[
            CredentialField(key="tavily_api_key", label="Tavily API Key"),
            CredentialField(key="exa_api_key", label="Exa API Key"),
        ],
    ),

    # ── productivity ────────────────────────────────────────────────
    IntegrationDef(
        id="nextcloud",
        display_name="Nextcloud",
        description="Self-hosted cloud storage. Browse files, manage shares, access calendars and contacts.",
        category="productivity",
        credential_fields=[
            CredentialField(key="url", label="Nextcloud URL", secret=False),
            CredentialField(key="username", label="Username", secret=False),
            CredentialField(key="app_password", label="App Password"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="todoist",
        display_name="Todoist",
        description="Task management. Create, read, update, delete tasks, projects, sections, and comments.",
        category="productivity",
        credential_fields=[
            CredentialField(key="api_key", label="API Token"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="ourgroceries",
        display_name="OurGroceries",
        description="Shared grocery list. Add, remove, and sync items across household members.",
        category="productivity",
        credential_fields=[
            CredentialField(key="username", label="Username", secret=False),
            CredentialField(key="password", label="Password"),
        ],
        default_policy="shared",
    ),
    IntegrationDef(
        id="mealie",
        display_name="Mealie",
        description="Recipe management and meal planning. Search recipes, manage meal plans, import from URL.",
        category="productivity",
        credential_fields=[
            CredentialField(key="url", label="Mealie URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="grocy",
        display_name="Grocy",
        description="Household inventory and grocery management. Track stock, create shopping lists.",
        category="productivity",
        credential_fields=[
            CredentialField(key="url", label="Grocy URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="shared",
    ),
    IntegrationDef(
        id="homebox",
        display_name="Homebox",
        description="Home inventory management. Track items, warranties, and maintenance schedules.",
        category="productivity",
        credential_fields=[
            CredentialField(key="url", label="Homebox URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="shared",
    ),
    IntegrationDef(
        id="hortusfox",
        display_name="Hortusfox",
        description="Plant collection manager. Track plants, watering schedules, and growth.",
        category="productivity",
        credential_fields=[
            CredentialField(key="url", label="Hortusfox URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="shared",
    ),
    IntegrationDef(
        id="notion",
        display_name="Notion",
        description="All-in-one workspace. Read and write pages, databases, and content blocks.",
        category="productivity",
        credential_fields=[
            CredentialField(key="url", label="Notion URL", secret=False),
            CredentialField(key="api_key", label="Integration Token"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="vouchervault",
        display_name="VoucherVault",
        description="Gift card and voucher tracker. Track balances, expiry dates, and usage.",
        category="finance",
        credential_fields=[
            CredentialField(key="url", label="VoucherVault URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="shared",
    ),

    # ── finance ─────────────────────────────────────────────────────
    IntegrationDef(
        id="actualbudget",
        display_name="Actual Budget",
        description="Personal budgeting. Track income, expenses, categories, and account balances.",
        category="finance",
        credential_fields=[
            CredentialField(key="url", label="Actual Budget URL", secret=False),
            CredentialField(key="password", label="Server Password"),
            CredentialField(key="e2e_encryption_key", label="E2E Encryption Key"),
        ],
        default_policy="personal",
        doc_url="https://actualbudget.org/docs/",
    ),
    IntegrationDef(
        id="ghostfolio",
        display_name="Ghostfolio",
        description="Investment portfolio tracker. Monitor holdings, performance, and asset allocation.",
        category="finance",
        credential_fields=[
            CredentialField(key="url", label="Ghostfolio URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="mercato",
        display_name="Mercato",
        description="Market data and price tracking. Stock quotes, price alerts, portfolio analysis.",
        category="finance",
        credential_fields=[],
        default_policy="personal",
    ),
    IntegrationDef(
        id="coingecko",
        display_name="CoinGecko",
        description="Cryptocurrency market data. Prices, market caps, volume, and historical charts.",
        category="external",
        credential_fields=[],
    ),

    # ── media ───────────────────────────────────────────────────────
    IntegrationDef(
        id="immich",
        display_name="Immich",
        description="Photo and video management. Search, browse, and organize your media library.",
        category="media",
        credential_fields=[
            CredentialField(key="url", label="Immich URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="yamtrack",
        display_name="Yamtrack",
        description="Media tracking. Track movies, TV shows, games, books, and anime.",
        category="media",
        credential_fields=[
            CredentialField(key="url", label="Yamtrack URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="tmdb",
        display_name="TMDB",
        description="The Movie Database. Search movies, TV shows, cast, and ratings.",
        category="media",
        credential_fields=[
            CredentialField(key="api_key", label="API Key v3"),
        ],
    ),
    IntegrationDef(
        id="karakeep",
        display_name="Karakeep",
        description="Universal bookmark manager. Search, tag, and organize bookmarks from any source.",
        category="media",
        credential_fields=[
            CredentialField(key="url", label="Karakeep URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="personal",
    ),

    # ── tracking ────────────────────────────────────────────────────
    IntegrationDef(
        id="dawarich",
        display_name="Dawarich",
        description="Location history tracking. View travel timelines, stats, and visit patterns.",
        category="tracking",
        credential_fields=[
            CredentialField(key="url", label="Dawarich URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="endurain",
        display_name="Endurain",
        description="Fitness and health tracking. Workout logs, activity data, and progress charts.",
        category="tracking",
        credential_fields=[
            CredentialField(key="url", label="Endurain URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="sparkyfitness",
        display_name="SparkyFitness",
        description="Training and workout management. Log exercises, track progress, manage routines.",
        category="tracking",
        credential_fields=[
            CredentialField(key="url", label="SparkyFitness URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="adventurelog",
        display_name="AdventureLog",
        description="Travel journal. Log trips, destinations, activities, and travel memories.",
        category="tracking",
        credential_fields=[
            CredentialField(key="url", label="AdventureLog URL", secret=False),
            CredentialField(key="username", label="Username", secret=False),
            CredentialField(key="password", label="Password"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="yazio",
        display_name="Yazio",
        description="Nutrition and calorie tracking. Log meals, track macros, and monitor diet goals.",
        category="tracking",
        credential_fields=[
            CredentialField(key="username", label="Username", secret=False),
            CredentialField(key="password", label="Password"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="opensky",
        display_name="OpenSky Network",
        description="Flight tracking. Real-time aircraft positions, flight routes, and airport data.",
        category="tracking",
        credential_fields=[
            CredentialField(key="username", label="Username", secret=False),
            CredentialField(key="password", label="Password"),
        ],
        default_policy="shared",
    ),
    IntegrationDef(
        id="parcelsapp",
        display_name="ParcelsApp",
        description="Package tracking. Track shipments from multiple carriers in one place.",
        category="tracking",
        credential_fields=[],
        default_policy="shared",
    ),
    IntegrationDef(
        id="healthconnect",
        display_name="Health Connect",
        description="Android Health Connect data gateway. Sync health and fitness data to homelab.",
        category="tracking",
        credential_fields=[
            CredentialField(key="url", label="HCGateway URL", secret=False),
            CredentialField(key="username", label="Username", secret=False),
            CredentialField(key="password", label="Password"),
        ],
    ),

    # ── external ────────────────────────────────────────────────────
    IntegrationDef(
        id="deepl",
        display_name="DeepL",
        description="Neural machine translation. Translate text between languages with high quality.",
        category="external",
        credential_fields=[
            CredentialField(key="api_key", label="API Key"),
        ],
    ),
    IntegrationDef(
        id="openweathermap",
        display_name="OpenWeatherMap",
        description="Weather data and forecasts. Current conditions, forecasts, and historical weather.",
        category="external",
        credential_fields=[
            CredentialField(key="api_key", label="API Key"),
        ],
    ),
    IntegrationDef(
        id="github",
        display_name="GitHub",
        description="Code hosting and collaboration. Manage repos, issues, PRs, and actions.",
        category="external",
        credential_fields=[
            CredentialField(key="api_key", label="Personal Access Token"),
        ],
        default_policy="personal",
    ),
    IntegrationDef(
        id="google_places",
        display_name="Google Places",
        description="Google Places API. Search for places, get details, photos, and reviews.",
        category="external",
        credential_fields=[
            CredentialField(key="api_key", label="API Key"),
        ],
    ),
    IntegrationDef(
        id="google_routes",
        display_name="Google Routes",
        description="Google Maps Routes API. Calculate routes, travel times, and directions.",
        category="external",
        credential_fields=[
            CredentialField(key="api_key", label="API Key"),
        ],
    ),
    IntegrationDef(
        id="foursquare",
        display_name="Foursquare",
        description="Foursquare Places API. Venue search, details, tips, and photos.",
        category="external",
        credential_fields=[
            CredentialField(key="api_key", label="API Key"),
        ],
    ),
    IntegrationDef(
        id="trivago",
        display_name="Trivago",
        description="Hotel price comparison. Search and compare hotel prices across providers.",
        category="external",
        credential_fields=[
            CredentialField(key="url", label="Crawl4AI URL", secret=False),
        ],
    ),
    IntegrationDef(
        id="aftership",
        display_name="AfterShip",
        description="Shipment tracking API. Multi-carrier package tracking with webhooks.",
        category="external",
        credential_fields=[
            CredentialField(key="api_key", label="API Key"),
        ],
    ),
    IntegrationDef(
        id="aishub",
        display_name="AISHub",
        description="Vessel tracking via AIS data. Real-time ship positions and maritime traffic.",
        category="external",
        credential_fields=[
            CredentialField(key="api_key", label="API Key"),
        ],
    ),

    # ── monitoring ──────────────────────────────────────────────────
    IntegrationDef(
        id="uptimekuma",
        display_name="Uptime Kuma",
        description="Service monitoring and status pages. Check service health, uptime, and response times.",
        category="monitoring",
        credential_fields=[
            CredentialField(key="url", label="Uptime Kuma URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="shared",
    ),
    IntegrationDef(
        id="grafana",
        display_name="Grafana",
        description="Observability dashboards. View metrics, logs, and monitoring dashboards.",
        category="monitoring",
        credential_fields=[
            CredentialField(key="url", label="Grafana URL", secret=False),
            CredentialField(key="api_key", label="API Key"),
        ],
        default_policy="shared",
    ),

    # ── vehicle ──────────────────────────────────────────────────────
    IntegrationDef(
        id="lubelogger",
        display_name="LubeLogger",
        description="Vehicle maintenance tracking. Log fuel-ups, services, and repairs.",
        category="vehicle",
        credential_fields=[
            CredentialField(key="url", label="LubeLogger URL", secret=False),
            CredentialField(key="username", label="Username", secret=False),
            CredentialField(key="password", label="Password"),
        ],
        default_policy="shared",
    ),
]


_BY_ID: dict[str, IntegrationDef] | None = None


def _ensure_index() -> dict[str, IntegrationDef]:
    global _BY_ID
    if _BY_ID is None:
        _BY_ID = {d.id: d for d in ALL}
    return _BY_ID


def list_all() -> list[IntegrationDef]:
    return list(ALL)


def get(connector_id: str) -> IntegrationDef | None:
    return _ensure_index().get(connector_id)


def get_category(connector_id: str) -> str | None:
    d = get(connector_id)
    return d.category if d else None


def get_default_policy(connector_id: str) -> str | None:
    d = get(connector_id)
    return d.default_policy if d else None


def get_fields(connector_id: str) -> list[CredentialField]:
    d = get(connector_id)
    return list(d.credential_fields) if d else []
