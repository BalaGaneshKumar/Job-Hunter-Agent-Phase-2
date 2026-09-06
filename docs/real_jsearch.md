# real_jsearch.py

Live JSearch (RapidAPI) client.

## Key function
- `real_search(query, country='in', cursor=None)` — calls
  `GET https://jsearch.p.rapidapi.com/search-v2` with header auth
  (`X-RapidAPI-Key`, `X-RapidAPI-Host`). Cursor-paginated (pass the
  previous response's `data.cursor` to get the next page). Attaches
  `_quota` (limit/remaining) to the returned dict when RapidAPI includes
  rate-limit headers.

## Timeout & retry behavior
- Timeout is 59s (search-v2 does live aggregation, seen taking up to 12s
  normally) — one retry on timeout, then fail.
- 5xx errors: retried up to 3 attempts with backoff (5s, 10s, 20s).
- 4xx errors: not retried, except HTTP 429 which raises the dedicated
  `JSearchQuotaExceeded` exception (monthly quota used up) so callers can
  stop gracefully instead of failing the whole workflow.
- All other raised errors are `RuntimeError`, with API keys redacted from
  error messages via `_redact()`.

## Used by
- `workflow_engine.py` (Scraper Abyss fetch stage for the JSearch portal)

## Notes
- Free tier: 200 requests/month.
- Returns full job descriptions directly — no separate Descriptor step
  needed for this portal.
