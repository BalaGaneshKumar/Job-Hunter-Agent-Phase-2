# dashboard_career.py

Career Tracker tab — two sub-tabs: **Applications** and **Job Sites**.

## Applications sub-tab
- Stats row, search box, stage filter panel (multi-select with OR/NOT
  operator, over stages: Applied, In Progress, Interview, Offer, Rejected,
  Closed, Ghosted, Withdrawn, NA), add/edit/delete rows, export.

## Job Sites sub-tab
- Tracks job-site credentials (name, url, cred, notes).

## Key functions
- `build_career_html()` — full tab HTML (both sub-tabs + Activity Log
  panel shared with Profile Nexus under the `'career'` bucket).
- `build_career_css()` — tab-specific CSS.
- `build_career_js()` — tab behavior: `crSwitchTab`, `crLoad`/`crSave`
  (via `/api/career-load` / `/api/career-save`), search/filter/pagination,
  stage-filter panel logic, export triggers, and `crSendLog` /
  `crLoadLogs` / `crToggleLogPanel` (shared log-panel helpers also used by
  Profile Nexus).

## Used by
- `dashboard_server.py` (embeds this tab's HTML/JS/CSS; backs it with
  `career_tracker.py` via `/api/career-load`, `/api/career-save`)
