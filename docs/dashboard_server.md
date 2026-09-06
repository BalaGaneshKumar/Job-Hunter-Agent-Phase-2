# dashboard_server.py

The application's HTTP server. Run with `python dashboard_server.py`,
open `http://localhost:8080`. Built on Python's stdlib `http.server`
(`HTTPServer` + `BaseHTTPRequestHandler`) — no external web framework.

## Page routes (GET)
| Route | Returns |
|---|---|
| `/`, `/dashboard`, `/jobodyssey`, `/career`, `/profile`, `/scraper` | Main dashboard HTML, tab pre-selected |
| `/workflow-detail?id=...` | Standalone Workflow Detail page |

## API routes (GET)
- `/api/career-load`
- `/api/workflow-list`
- `/api/workflow-detail?id=...`
- `/api/workflow-logs?id=...&search=...`
- `/api/jobodyssey-load` (status/portal/location/search/sort/validation/
  linkType filters + pagination)
- `/api/jobodyssey-export` (same filters, unpaginated — full export)
- `/api/jobodyssey-job-detail?id=...`
- `/api/logs?tab=...`

## API routes (POST)
- `/api/save-profile` — writes `profile.json`
- `/api/career-save` — writes both career_apps and career_sites (via
  `career_tracker.py`)
- `/api/scraper-submit` — creates and chains Scraper/Descriptor workflows
  per selected portal (`workflow_store.create_workflow` /
  `create_descriptor_workflow`), starts the first one
  (`workflow_engine.start_workflow`); Descriptor is skipped for JSearch/
  JobsPipe since they already return full descriptions.
- `/api/workflow-action` — hold / cancel / revoke / retry / reset a
  workflow (delegates to `workflow_engine.py`)
- `/api/jobodyssey-status` — updates a job's status
- `/api/client-log` — records a browser-side action log entry for a tab
- `/api/export-file` — generic CSV/XLSX export; color-codes rows by
  `status` (Job Odyssey) or `stage` (Applications) if present. XLSX is
  built with openpyxl in `write_only` mode for speed on large exports.

## Key internals
- `build_dashboard_html(active_tab)` — assembles the full page by calling
  each tab module's `build_*_html()`/`build_*_js()` and wrapping the
  result via `dashboard_ui.html_page`.
- `read_profile()` — reads `profile.json`, returns `{}` if missing/corrupt.
- `_build_xlsx_bytes(rows, keys, labels)` — streaming XLSX writer.
- `DashboardHandler` — the request handler; `send_json`/`send_html`/
  `send_file_download`/`read_body` are shared response/request helpers.

## Depends on
Every other module in this project: `career_tracker`, `dashboard_ui`,
`dashboard_profile`, `dashboard_career`, `dashboard_jobodyssey`,
`dashboard_scraper`, `dashboard_log`, `jobodyssey_store`, `workflow_store`,
`workflow_engine`, `dashboard_workflow_detail`.
