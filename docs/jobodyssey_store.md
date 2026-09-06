# jobodyssey_store.py

Data layer for Job Odyssey. Stores every job pulled by Scraper Abyss
workflows in `jobodyssey.db` (SQLite), one row per unique
`(portal, raw_id)` pair.

## Schema
Table `jobs`: id, portal, raw_id, title, company, location, link,
description, posted_date, keyword, search_location, status, validation,
created_at, updated_at.

- `status`: `scraped | eligible | hold | ineligible | blacklist | applied`
- `validation`: `valid | defect` (set by the Validation stage)

## Key functions
- `insert_jobs(rows)` — bulk insert, skips duplicates on `(portal, raw_id)`.
- `load_jobs(...)` / `count_jobs(...)` — filtered, sorted, paginated reads
  (filters: status list + OR/NOT operator, portal, location, search text,
  validation, link_type, is_duplicate).
- `get_stats(...)` — aggregate counts for the stats bar, same filter set.
- `get_filter_options()` — distinct values available for filter dropdowns.
- `get_job(job_id)` — single job detail.
- `update_status(job_id, status)` — used by Eligible/Hold/Ineligible/
  Applied actions (with undo) in the dashboard.
- `get_jobs_needing_description(portal)` / `get_description_locations(portal)`
  — used by the Descriptor stage to find Adzuna jobs still missing a full
  description.
- `update_description(job_id, full_description)` — writes the full
  description fetched by `descriptor_engine.py`.
- `_ensure_schema(conn)` — creates the table/indexes if missing.

## Used by
- `dashboard_server.py` (Job Odyssey API endpoints)
- `workflow_engine.py` (inserting fetched jobs, Descriptor stage lookups)
