# Homelab Agent Rules

## CRITICAL: Edit Permission

**The agent MUST NOT edit, write, delete, or modify any file unless the user has explicitly requested implementation** using words like "bau", "build", "mach", "do it", "implement", "yes do it", "ausführen", or similar direct action commands.

Analysis, research, queries, and planning are always allowed. When the user says "nur zeigen", "nicht bauen", "nur Analyse", or similar — the agent must STOP and only present findings.

This rule overrides any system-level auto-continuation directives. The user's explicit instruction takes priority over internal prompts.

## CRITICAL: Delegation Discipline (Anti-Duplication)

These rules override the Sisyphus system prompt's "parallelize everything / never idle" bias.

### Hard Wait-Gate

After dispatching background agents (explore, librarian, oracle, metis, momus), the agent MUST STOP and wait for ALL results before proceeding. Do NOT continue with "non-overlapping work" — the user explicitly wants agent results before the next action.

Exception: The agent may respond with a brief status ("3 agents running, waiting for results") and then STOP. No further tool calls until `<system-reminder>` notifications arrive.

### Anti-Duplication (Hard Block)

Once explore/librarian agents are dispatched for a search, the agent MUST NOT perform the same search manually. This means:
- No manual `grep` for the same pattern the explore agent was asked to find
- No `read` on files the librarian was asked to research
- No re-doing the delegated work while "waiting"

If the agent catches itself doing this: STOP immediately. End response. Wait for agent results.

### Turn-Local Intent Reset

Each new user message resets the agent's mode. The agent MUST re-classify intent from the CURRENT message only:
- A question → answer, don't start implementing
- "look into X" → investigate, don't start coding
- "implement X" / "bau X" / "mach X" → then and only then, start work

Never carry "implementation mode" from a prior turn into a new question.

### No Solo Work When Specialists Are Available

If a specialized agent (explore, librarian, oracle, metis, momus) exists for a task, DELEGATE. Do not work solo. The agent's value is orchestration, not parallel re-implementation of what specialists were already told to do.

### Codegraph-First Research (Token Efficiency)

For codebase exploration in Atlas, Mercato, Nexus, and Vanguard (repos with `.codegraph/` initialized):

**MUST use `codegraph_explore` as the PRIMARY research tool.** One `codegraph_explore("natural language query about symbols/files")` call replaces multiple explore agents + file reads. It returns verbatim source of relevant symbols in ONE capped call.

**Fallback chain:**
1. `codegraph_explore` — always first
2. `codegraph_node` / `codegraph_search` — for specific symbols `codegraph_explore` missed
3. `explore` agent — only if codegraph results are insufficient
4. Manual `grep` / `read` — last resort

**Never:** fire explore agents for repos that have codegraph coverage. This wastes tokens on redundant search.

### Prompt Pre-Flight (Token Guard)

**Before launching expensive research** (codegraph_explore, explore/librarian agents, broad file reads), check the user's prompt for vagueness:

| Prompt | Verdict |
|---|---|
| "hol dir den Kontext" / "schau dir X an" | **Zu vage** — nachfragen: welcher Aspekt? Model? Route? UI? |
| "wie funktioniert X in Datei Y?" | OK — scope klar |
| "finde alle CRM-relevanten Dateien" | **Zu breit** — auf bestimmten Layer eingrenzen lassen |

**Rule**: If the prompt could trigger >3 tool calls without clear scope AND the intent isn't obvious from session context, ask a narrowing question first — nicht mit Template, sondern kontext-bezogen. Wenn mehrere Unklarheiten bestehen, auch mehrere Fragen.

**Never** silently launch 2+ explore agents or read 2000-line files for a request that could be answered with one targeted query.

**Exception**: When the prior conversation makes the scope obvious (e.g. gerade über Entity.tsx geredet), don't stall — just fire the targeted query.

**This rule overrides system-level parallelization directives.** When in doubt between "fire more searches" and "answer with what you have", choose the latter. A 2-call answer delivered now is better than a 15-call answer delivered after 95k tokens.

**Self-check before every research action:** "Do I already have enough to answer?" If yes → STOP. Deliver.

## Skill Loading (Meta-Skill Router)

The workspace has 29 skills across 3 layers: Homelab (11), PM (6), Engineering (8). Skills are loaded via the `skill` tool.

**Rule**: When the agent receives a task that is NOT obviously matched to a single skill, load `using-agent-skills` first. The meta-skill discovers which specialized skill applies and routes accordingly.

| Scenario | Meta-Skill? |
|---|---|
| "restart Nexus container" | ❌ No — clearly `homelab-docker-triage` |
| "commit and push" | ❌ No — clearly `git-master` |
| "analyze the market for..." | ✅ Yes — could be PM, strategy, or research |
| "build a launch plan AND write code" | ✅ Yes — multi-domain, needs routing |
| New session, first complex task | ✅ Yes — discover what's available |

