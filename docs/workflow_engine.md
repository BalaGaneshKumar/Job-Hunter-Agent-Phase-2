# workflow_engine.py

Scraper Abyss execution engine. Runs a workflow's stages in a background
thread: **Create order → Fetching N (per keyword+location, split into
cycles) → Validation → Deduplication and Patching → Transmission →
Cleanup → Completed.**

Calls Adzuna, JSearch, and JobsPipe APIs directly via `real_adzuna.py`,
`real_jsearch.py`, `real_jobspipe.py` — no mock layer.

## Control flow
- `run_workflow(workflow_id)` — the main stage loop, invoked in a thread.
- `start_workflow` / `hold_workflow` / `cancel_workflow` / `revoke_workflow`
  / `retry_workflow` / `reset_workflow` — public control functions called
  from `dashboard_server.py`'s `/api/workflow-action` endpoint.
- Hold/cancel/revoke signals are checked between cycles (`_get_control`,
  `_set_control`) so a run can be paused/stopped without killing the
  interpreter.
- `retry_workflow` resumes from the exact cycle within the stage that was
  interrupted (`_skip_to_validation`, `_handle_stop`).
- `_trigger_dependents(workflow_id, ok=True)` — wakes the next workflow in
  a dependency chain (e.g. Scraper → Descriptor) once this one finishes.

## Per-portal fetch stages
- `_run_fetch_stage_adzuna` — pages through Adzuna results.
- `_run_fetch_stage_jsearch` — cursor-paginated, capped at
  `JSEARCH_MAX_CYCLES = 3` cycles per keyword+location (protects the
  200-calls/month free tier).
- `_run_fetch_stage_jobspipe` — one call per keyword+location, capped at
  10 jobs each (protects the 1,000 jobs/month free tier); JobsPipe billing
  is 1 credit per job *returned*, not per call.
- Each has a matching `_normalize_*` function that maps the raw API
  response into the common job shape (`REQUIRED_FIELDS = ['title',
  'company', 'location', 'link', 'description']`).

## Pipeline stages
- `_run_validation_stage` — flags jobs missing required fields as
  `defect` rather than `valid`.
- `_run_blacklist_stage` — filters out jobs matching blacklisted title
  keywords.
- `_collapse_batch_duplicates` / `_run_dedup_stage` — removes duplicates
  within a batch and against jobs already in `jobodyssey.db`.
- `_run_transmission_stage` — writes surviving jobs into `jobodyssey.db`
  via `jobodyssey_store.insert_jobs`.
- `_run_descriptor_create_order` / `_run_descriptor_stage` /
  `_run_descriptor_transmission_stage` — Adzuna-only: fetches full
  descriptions via `descriptor_engine.py` for jobs still missing one, and
  writes them back via `jobodyssey_store.update_description`.

## Used by
- `dashboard_server.py` (`/api/scraper-submit`, `/api/workflow-action`)

## Notes
- JSearch and JobsPipe already return full descriptions from Scraper
  directly, so the Descriptor stage is always skipped for them.
