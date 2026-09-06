import os
import sqlite3

from dashboard_log import log_event

def log_info(message):
    """Kept for compatibility with any old call sites — routes through the
    shared log buffer under the 'CareerTracker' source tag."""
    log_event('CareerTracker', message)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CAREER_DB  = os.path.join(BASE_DIR, 'career_tracker.db')

APP_COLUMNS  = ['company', 'link', 'credential', 'credtype', 'passhint', 'role', 'location', 'date', 'stage', 'substage', 'ghostedsub', 'jobid', 'notes']
SITE_COLUMNS = ['name', 'url', 'cred', 'notes']

# ---------------------------------------------------------------------------
# Connection / schema
# ---------------------------------------------------------------------------
def _get_conn():
    conn = sqlite3.connect(CAREER_DB)
    conn.row_factory = sqlite3.Row
    return conn

def _ensure_schema(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS career_apps (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            company     TEXT,
            link        TEXT,
            credential  TEXT,
            credtype    TEXT,
            passhint    TEXT,
            role        TEXT,
            location    TEXT,
            date        TEXT,
            stage       TEXT,
            substage    TEXT,
            ghostedsub  TEXT,
            jobid       TEXT,
            notes       TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS career_sites (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name   TEXT,
            url    TEXT,
            cred   TEXT,
            notes  TEXT
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_apps_stage ON career_apps(stage)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_apps_company ON career_apps(company)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_sites_name ON career_sites(name)')
    conn.commit()

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
def load_career_apps():
    try:
        conn = _get_conn()
        _ensure_schema(conn)
        cols = ','.join(APP_COLUMNS)
        cur = conn.execute(f'SELECT {cols} FROM career_apps ORDER BY id')
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        log_info('Apps read error: ' + str(e)[:50])
        return []

def load_career_sites():
    try:
        conn = _get_conn()
        _ensure_schema(conn)
        cols = ','.join(SITE_COLUMNS)
        cur = conn.execute(f'SELECT {cols} FROM career_sites ORDER BY id')
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        log_info('Sites read error: ' + str(e)[:50])
        return []

# ---------------------------------------------------------------------------
# Save
# Frontend sends the whole in-memory array on every add/edit/delete (no row
# ids involved anywhere in dashboard_career.py), so a full replace here
# reproduces exactly the same overwrite-the-file behavior the CSV version had.
# ---------------------------------------------------------------------------
def save_career_apps(rows):
    try:
        conn = _get_conn()
        _ensure_schema(conn)
        with conn:
            conn.execute('DELETE FROM career_apps')
            placeholders = ','.join(['?'] * len(APP_COLUMNS))
            insert_sql = f"INSERT INTO career_apps ({','.join(APP_COLUMNS)}) VALUES ({placeholders})"
            conn.executemany(insert_sql, [[row.get(c, '') for c in APP_COLUMNS] for row in rows])
        conn.close()
        return True
    except Exception as e:
        log_info('Apps write error: ' + str(e)[:50])
        return False

def save_career_sites(rows):
    try:
        conn = _get_conn()
        _ensure_schema(conn)
        with conn:
            conn.execute('DELETE FROM career_sites')
            placeholders = ','.join(['?'] * len(SITE_COLUMNS))
            insert_sql = f"INSERT INTO career_sites ({','.join(SITE_COLUMNS)}) VALUES ({placeholders})"
            conn.executemany(insert_sql, [[row.get(c, '') for c in SITE_COLUMNS] for row in rows])
        conn.close()
        return True
    except Exception as e:
        log_info('Sites write error: ' + str(e)[:50])
        return False
