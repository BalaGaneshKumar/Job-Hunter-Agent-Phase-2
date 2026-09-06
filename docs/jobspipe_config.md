# jobspipe_config.py

Loads the JobsPipe API key from `.env` at import time. Same pattern as
`adzuna_config.py` and `jsearch_config.py`.

## What it does
- Reads `.env`, sets `os.environ`, exposes `JOBSPIPE_API_KEY`.
- Prints a startup confirmation showing only the last 4 characters of the
  key, or a warning if it's missing.

## Used by
- `real_jobspipe.py` (imports `JOBSPIPE_API_KEY`)
