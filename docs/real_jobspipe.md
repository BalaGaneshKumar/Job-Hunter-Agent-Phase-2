# real_jobspipe.py

Live JobsPipe API client.

## Key function
- `real_search(keyword, location, limit=10, cursor=None)` — calls
  `POST https://api.jobspipe.dev/v1/jobs/search` with Bearer token auth
  (`Authorization: Bearer jp_live_...`). Cursor-paginated like JSearch.

## Retry behavior
- 5xx errors: retried up to 3 attempts with backoff (5s, 10s, 20s).
- 4xx errors: not retried.
- All raised errors are `RuntimeError`, with the API key redacted from
  error messages via `_redact()`.

## Used by
- `workflow_engine.py` (Scraper Abyss fetch stage for the JobsPipe portal)

## Notes
- Billing: 1 credit = 1 job returned (not 1 credit per call) — the
  `limit` param directly controls cost.
- Free tier: 1,000 jobs/month, resets monthly.
- Returns full, untruncated job descriptions directly (confirmed
  2,100–7,000 chars per job) — no separate Descriptor step needed.
