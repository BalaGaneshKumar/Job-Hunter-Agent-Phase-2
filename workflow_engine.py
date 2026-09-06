"""
workflow_engine.py — Scraper Abyss execution engine
Runs a workflow's stages in a background thread: Create order -> Fetching N
(one per keyword+location combo, split into cycles) -> Validation ->
Deduplication and Patching -> Transmission -> Cleanup -> Completed.

Control signals (hold/cancel/revoke) are checked between cycles so a
workflow can be paused/stopped without killing the interpreter. Retry
resumes from the exact cycle within the stage that was interrupted.

Adzuna and JSearch both call their real APIs directly (real_adzuna.py,
real_jsearch.py) — no mock layer in this file.
"""

import re
import threading
import time

from real_adzuna import real_search
from real_jsearch import real_search as _real_jsearch_search, JSearchQuotaExceeded
from real_jobspipe import real_search as _real_jobspipe_search
from descriptor_engine import fetch_full_description, classify_link
from dashboard_log import add_tab_log, log_event
import workflow_store as ws
from jobodyssey_store import (
    insert_jobs, get_job, update_status, update_description,
    get_jobs_needing_description, _get_conn as jo_conn, _ensure_schema as jo_schema
)

REQUIRED_FIELDS = ['title', 'company', 'location', 'link', 'description']

# Caps real API calls per keyword+location so one Scraper run can't
# accidentally burn a large chunk of JSearch's 200-calls/month free tier
# (an Adzuna-style run can hit 50+ calls for comparison).
JSEARCH_MAX_CYCLES = 3

# JobsPipe: 1 credit = 1 job RETURNED, not 1 credit per call — so cost is
# controlled directly by the per-call limit, not by a cycle count. Free
# tier is 1,000 jobs/month, resets monthly.
# One call per keyword+location, capped at 10 jobs each — confirmed via
# direct testing that all 10 came back with full, untruncated
# descriptions (2,100–7,000 chars), so no Descriptor step is needed here
# either, same treatment as JSearch.
JOBSPIPE_MAX_CYCLES = 1
JOBSPIPE_JOBS_PER_CALL = 10

# workflow_id -> 'run' | 'hold' | 'cancel' | 'revoke'
_control = {}
_control_lock = threading.Lock()


def _set_control(workflow_id, signal):
    with _control_lock:
        _control[workflow_id] = signal

def _get_control(workflow_id):
    with _control_lock:
        return _control.get(workflow_id, 'run')

def _wflog(workflow_id, message):
    """Per-workflow log file only — every stage/cycle detail goes here."""
    ws.wf_log(workflow_id, message)

def _activity(workflow_id, message):
    """Live Activity Log — only major lifecycle events (triggered/completed/
    failed/cancelled/held/etc.), never per-cycle noise."""
    ws.wf_log(workflow_id, message)
    add_tab_log('scraper', 'ScraperAbyss', '[' + workflow_id + '] ' + message)


# ---------------------------------------------------------------------------
# Fetch — both portals call their real APIs directly
# ---------------------------------------------------------------------------
def _fetch_page(what, where, page, results_per_page):
    return real_search(what, where, page=page, results_per_page=results_per_page)


def _normalize(portal, raw_job, keyword, location):
    link = raw_job.get('redirect_url', '')
    return {
        'portal': portal,
        'raw_id': str(raw_job.get('id', '')),
        'title': raw_job.get('title', ''),
        'company': (raw_job.get('company') or {}).get('display_name', ''),
        'location': (raw_job.get('location') or {}).get('display_name', ''),
        'link': link,
        'link_type': classify_link(link),
        'description': raw_job.get('description', ''),
        'posted_date': raw_job.get('created', ''),
        'keyword': keyword,
        'search_location': location,
    }


def _validate(job):
    missing = [f for f in REQUIRED_FIELDS if not job.get(f)]
    job['validation'] = 'defect' if missing else 'valid'
    return job


def _fetch_jsearch_page(query, cursor):
    return _real_jsearch_search(query, country='in', cursor=cursor)


