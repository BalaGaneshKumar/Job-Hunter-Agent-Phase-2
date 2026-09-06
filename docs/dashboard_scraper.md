# dashboard_scraper.py

Scraper Abyss tab — where new fetch workflows are configured and launched.
Two sub-tabs: **Request** and **Workflow**.

## Request sub-tab
Cascading selection: Engine (Scraper / Descriptor) → Portal → Keyword →
Location, each with select-all and editable tag lists. Submit is gated on
all required selections having at least one entry. Also holds an editable
blacklist (title keywords to exclude), defaulting to `DEFAULT_BLACKLIST`
(`Senior, Lead, Principal, Staff, Manager, Walk In`).

## Workflow sub-tab
Lists past/running workflows (from `workflow_store.list_workflows()`),
links to the Workflow Detail page per workflow.

## Defaults
- `DEFAULT_KEYWORDS` — 10 role titles (Technical Support Engineer, etc.)
- `DEFAULT_LOCATIONS` — `Chennai, Coimbatore, Bangalore`
- `DEFAULT_BLACKLIST` — see above

## Key functions
- `build_scraper_html()` — full tab HTML.
- `build_scraper_css()` — tab-specific CSS.
- `build_scraper_js()` — tab behavior: `saSwitchTab`, `saSelectAll`,
  request submission (POSTs to `/api/scraper-submit`), workflow list
  rendering.

## Used by
- `dashboard_server.py` (embeds this tab; `/api/scraper-submit` creates
  workflows via `workflow_store.py` and starts them via
  `workflow_engine.py`)
