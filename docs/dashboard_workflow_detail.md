# dashboard_workflow_detail.py

Workflow Detail page — its own standalone page (not a tab), opened when a
Workflow ID is clicked in the Scraper Abyss Workflow list.

## Sections
1. **Details + Actions** — workflow metadata and hold/cancel/revoke/retry/
   reset controls.
2. **Stages progress** — each stage's status (`not_started`, `in_progress`,
   `completed`, `failed`) with icons.
3. **Logs** — search box + per-workflow log lines.

## Status badges
`STATUS_BADGES` maps workflow status → (label, CSS class): waiting,
in_progress, hold, failed, cancelled, completed.

## Key functions
- `build_workflow_detail_page(workflow_id)` — full standalone HTML page
  (uses `dashboard_ui.html_page`, `esc`, `status_icons_json`).
- `build_wfd_css()` — page-specific CSS.
- `build_wfd_js()` — `wfdLoad()` (fetches `/api/workflow-detail` and
  `/api/workflow-logs`), auto-refresh toggle, action buttons (POST to
  `/api/workflow-action`).

## Used by
- `dashboard_server.py` (served at `GET /workflow-detail?id=...`)