def _normalize_jsearch(raw_job, keyword, location):
    apply_link = raw_job.get('job_apply_link', '')
    return {
        'portal': 'JSearch',
        'raw_id': str(raw_job.get('job_id', '')),
        'title': raw_job.get('job_title', ''),
        'company': raw_job.get('employer_name', ''),
        'location': raw_job.get('job_city', '') or location,
        'link': apply_link,
        # Always external — JSearch's apply link goes straight to the
        # employer's own site, never a scrapable intermediate page like
        # Adzuna's /details/ pages, so Descriptor never applies here.
        'link_type': 'external',
        'description': raw_job.get('job_description', ''),
        # Full text always comes back with the search response — nothing
        # left for a Descriptor stage to enrich.
        'description_full': 1,
        'posted_date': raw_job.get('job_posted_at_datetime_utc', ''),
        'keyword': keyword,
        'search_location': location,
    }


def _fetch_jobspipe_page(keyword, location, cursor=None):
    return _real_jobspipe_search(keyword, location, limit=JOBSPIPE_JOBS_PER_CALL, cursor=cursor)


def _normalize_jobspipe(raw_job, keyword, location):
    # final_url is the resolved/canonical destination when JobsPipe has
    # one; it's often null (as seen in testing), so fall back to the
    # direct source link (e.g. the LinkedIn posting URL itself).
    link = raw_job.get('final_url') or raw_job.get('url') or raw_job.get('source_url', '')
    return {
        'portal': 'JobsPipe',
        'raw_id': str(raw_job.get('id', '')),
        'title': raw_job.get('job_title', ''),
        'company': raw_job.get('company', ''),
        'location': raw_job.get('location', '') or location,
        'link': link,
        # Always external — this points at the source board (LinkedIn,
        # Workday, etc.), not a page we'd ever need to scrape further,
        # since the API already hands back the complete description.
        'link_type': 'external',
        # Confirmed via direct testing: full, untruncated description
        # text (2,100–7,000 chars across a real 10-job sample) — nothing
        # left for a Descriptor stage to enrich, same as JSearch.
        'description': raw_job.get('description', ''),
        'description_full': 1,
        'posted_date': raw_job.get('date_posted', ''),
        'keyword': keyword,
        'search_location': location,
    }


# ---------------------------------------------------------------------------
# Main run loop
# ---------------------------------------------------------------------------
def _trigger_dependents(workflow_id, ok=True):
    """Called the moment a workflow reaches a real terminal state (completed,
    failed, cancelled, or revoked — never 'hold', which is a pause, not a
    finish). Wakes any workflow that was waiting on this one, starting it
    for the first time. This replaces the old polling-based wait, which
    could read another workflow's file mid-write and misread it as done."""
    for dep_id in ws.find_dependents(workflow_id):
        if not ok:
            _wflog(dep_id, 'Dependency ' + workflow_id + ' did not complete successfully — starting anyway')
        else:
            _wflog(dep_id, 'Dependency ' + workflow_id + ' completed — starting now')
        start_workflow(dep_id)


def _skip_to_validation(workflow_id, data, start_index):
    """Called when JSearch's monthly quota runs out mid-run. Marks every
    not-yet-attempted Fetching stage from start_index onward 'completed'
    (not 'failed' — nothing went wrong with them, they just weren't run)
    and jumps straight to the Validation stage. Without this, one
    exhausted quota used to fail the ENTIRE workflow and lose every job
    already collected from the fetch stages that succeeded before it —
    this way that work still goes through Validation -> Blacklist ->
    Dedup -> Transmission -> Cleanup normally, and the run shows as a
    clean completed pipeline rather than looking stalled or broken.
    The full explanation (which stages were skipped, and why) still goes
    to this workflow's own log — this only affects the stage badge shown
    in the pipeline diagram, not the record of what actually happened."""
    stages = data['stages']
    skipped_count = 0
    validation_idx = None
    for idx in range(start_index, len(stages)):
        s = stages[idx]
        if s['name'] == 'Validation':
            validation_idx = idx
            break
        if s.get('type') == 'fetch' and s['status'] in ('not_started', 'in_progress'):
            s['status'] = 'completed'
            skipped_count += 1
    if validation_idx is None:
        # Defensive fallback — every Scraper workflow should have a
        # Validation stage after its fetch stages; if it's somehow
        # missing, just continue to the next stage rather than crash.
        validation_idx = start_index
    data['current_stage_index'] = validation_idx
    ws.save_workflow(data)
    _activity(workflow_id, 'JSearch monthly quota exhausted — skipped ' + str(skipped_count) +
               ' remaining fetch stage(s), proceeding to Validation with the jobs already collected')
    return validation_idx


