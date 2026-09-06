# dashboard_profile.py

Profile Nexus tab — a single structured personal-data form, saved to
`profile.json`. Split into 9 sub-tabs so a long form doesn't force
scrolling past unrelated sections.

## Sub-tabs
Personal Information, Education, Experience, Work History (repeatable job
entries), EEO Information, Work Authorization, India Specific, Social &
Links, Skills & Preferences.

## Key functions
- `build_profile_html(prof_json)` — returns the tab's HTML, including the
  sub-nav and all 9 sub-pages, plus an Activity Log panel (shares the
  `/api/logs` feed with the Career tab, under the `'profile'` bucket).
- `build_profile_js(prof_json)` — returns the tab's JS:
  - `fillProfileForm(data)` / `collectProfile()` — populate/read the form.
  - `renderJobEntry` / `addJob` / `removeJob` — repeatable Work History
    entries.
  - `pfSwitchSub(id, btn)` — sub-tab switching.
  - `saveProfile()` — POSTs to `/api/save-profile`, logs the result via
    `crSendLog('pf', ...)`.

## Used by
- `dashboard_server.py` (embeds this tab's HTML/JS into the main page,
  serves/saves `profile.json` via `/api/save-profile`)

## Notes
- Uses the shared sub-nav/sub-page CSS already defined in `dashboard_ui.py`.
