# Job Hunter Agent — Phase 2

A personal job-search dashboard: fetches job listings via legitimate job-board
APIs (no scraping), stores them in SQLite, and provides a browser dashboard to
review, filter, and track applications end-to-end.

Built with Claude, no prior programming background.

> **Phase 1 note:** an earlier version of this project scraped job portals
> directly with Selenium. That approach was stopped and archived separately
> because those portals' Terms of Service prohibit automated scraping. Phase 2
> is a full rebuild on official APIs (Adzuna, JSearch, JobsPipe) instead.

## Features

- **Scraper Abyss** — configure keyword/location/portal combinations and run
  a background workflow that fetches jobs from live job-board APIs.
- **Job Odyssey** — browse, filter, and triage fetched jobs (Scraped →
  Eligible / Hold / Ineligible / Blacklist → Applied).
- **Career Tracker** — track applications and job-site credentials in one
  place, independent of the scraper.
- **Profile Nexus** — a single structured profile (personal info, education,
  experience, work auth, etc.) reusable across applications.
- **Workflow Detail** — live progress view per workflow run: stages, logs,
  hold/cancel/retry controls.

## Architecture

```
dashboard_server.py        HTTP server — routes, static page assembly, API endpoints
├── dashboard_ui.py         Shared CSS / page shell
├── dashboard_profile.py    Profile Nexus tab (reads/writes profile.json)
├── dashboard_career.py     Career Tracker tab (Applications + Job Sites)
├── dashboard_jobodyssey.py Job Odyssey tab (job browser/filter/actions)
├── dashboard_scraper.py    Scraper Abyss tab (request builder + workflow list)
├── dashboard_workflow_detail.py  Per-workflow detail page
└── dashboard_log.py        Server console logs + per-tab in-memory activity logs

workflow_engine.py          Background pipeline: fetch → validate → dedupe → store
├── real_adzuna.py           Adzuna API client
├── real_jsearch.py          JSearch (RapidAPI) client
├── real_jobspipe.py         JobsPipe API client
└── descriptor_engine.py     Fetches full job descriptions for Adzuna listings
                              (Adzuna's search API only returns a short snippet)

workflow_store.py           Workflow IDs, per-workflow JSON state (workflows/), logs
jobodyssey_store.py         SQLite (jobodyssey.db) — all fetched jobs
career_tracker.py           SQLite (career_tracker.db) — applications + job sites

adzuna_config.py / jsearch_config.py / jobspipe_config.py
                             Load each API's credentials from .env
```

## Data stored locally (not in version control)

| File / folder            | Contents                                  |
|---------------------------|--------------------------------------------|
| `.env`                    | API credentials                            |
| `jobodyssey.db`           | All fetched jobs                           |
| `career_tracker.db`       | Applications + job sites                   |
| `profile.json`            | Personal profile data                      |
| `workflows/`, `temp/`, `logs/` | Per-run workflow state and logs       |
| `workflow_counter.json`   | Workflow ID counter                        |
| `resume.pdf`, `cover_letter.pdf` | Personal documents                  |
| `__pycache__/`            | Python bytecode cache                      |

## Setup

**Prerequisite:** Python 3.9+ must be installed. If it isn't, download it from
[python.org/downloads](https://www.python.org/downloads/) (on Windows, check
"Add python.exe to PATH" during install). Verify with:
```
python --version
```

1. Clone the repo and install dependencies:
   ```
   pip install requests
   ```
2. Copy `.env.example` to `.env` and fill in your API keys (see the setup
   guide for how to get each one).
3. Run the server:
   ```
   python dashboard_server.py
   ```
4. Open `http://localhost:8080`.

See `SETUP_GUIDE.md` for cloning and API-key creation steps in detail.

## Job sources

| Portal   | Auth style              | Free tier        | Notes |
|----------|--------------------------|-------------------|-------|
| Adzuna   | `app_id` + `app_key` (URL params) | — | Full description fetched separately via `descriptor_engine.py` |
| JSearch  | RapidAPI header key      | 200 calls/month   | Cursor-paginated |
| JobsPipe | Bearer token             | 1,000 jobs/month  | Returns full description directly |

## Status

Phase 2 (this repo) is a dev/QA validation stage for the SQLite-based storage
and API-driven fetch pipeline before it carries into Phase 3 (new portal
integrations, AI-powered job matching, cover-letter generation, and a UI
redesign).

## Disclaimer

Personal project for individual job-search use. No license is currently
attached (portfolio/demonstration only, not intended for reuse).