def run_workflow(workflow_id):
    _set_control(workflow_id, 'run')
    data = ws.load_workflow(workflow_id)
    if not data:
        return

    data['status'] = 'in_progress'
    if not data.get('started_at'):
        data['started_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
    ws.save_workflow(data)
    _activity(workflow_id, 'Workflow started')

    stages = data['stages']
    i = data['current_stage_index']

    while i < len(stages):
        signal = _get_control(workflow_id)
        if signal in ('hold', 'cancel', 'revoke'):
            _handle_stop(workflow_id, data, signal, i)
            return

        stage = stages[i]
        name = stage['name']
        stage['status'] = 'in_progress'
        data['current_stage_index'] = i
        ws.save_workflow(data)

        quota_skip = False
        try:
            if name == 'Create order':
                if data.get('kind') == 'descriptor':
                    _run_descriptor_create_order(workflow_id, data)
                else:
                    _wflog(workflow_id, 'Stage "Create order" completed — stages generated')

            elif stage.get('type') == 'fetch':
                result = _run_fetch_stage(workflow_id, data, stage)
                if result is False:
                    return  # stopped mid-stage (hold/cancel/revoke)
                if result == 'quota_exceeded':
                    quota_skip = True

            elif stage.get('type') == 'descriptor':
                if not _run_descriptor_stage(workflow_id, data, stage):
                    return  # stopped mid-stage (hold/cancel/revoke)

            elif name == 'Validation':
                _run_validation_stage(workflow_id, data)

            elif name == 'Blacklist':
                _run_blacklist_stage(workflow_id, data)

            elif name == 'Deduplication and Patching':
                _run_dedup_stage(workflow_id, data)

            elif name == 'Transmission':
                if data.get('kind') == 'descriptor':
                    _run_descriptor_transmission_stage(workflow_id, data)
                else:
                    _run_transmission_stage(workflow_id, data)

            elif name == 'Cleanup':
                time.sleep(1)
                ws.temp_cleanup(workflow_id)
                _wflog(workflow_id, 'Temp file removed')

            elif name == 'Completed':
                stage['status'] = 'completed'
                data['status'] = 'completed'
                ws.save_workflow(data)
                _activity(workflow_id, 'Workflow completed')
                _trigger_dependents(workflow_id, ok=True)
                return

        except Exception as e:
            stage['status'] = 'failed'
            data['status'] = 'failed'
            data['current_stage_index'] = i
            ws.save_workflow(data)
            _activity(workflow_id, 'Stage "' + name + '" FAILED: ' + str(e)[:150])
            _trigger_dependents(workflow_id, ok=False)
            return

        if quota_skip:
            # Marked 'completed', not 'skipped' — this stage DID collect
            # some jobs before quota ran out, and showing it as anything
            # other than green would make an otherwise-successful run look
            # broken in the pipeline diagram. The log line already records
            # that this and the following stages were skipped, and why.
            stage['status'] = 'completed'
            i = _skip_to_validation(workflow_id, data, i + 1)
            continue

        stage['status'] = 'completed'
        data['current_stage_index'] = i + 1
        ws.save_workflow(data)
        i += 1

    data['status'] = 'completed'
    ws.save_workflow(data)


def _handle_stop(workflow_id, data, signal, stage_index):
    if signal == 'hold':
        data['status'] = 'hold'
        _activity(workflow_id, 'Workflow held — resumable from current cycle')
    elif signal == 'cancel':
        data['status'] = 'cancelled'
        for j in range(stage_index, len(data['stages'])):
            if data['stages'][j]['status'] == 'in_progress':
                data['stages'][j]['status'] = 'not_started'
        _activity(workflow_id, 'Workflow cancelled — stopped immediately')
    elif signal == 'revoke':
        data['status'] = 'failed'
        if stage_index < len(data['stages']):
            data['stages'][stage_index]['status'] = 'failed'
            if data['stages'][stage_index].get('type') == 'fetch':
                data['stages'][stage_index]['cycles_done'] = 0  # lose current stage progress
        _activity(workflow_id, 'Workflow revoked — force stopped, current stage progress lost')
    data['current_stage_index'] = stage_index
    ws.save_workflow(data)
    if signal in ('cancel', 'revoke'):
        _trigger_dependents(workflow_id, ok=False)


def _run_fetch_stage(workflow_id, data, stage):
    if data['portal'] == 'JSearch':
        return _run_fetch_stage_jsearch(workflow_id, data, stage)
    if data['portal'] == 'JobsPipe':
        return _run_fetch_stage_jobspipe(workflow_id, data, stage)
    return _run_fetch_stage_adzuna(workflow_id, data, stage)


def _run_fetch_stage_adzuna(workflow_id, data, stage):
    kw, loc = stage['keyword'], stage['location']

    if stage['cycles_total'] is None:
        first = _fetch_page(kw, loc, page=1, results_per_page=1)
        total_count = first['count']
        sizes = ws.compute_cycles(total_count)
        stage['cycles_total'] = len(sizes)
        stage['cycle_sizes'] = sizes
        stage['total_count'] = total_count
        ws.save_workflow(data)
        _wflog(workflow_id, stage['name'] + ' (' + stage['stage_code'] + '): ' +
                   str(total_count) + ' jobs found, split into ' + str(len(sizes)) + ' cycle(s)')

    sizes = stage['cycle_sizes']
    start_cycle = stage['cycles_done']

    for c in range(start_cycle, len(sizes)):
        signal = _get_control(workflow_id)
        if signal in ('hold', 'cancel', 'revoke'):
            _handle_stop(workflow_id, data, signal, data['current_stage_index'])
            return False

        size = sizes[c]
        page_result = _fetch_page(kw, loc, page=c + 1, results_per_page=size)
        raw_jobs = page_result.get('results', [])
        normalized = [_validate(_normalize(data['portal'], rj, kw, loc)) for rj in raw_jobs]
        ws.temp_append(workflow_id, normalized)

        stage['cycles_done'] = c + 1
        ws.save_workflow(data)
        _wflog(workflow_id, stage['name'] + ' cycle ' + str(c + 1) + '/' + str(len(sizes)) +
                   ' complete — ' + str(len(normalized)) + ' jobs collected')
        time.sleep(2.5)  # simulated work time — long enough to test Hold/Cancel/Revoke between cycles

    return True


def _run_fetch_stage_jsearch(workflow_id, data, stage):
    kw, loc = stage['keyword'], stage['location']

    if stage['cycles_total'] is None:
        stage['cycles_total'] = JSEARCH_MAX_CYCLES
        stage['cursor'] = None
        ws.save_workflow(data)
        _wflog(workflow_id, stage['name'] + ' (' + stage['stage_code'] + '): up to ' +
                   str(JSEARCH_MAX_CYCLES) + ' cycle(s), 10 jobs each, cursor-paginated' +
                   ' [LIVE — uses real quota]')

    start_cycle = stage['cycles_done']
    cursor = stage.get('cursor')
    query = kw + ' in ' + loc

    for c in range(start_cycle, stage['cycles_total']):
        signal = _get_control(workflow_id)
        if signal in ('hold', 'cancel', 'revoke'):
            _handle_stop(workflow_id, data, signal, data['current_stage_index'])
            return False

        # Reactive case: quota ran out between our last successful call and
        # this one (e.g. resuming a previously-interrupted run in the same
        # month). Caught here specifically so it can skip ahead instead of
        # failing the whole workflow like any other API error would.
        try:
            page_result = _fetch_jsearch_page(query, cursor)
        except JSearchQuotaExceeded as e:
            _wflog(workflow_id, str(e))
            return 'quota_exceeded'

        page_data = page_result.get('data', {}) or {}
        raw_jobs = page_data.get('jobs', [])
        cursor = page_data.get('cursor')

        normalized = [_validate(_normalize_jsearch(rj, kw, loc)) for rj in raw_jobs]
        ws.temp_append(workflow_id, normalized)

        stage['cycles_done'] = c + 1
        stage['cursor'] = cursor
        ws.save_workflow(data)
        _wflog(workflow_id, stage['name'] + ' cycle ' + str(c + 1) + '/' + str(stage['cycles_total']) +
                   ' complete — ' + str(len(normalized)) + ' jobs collected')

        quota = page_result.get('_quota')
        if quota:
            _wflog(workflow_id, 'JSearch quota: ' + str(quota['remaining']) + '/' +
                       str(quota['limit']) + ' calls remaining this month')
            # Proactive case: this call succeeded, but it was the last one
            # left this month. Stop here rather than spending one more
            # cycle finding that out the hard way via a 429.
            if str(quota['remaining']) == '0':
                _wflog(workflow_id, stage['name'] + ': JSearch monthly quota fully used — ' +
                           'stopping further JSearch fetches this run')
                return 'quota_exceeded'

        if not cursor:
            _wflog(workflow_id, stage['name'] + ': no cursor returned — no more results, stopping early')
            break
        time.sleep(2.5)

    return True


def _run_fetch_stage_jobspipe(workflow_id, data, stage):
    kw, loc = stage['keyword'], stage['location']

    if stage['cycles_total'] is None:
        stage['cycles_total'] = JOBSPIPE_MAX_CYCLES
        stage['cursor'] = None
        ws.save_workflow(data)
        _wflog(workflow_id, stage['name'] + ' (' + stage['stage_code'] + '): up to ' +
                   str(JOBSPIPE_MAX_CYCLES) + ' cycle(s), ' + str(JOBSPIPE_JOBS_PER_CALL) +
                   ' jobs each, cursor-paginated [LIVE — 1 credit per job returned, 1,000/month free]')

    start_cycle = stage['cycles_done']
    cursor = stage.get('cursor')

    for c in range(start_cycle, stage['cycles_total']):
        signal = _get_control(workflow_id)
        if signal in ('hold', 'cancel', 'revoke'):
            _handle_stop(workflow_id, data, signal, data['current_stage_index'])
            return False

        page_result = _fetch_jobspipe_page(kw, loc, cursor=cursor)
        raw_jobs = page_result.get('data', [])
        cursor = (page_result.get('metadata') or {}).get('next_cursor')

        normalized = [_validate(_normalize_jobspipe(rj, kw, loc)) for rj in raw_jobs]
        ws.temp_append(workflow_id, normalized)

        stage['cycles_done'] = c + 1
        stage['cursor'] = cursor
        ws.save_workflow(data)
        _wflog(workflow_id, stage['name'] + ' cycle ' + str(c + 1) + '/' + str(stage['cycles_total']) +
                   ' complete — ' + str(len(normalized)) + ' jobs collected')

        if not cursor:
            _wflog(workflow_id, stage['name'] + ': no cursor returned — no more results, stopping early')
            break
        time.sleep(2.5)

    return True


def _run_validation_stage(workflow_id, data):
    time.sleep(1.5)
    jobs = ws.temp_load(workflow_id)
    valid = sum(1 for j in jobs if j.get('validation') == 'valid')
    defect = len(jobs) - valid
    _wflog(workflow_id, 'Validation complete — ' + str(valid) + ' valid, ' + str(defect) + ' defect')


def _run_blacklist_stage(workflow_id, data):
    time.sleep(1.5)
    keywords = data.get('blacklist') or []
    jobs = ws.temp_load(workflow_id)
    if not keywords:
        _wflog(workflow_id, 'Blacklist complete — no keywords selected for this request, nothing checked')
        return

    # Each keyword matches both its normal spelling ("walk in") and the
    # fully-joined one-word spelling ("walkin") — real postings write
    # compound phrases like this inconsistently, and a hyphen-to-space
    # swap alone doesn't catch a genuinely single, unbroken word. For a
    # single-word keyword (e.g. "Senior"), both variants are identical,
    # so this has no effect on them at all.
    patterns = []
    for kw in keywords:
        kw_lower = kw.lower()
        variants = {kw_lower, kw_lower.replace(' ', '')}
        alternation = '|'.join(re.escape(v) for v in variants)
        patterns.append(re.compile(r'\b(?:' + alternation + r')\b'))

    def is_match(title):
        t = (title or '').lower().replace('-', ' ')
        return any(p.search(t) for p in patterns)

    # Fresh batch only — jobs fetched in this run, not yet in the DB.
    # No retroactive sweep of pre-existing DB rows (by design).
    matched = 0
    for j in jobs:
        if is_match(j.get('title')):
            j['status'] = 'blacklist'
            matched += 1
    ws.temp_save(workflow_id, jobs)

    _wflog(workflow_id, 'Blacklist complete — ' + str(matched) + '/' + str(len(jobs)) +
           ' job(s) matched in this batch (' + ', '.join(keywords) + ')')


def _collapse_batch_duplicates(jobs):
    """Two fetch cycles in the same run (different keyword/location combos)
    can pull the identical Adzuna listing, giving the batch two dicts with
    the same (portal, raw_id). Left alone, both would reach insert_jobs(),
    the DB's UNIQUE(portal, raw_id) would let only the first one in via
    INSERT OR IGNORE, and whichever copy lost the race silently vanishes —
    including its status if it was the one Blacklist had matched. Collapse
    them here first: keep 'blacklist' status if either copy has it, prefer
    a 'valid' copy over a 'defect' one, and patch any fields the losing
    copy has that the surviving one is missing."""
    merged = {}
    order = []
    for j in jobs:
        key = (j.get('portal', ''), j.get('raw_id', ''))
        if key not in merged:
            merged[key] = j
            order.append(key)
            continue
        existing = merged[key]
        if j.get('validation') == 'valid' and existing.get('validation') != 'valid':
            keep_status = 'blacklist' if existing.get('status') == 'blacklist' else j.get('status')
            existing = dict(j)
            existing['status'] = keep_status
        else:
            for f in REQUIRED_FIELDS:
                if not existing.get(f) and j.get(f):
                    existing[f] = j[f]
            if j.get('status') == 'blacklist':
                existing['status'] = 'blacklist'
        merged[key] = existing
    collapsed_count = len(jobs) - len(order)
    return [merged[k] for k in order], collapsed_count


def _run_dedup_stage(workflow_id, data):
    time.sleep(1.5)
    jobs = ws.temp_load(workflow_id)
    jobs, collapsed = _collapse_batch_duplicates(jobs)
    conn = jo_conn()
    jo_schema(conn)
    kept = []
    removed = 0
    patched = 0
    for j in jobs:
        cur = conn.execute('SELECT * FROM jobs WHERE portal = ? AND raw_id = ?', (j['portal'], j['raw_id']))
        row = cur.fetchone()
        if row is None:
            kept.append(j)
            continue
        existing = dict(row)
        if existing['validation'] == 'valid':
            removed += 1  # already have a good copy — dedup
            continue
        # existing is defect — patch any fields temp has that master is missing
        changed = False
        for f in REQUIRED_FIELDS:
            if not existing.get(f) and j.get(f):
                existing[f] = j[f]
                changed = True
        if changed:
            still_missing = [f for f in REQUIRED_FIELDS if not existing.get(f)]
            new_validation = 'defect' if still_missing else 'valid'
            with conn:
                conn.execute(
                    'UPDATE jobs SET title=?, company=?, location=?, link=?, description=?, validation=?, '
                    "updated_at=datetime('now') WHERE portal=? AND raw_id=?",
                    (existing['title'], existing['company'], existing['location'], existing['link'],
                     existing['description'], new_validation, j['portal'], j['raw_id'])
                )
            patched += 1
        removed += 1  # either patched or left as-is — remove from temp either way

    # Duplicate detection — same title, company, description AND location
    # already exist under a different job ID (portals sometimes repost the
    # identical listing). If ANY of these differ, it's a genuinely different
    # role/location, not a duplicate. Confirmed reliable after manual review
    # of flagged jobs — duplicates are now auto-marked ineligible, not just
    # visually flagged.
    dup_flagged = 0
    for j in kept:
        desc = (j.get('description') or '').strip()
        title = (j.get('title') or '').strip()
        company = (j.get('company') or '').strip()
        location = (j.get('location') or '').strip()
        if not desc or not title:
            continue
        cur = conn.execute(
            'SELECT 1 FROM jobs WHERE title = ? AND company = ? AND description = ? AND location = ? AND '
            '(portal != ? OR raw_id != ?) LIMIT 1',
            (title, company, desc, location, j.get('portal', ''), j.get('raw_id', ''))
        )
        if cur.fetchone():
            j['is_duplicate'] = 1
            if j.get('status') != 'blacklist':
                j['status'] = 'ineligible'
            dup_flagged += 1
    # also catch duplicates that only exist within this same batch
    seen = {}
    for j in kept:
        desc = (j.get('description') or '').strip()
        title = (j.get('title') or '').strip()
        company = (j.get('company') or '').strip()
        location = (j.get('location') or '').strip()
        if not desc or not title:
            continue
        key = (title, company, desc, location)
        if key in seen:
            j['is_duplicate'] = 1
            if j.get('status') != 'blacklist':
                j['status'] = 'ineligible'
            dup_flagged += 1
        else:
            seen[key] = j

    conn.close()
    ws.temp_save(workflow_id, kept)
    _wflog(workflow_id, 'Dedup/patch complete — ' + str(collapsed) + ' in-batch collision(s) merged, ' +
               str(removed) + ' removed (' + str(patched) +
               ' patched), ' + str(len(kept)) + ' new job(s) remain for transmission, ' +
               str(dup_flagged) + ' flagged as duplicate description')


def _run_transmission_stage(workflow_id, data):
    time.sleep(1.5)
    jobs = ws.temp_load(workflow_id)
    result = insert_jobs(jobs)
    if result is False:
        _wflog(workflow_id, 'Transmission FAILED — see error log')
    else:
        skipped = len(jobs) - result
        note = '' if skipped == 0 else ' (' + str(skipped) + ' already existed from a prior run, skipped)'
        _wflog(workflow_id, 'Transmission complete — ' + str(result) + '/' + str(len(jobs)) +
                   ' job(s) written to main DB' + note)


# ---------------------------------------------------------------------------
# Descriptor engine — enriches full descriptions for existing jobs
# ---------------------------------------------------------------------------
def _run_descriptor_create_order(workflow_id, data):
    jobs = get_jobs_needing_description(data['portal'])
    ws.temp_save(workflow_id, jobs)
    _wflog(workflow_id, 'Create order complete — ' + str(len(jobs)) +
           ' job(s) missing full description, saved to temp')


def _run_descriptor_stage(workflow_id, data, stage):
    location = stage['location']
    all_jobs = ws.temp_load(workflow_id)
    target_jobs = [j for j in all_jobs if j.get('search_location') == location and not j.get('description_full')]

    if stage['jobs_total'] is None:
        stage['jobs_total'] = len(target_jobs)
        ws.save_workflow(data)
        _wflog(workflow_id, stage['name'] + ' (' + stage['stage_code'] + '): ' +
               str(len(target_jobs)) + ' job(s) to enrich')

    start_idx = stage['jobs_done']
    for idx in range(start_idx, len(target_jobs)):
        signal = _get_control(workflow_id)
        if signal in ('hold', 'cancel', 'revoke'):
            _handle_stop(workflow_id, data, signal, data['current_stage_index'])
            return False

        job = target_jobs[idx]
        full_text, fail_reason, is_unavailable = fetch_full_description(job['link'])

        # find and update this job's entry in the full temp list (by portal+raw_id)
        for j in all_jobs:
            if j.get('portal') == job.get('portal') and j.get('raw_id') == job.get('raw_id'):
                if full_text:
                    j['description'] = full_text
                    j['description_full'] = 1
                break
        ws.temp_save(workflow_id, all_jobs)

        if is_unavailable and job.get('id'):
            update_status(job['id'], 'ineligible')

        stage['jobs_done'] = idx + 1
        ws.save_workflow(data)
        if full_text:
            outcome = 'enriched'
        elif is_unavailable:
            outcome = 'marked ineligible (job listing expired)'
        else:
            outcome = 'skipped (' + str(fail_reason) + ')'
        _wflog(workflow_id, stage['name'] + ' — ' + str(idx + 1) + '/' + str(len(target_jobs)) +
               ' ' + outcome + ' — ' + job.get('link', ''))

    return True


def _run_descriptor_transmission_stage(workflow_id, data):
    time.sleep(1.5)
    jobs = ws.temp_load(workflow_id)
    updated = 0
    for j in jobs:
        if j.get('description_full'):
            db_job = get_job(j['id']) if j.get('id') else None
            # jobs from temp only have portal/raw_id reliably; look up real id
            if not db_job:
                conn = jo_conn()
                jo_schema(conn)
                cur = conn.execute('SELECT id FROM jobs WHERE portal = ? AND raw_id = ?', (j['portal'], j['raw_id']))
                row = cur.fetchone()
                conn.close()
                if row:
                    j['id'] = row['id']
            if j.get('id'):
                update_description(j['id'], j['description'])
                updated += 1
    _wflog(workflow_id, 'Transmission complete — ' + str(updated) + ' description(s) written to main DB')


# ---------------------------------------------------------------------------
# Public controls
# ---------------------------------------------------------------------------
def start_workflow(workflow_id):
    t = threading.Thread(target=run_workflow, args=(workflow_id,), daemon=True)
    t.start()

def hold_workflow(workflow_id):
    _set_control(workflow_id, 'hold')

def cancel_workflow(workflow_id):
    _set_control(workflow_id, 'cancel')

def revoke_workflow(workflow_id):
    _set_control(workflow_id, 'revoke')

def retry_workflow(workflow_id):
    data = ws.load_workflow(workflow_id)
    if not data or data['status'] not in ('hold', 'failed'):
        return False
    data['status'] = 'in_progress'
    idx = data['current_stage_index']
    if idx < len(data['stages']):
        data['stages'][idx]['status'] = 'not_started'
    ws.save_workflow(data)
    _activity(workflow_id, 'Retry requested — resuming from stage "' +
               (data['stages'][idx]['name'] if idx < len(data['stages']) else '?') + '"')
    start_workflow(workflow_id)
    return True

def reset_workflow(workflow_id):
    data = ws.load_workflow(workflow_id)
    if not data:
        return False
    for s in data['stages']:
        s['status'] = 'not_started'
        if s.get('type') == 'fetch':
            s['cycles_done'] = 0
            s['cycles_total'] = None
            s.pop('cycle_sizes', None)
            s.pop('total_count', None)
    data['current_stage_index'] = 0
    data['status'] = 'hold'
    data['started_at'] = None
    ws.temp_cleanup(workflow_id)
    ws.save_workflow(data)
    _activity(workflow_id, 'Workflow reset — all progress cleared, moved to Hold (press Retry to restart)')
    return True
