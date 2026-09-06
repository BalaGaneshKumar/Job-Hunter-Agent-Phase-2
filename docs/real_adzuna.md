# real_adzuna.py

Live Adzuna API client.

## Key function
- `real_search(what, where, page=1, results_per_page=20)` — calls
  `GET https://api.adzuna.com/v1/api/jobs/in/search/{page}` with
  `app_id`/`app_key` (from `adzuna_config.py`), `what` (keyword), `where`
  (location), and `results_per_page` (capped at 50, Adzuna's documented
  max). Returns the parsed JSON response.

## Retry behavior
- 5xx errors: retried up to 3 attempts with backoff (5s, 10s, 20s).
- 4xx errors: not retried (won't fix themselves).
- All raised errors are `RuntimeError`, with `app_id`/`app_key` redacted
  from any error message via `_redact()`.

## Used by
- `workflow_engine.py` (Scraper Abyss fetch stage for the Adzuna portal)

## Notes
- Adzuna's search response only contains a short description snippet —
  `descriptor_engine.py` is used separately to fetch the full description.
