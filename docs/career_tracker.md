# career_tracker.py

Data layer for the Career Tracker tab. Stores applications and job-site
credentials in `career_tracker.db` (SQLite).

## Tables
- `career_apps` — company, link, credential, credtype, passhint, role,
  location, date, stage, substage, ghostedsub, jobid, notes.
- `career_sites` — name, url, cred, notes.

## Key functions
- `load_career_apps()` / `load_career_sites()` — read all rows.
- `save_career_apps(rows)` / `save_career_sites(rows)` — full replace
  (delete all, re-insert). The frontend always sends the whole in-memory
  array on every add/edit/delete, so this reproduces the old CSV
  overwrite-the-file behavior exactly.
- `_ensure_schema(conn)` — creates tables/indexes if missing (called on
  every load/save, so a fresh `career_tracker.db` self-initializes).

## Used by
- `dashboard_server.py` (`/api/career-load`, `/api/career-save`)

## Notes
- All read/write errors are caught and logged via `dashboard_log.log_event`
  under the `'CareerTracker'` tag — save functions return `False` on
  failure rather than raising.
