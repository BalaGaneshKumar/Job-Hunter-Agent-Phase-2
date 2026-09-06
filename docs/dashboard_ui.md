# dashboard_ui.py

Shared CSS, HTML page wrapper, and small helpers used across every tab.

## Key items
- `CSS` — the full shared stylesheet: header/nav, page/tab switching
  (`.page.active`), stat cards, job cards, filters, badges, status-spinner
  icons, and more. Every tab module (`dashboard_career.py`,
  `dashboard_jobodyssey.py`, `dashboard_scraper.py`,
  `dashboard_workflow_detail.py`) builds on this base and adds its own
  tab-specific CSS on top.
- `html_page(title, body, extra_head='')` — wraps a body string in the
  full `<html>` document, injecting `CSS`.
- `esc(s)` — HTML-escapes a string for safe interpolation.
- `status_icons_json()` — JSON of SVG icon markup keyed by status, shared
  by tabs that show status badges/spinners.
- `render_pagination_js()` — shared pagination widget JS reused by
  Job Odyssey and Career Tracker list views.

## Used by
- `dashboard_server.py` (`html_page`, `render_pagination_js`)
- `dashboard_profile.py`, `dashboard_career.py`, `dashboard_jobodyssey.py`,
  `dashboard_scraper.py`, `dashboard_workflow_detail.py` (CSS base, `esc`,
  `status_icons_json`)
