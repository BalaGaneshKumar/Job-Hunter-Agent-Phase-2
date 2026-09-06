# jsearch_config.py

Loads the JSearch (RapidAPI) key from `.env` at import time. Same pattern
as `adzuna_config.py` and `jobspipe_config.py`.

## What it does
- Reads `.env`, sets `os.environ`, exposes `JSEARCH_API_KEY`.
- Prints a startup confirmation showing only the last 4 characters of the
  key, or a warning if it's missing.

## Used by
- `real_jsearch.py` (imports `JSEARCH_API_KEY`)