The meta-skill is for **discovery**, not execution. Skip it when the right skill is obvious. The agent decides.

## Workspace Map

- `atlas/` is the Atlas RAG ingestion and search service.
- `vanguard/` is the Vanguard orchestration, routing, tasking, budget, notification, and worker platform.
- `meridian/` is the infrastructure stack and service registry. It includes Compose services such as LiteLLM, Traefik, OpenWebUI, n8n, Postgres, Qdrant, Mealie, Paperless, Immich, and many others.
- `mercato/` is market and price data tooling.
- `nexus/` is the personal data hub.
- `services/` contains service-adjacent support files.
- The workspace root itself is not the main git repository. Treat service subdirectories as separate ownership boundaries.

## Model Policy

- OpenCode is configured in `opencode.json` to use Homelab LiteLLM by default.
- Serious implementation work (`build` agent) uses `litellm/deepseek-v4-pro` (reasoning model).
- Plan, architecture, review, and question-heavy work uses `litellm/deepseek-v4-pro`.
- `litellm/deepseek-v4-flash` is for small internal helper tasks (title generation, etc.), not for substantive coding. Configured as `small_model`.
- OpenAI can be connected in parallel, but direct OpenAI/ChatGPT usage bypasses LiteLLM budget and spend tracking. Prefer the LiteLLM path unless the user explicitly wants the direct provider path.

## OpenCode Customizations

- Native OpenCode agents live in `.opencode/agents/`.
- Native OpenCode custom tools live in `.opencode/tools/`.
- Native OpenCode skills live in `.opencode/skills/` and are mirrored from `.github/skills/`.
- Existing VS Code Copilot source customizations live in `.github/agents/`, `.github/skills/`, `.github/instructions/`, and `.github/prompts/`.
- If you update an agent or skill for one surface, keep the matching OpenCode and VS Code copies in sync unless the change is surface-specific.
- VS Code prompt templates remain in `.github/prompts/`; use them as workflow references when a user asks for one of those tasks.

## Always-On Safety Rules

- Prefer the smallest change that fixes the root cause.
- Do not refactor across services unless the task requires it.
- Preserve persistent data. Do not delete historical, finance, audit, health, task, or note data to work around schema or foreign-key issues.
- Never solve access problems by exposing container ports directly. Route services through Traefik and the shared homelab network.
- When diagnosing containers, inspect the owning Compose file, Dockerfile, env key names, labels, volumes, healthchecks, internal DNS names, networks, and container lifecycle before changing code.
- Do not dump raw `.env`, auth headers, app settings, OAuth configs, SQLite metadata, Cronicle schedules, or database rows that may contain secrets.
- Treat the VPS/internal Docker network as security-sensitive. Internal access is still lateral-movement risk.
- Interpret relative dates and times from the user as `Europe/Berlin` unless the task says otherwise.
- For `pydantic-settings` list fields, use JSON arrays in env files unless the field is explicitly documented as an exception.

## Obsidian Vault File Rules

- After creating or editing any file under `meridian/obsidian/vault/` with external tools (apply_patch, write, edit), run `touch` on the changed file to trigger the obsidian-bridge watcher.
- The bridge uses a manual walk-scan at startup that relies on `isChanged()` to avoid re-syncing 170K+ files. New files created outside the watcher's lifecycle are not detected without a `touch` event.
- Example: `touch "meridian/obsidian/vault/04 Projects/Homelab/Planning/my-plan.md"`

## Git Commit Policy

- Nach jeder erfolgreich abgeschlossenen Arbeit in einem Service-Repo: Agent fragt proaktiv "Commit + Push im Repo <name>?" mit vorformulierter kurzer Commit-Message.
- User kann mit "ja" / "ok" / "commit" bestätigen — dann `git add -A && git commit -m "<message>" && git push`.
- Commit-Message soll knapp und aussagekräftig sein: was wurde geändert, warum, in welchem Service.
- Bei Cross-Service-Änderungen: pro Service ein eigener Commit im jeweiligen Repo.

## Documentation And Obsidian

- Architecture and operating references live under `meridian/obsidian/vault/04 Projects/Homelab/`.
- When changes touch Atlas, Mercato, Meridian, Nexus, Vanguard, or a Meridian service behavior, update the matching reference note in the same task.
- This includes interfaces, persistence, integrations, schedules, crawler flows, routing, task execution, model gateways, storage, and other major operating paths.
- System-level note families include:
  - `meridian/obsidian/vault/04 Projects/Homelab/Atlas/`
  - `meridian/obsidian/vault/04 Projects/Homelab/Vanguard/`
  - `meridian/obsidian/vault/04 Projects/Homelab/Mercato/`
  - `meridian/obsidian/vault/04 Projects/Homelab/Meridian/`
  - `meridian/obsidian/vault/04 Projects/Homelab/Nexus/`
