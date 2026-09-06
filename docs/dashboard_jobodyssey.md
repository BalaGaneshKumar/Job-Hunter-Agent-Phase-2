# dashboard_jobodyssey.py

Job Odyssey tab — browses jobs collected by Scraper Abyss workflows.
Filter bar + stats breakdown + split view (job card list / detail panel).

## Features
- Status filter panel (multi-select, OR/NOT operator, over: scraped,
  eligible, hold, ineligible, blacklist, applied).
- Portal/location/search filters, sort options.
- Actions: Eligible / Hold / Ineligible / Applied — update job status via
  `/api/jobodyssey-status`, with an undo toast.
- Export (CSV/XLSX) via `/api/export-file`.

## Key functions
- `build_jobodyssey_html()` — full tab HTML, including the undo bar and
  filter bar.
- `build_jobodyssey_css()` — tab-specific CSS.
- `build_jobodyssey_js()` — tab behavior: `joLoad` (calls
  `/api/jobodyssey-load`), `joToggleStatusPanel`/`joOnStatusChange`,
  pagination, `joUndo`, job detail panel rendering, export triggers.

## Used by
- `dashboard_server.py` (embeds this tab; backed by `jobodyssey_store.py`
  via `/api/jobodyssey-load`, `/api/jobodyssey-export`,
  `/api/jobodyssey-job-detail`, `/api/jobodyssey-status`)
