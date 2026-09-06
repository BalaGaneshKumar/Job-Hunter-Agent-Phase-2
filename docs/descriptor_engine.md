# descriptor_engine.py

Fetches the full, untruncated job description for an Adzuna job by
visiting its `redirect_url` and parsing the page's embedded JSON-LD
(`schema.org` `JobPosting`) block — Adzuna's own hosted listing page,
confirmed to return plain HTML with no bot-blocking.

## Key functions
- `classify_link(link)` — sorts an Adzuna `redirect_url` into:
  - `'internal'` — `/details/{id}` (Adzuna's own page, scrapable)
  - `'external'` — `/land/ad/{id}` (redirects straight to the original
    job board, which blocks bots — skipped, no request spent)
  - `'unknown'` — anything else
- `is_job_unavailable(html)` — detects Adzuna's "no longer available"
  notice on an expired listing.
- `fetch_full_description(url, timeout=15, delay=1.0)` — fetches the page
  and returns `(full_text, fail_reason, is_unavailable)`:
  - Tries the JSON-LD `JobPosting.description` first.
  - Falls back to the visible `adp-body` HTML section if no JSON-LD.
  - Converts the found HTML into clean plain text (`_html_to_text`),
    preserving paragraph breaks and bullet points.
  - `is_unavailable=True` tells the caller to mark the job ineligible
    rather than keep retrying it.
  - `delay` adds a politeness pause before each request.

## Used by
- `workflow_engine.py` (Descriptor stage — Adzuna only)

## Notes
- Only used for Adzuna. JSearch and JobsPipe already return full
  descriptions from their search APIs, so this step is skipped for them.
