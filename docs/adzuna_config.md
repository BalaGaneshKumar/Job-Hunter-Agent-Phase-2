# adzuna_config.py

Loads Adzuna API credentials from `.env` at import time. Credentials are
never hardcoded in this file and never logged in full.

## What it does
- Reads `.env` (simple `KEY=value` line parser, skips blanks/comments).
- Sets `os.environ` from it, then exposes:
  - `ADZUNA_APP_ID`
  - `ADZUNA_APP_KEY`
- Prints a startup confirmation showing only the last 4 characters of the
  app ID, or a warning if credentials are missing/still placeholders.

## Used by
- `real_adzuna.py` (imports `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`)

## Notes
- `.env` must sit next to this file and must never be committed to git.