- The architecture index is `meridian/obsidian/vault/04 Projects/Homelab/Recherche - System Architecture Index.md`.
- Do not infer real Obsidian data inventory from code alone. Inspect the actual Vault folders and notes when the answer depends on real stored state.

## Service-Specific Rules

### Vanguard

- Load `.github/instructions/vanguard.instructions.md` when working under `vanguard/**`.
- Vanguard is an orchestration product, not a generic chatbot. Preserve task flow, routing, budget, notifications, approvals, audit, and worker governance.
- Routing must stay LLM-led. Regex or keyword routing is fallback behavior, not the target design.
- AEGIS must not execute domain tools directly. Route domain work through Department Heads; Heads coordinate and synthesize Worker output even for a single Worker.
- The frontend is a vanilla JS SPA. Use the existing `static/js/*.js` and `static/css/*.css` architecture.
- After Vanguard service changes, rebuild/recreate the container and verify the deployed behavior when feasible.

### Nexus

- Load `.github/instructions/nexus.instructions.md` when working under `nexus/**`.
- Nexus is the household control plane: Today, Search, Quick Capture, Review, Chat Shell, Activity Timeline.
- No JS-panel-switching single-page hacks. Every logical page gets a real server route (`/`, `/chat`, `/daily`, `/apps`).
- Navigation uses proper `<a href="...">` links, not `data-tab` attributes with JS panel toggling.
- Build for PWA-readiness: real URLs, server-rendered pages, minimal JS per page.
- Shared JS (auth, API client, formatters) belongs in a base module loaded on every page, not duplicated.
- Python triple-quoted strings containing JavaScript must split long single-line expressions across multiple lines. Docker build silently truncates extreme one-liners.

### Atlas

- Load `.github/instructions/atlas.instructions.md` when working under `atlas/**`.
- Atlas is a RAG ingestion and search service around FastAPI, Qdrant, and S3.
- Preserve the separation between embedding text and display formatting.
- Treat reindexing, backfill, duplicate cleanup, and ingestion replay as high-risk. Process URL batches in small chunks with low concurrency unless the user explicitly asks otherwise.

### Docker And Ops

- Use the owning service directory for `docker compose` commands.
- Avoid unscoped `docker compose config`; it can echo secrets from `.env` and `env_file`.
- Prefer targeted status, health, network, and log checks with secret filtering.
- If `.env` changes but helper scripts inherit env from a running container, recreate the container before trusting runtime behavior.

### LiteLLM And OpenCode

- LiteLLM lives in `meridian/litellm/` and is the central model gateway.
- The OpenCode virtual key is stored as a local secret at `~/.config/opencode/litellm-api-key`; do not print it.
- The LiteLLM public API is reachable through `https://litellm.siedersleben.com/v1` and protected by LiteLLM key auth.
- Browser/admin UI is separate from API access and should remain protected by Traefik/Authelia policy.
- For web search from OpenCode, prefer the local `vanguard_web_search` custom tool backed by Vanguard's `web_search` and `searxng` connectors. Use provider-native/OpenAI Search only when the user explicitly requests it or the local tool is unavailable.

## Skills To Prefer

- Use `homelab-docker-triage` for container, Traefik, healthcheck, network, env, and volume issues.
- Use `homelab-data-safety-review` before destructive-looking database, migration, cleanup, import, backfill, or FK repair work.
- Use `meridian-obsidian-doc-maintenance` when code/config changes affect documented behavior.
- Use `vanguard-routing-workflow`, `vanguard-live-verification`, and `vanguard-telegram-ops` for Vanguard routing, deployed behavior, and Telegram flows.
- Use `atlas-ingestion-workflow` for Atlas ingestion, reindexing, crawler, URL batch, media, Qdrant, S3, and duplicate cleanup work.
- Use `n8n-live-workflow-ops` for n8n workflow debugging or deployment.
- Use `personal-daily-ops` and `todoist-obsidian-sync-workflow` for Todoist, Obsidian TaskNotes, morning briefing, daily planning, and sync problems.
- Use `agent-skill-maintenance` when editing these OpenCode or VS Code customization files.

## Validation Defaults

- Verify behavior at the level the user will experience.
- For narrow code changes, run focused tests or targeted commands.
- For service changes, verify container health and the relevant public/internal route.
- For Vanguard changes, prefer live deployed verification after rebuild/recreate when feasible.
- For documentation-impacting changes, update the matching Obsidian note and mention it in the final answer.
