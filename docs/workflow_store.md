# workflow_store.py

Scraper Abyss workflow persistence: workflow IDs, per-workflow JSON state
files, and per-workflow logs.

## Storage layout
- `workflows/{workflow_id}.json` — one file per workflow (its full state).
- `temp/{workflow_id}.json` — raw fetch data during a run, removed at the
  Cleanup stage.
- `logs/{workflow_id}.log` — per-workflow logs (isolated from the live
  Activity Log in `dashboard_log.py`).
- `workflow_counter.json` — per-portal counters for ID generation.

## Key functions
- `next_workflow_id(portal, type_code='SCR')` — generates IDs in the
  `WFI{type}{portal_code}{AAA-ZZZ}{0000-9999}` format, independent counter
  per portal, rolling over (e.g. `AAA9999` → `AAB0000`).
- `create_workflow(portal, keywords, locations, blacklist=None, depends_on=None)`
  — creates a new Scraper workflow's stage list and initial state.
- `create_descriptor_workflow(portal, locations, depends_on=None)` —
  creates a Descriptor workflow (Adzuna only).
- `compute_cycles(total_count)` — splits large fetch runs into cycles.
- `find_dependents(workflow_id)` — finds workflows waiting on this one
  (chained portal → descriptor execution).
- `save_workflow(data)` / `load_workflow(workflow_id)` / `list_workflows()`
  — read/write workflow state files.
- `temp_append` / `temp_load` / `temp_save` / `temp_cleanup` — manage
  in-progress fetch data under `temp/`.
- `wf_log(workflow_id, message)` / `wf_get_logs(workflow_id, search=None)`
  — per-workflow log file read/write.
- `keyword_code` / `location_code` / `stage_code` / `descriptor_stage_code`
  — short codes used in stage names/IDs.

## Constants
- `PORTAL_CODES` — `{'Adzuna': 'AD', 'JSearch': 'JS', 'JobsPipe': 'JP'}`
- `STATUS_ORDER` — the six Job Odyssey status values, in pipeline order.

## Used by
- `dashboard_server.py` (workflow list/detail/logs endpoints, submitting
  new scraper requests)
- `workflow_engine.py` (runs the stages this module defines)
