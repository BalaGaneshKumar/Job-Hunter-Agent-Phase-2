# dashboard_log.py

Two independent logging channels — server-side system logs vs. client-side
per-tab activity logs.

## Key functions
- `log_event(source, message)` — server-side log, printed to console only
  (startup, DB errors, backup/request errors). Never stored, never shown
  in the browser.
- `add_tab_log(tab, source, message)` — client-side activity log entry for
  one tab (`'career'` or `'profile'`). Stored in-memory, one ring buffer
  per tab (cap 300 entries), never printed to console.
- `get_tab_logs(tab, limit=200)` — returns the most recent entries for a
  tab's Logs panel.

## Notes
- Sub-tabs within a main tab share one bucket — e.g. Applications and Job
  Sites both write into `'career'`; all 9 Profile sub-tabs write into
  `'profile'`. Only the two main tabs are separated from each other.
- Logs are in-memory only — they reset when the server restarts.

## Used by
- `dashboard_server.py`, `workflow_engine.py`, `workflow_store.py`,
  `career_tracker.py`, `jobodyssey_store.py` (via `log_event`)
- `dashboard_server.py`'s `/api/client-log` and `/api/logs` endpoints
  (via `add_tab_log` / `get_tab_logs`)
