"""
dashboard_log.py — two separate logging channels.

1. log_event(source, message)  — SERVER-SIDE system logs (startup, DB
   read/write errors, backup events, request errors). Printed to the
   console only. Never stored, never shown in the browser's activity
   panels.

2. add_tab_log(tab, source, message) / get_tab_logs(tab) — CLIENT-SIDE
   activity logs for a specific tab ('career' or 'profile'). Stored
   in-memory, one bucket per tab, and served to that tab's own Logs
   panel only. Deliberately NOT printed to the console — these are
   silent there, since the console is reserved for server-side events.

Sub-tabs within a main tab share the same bucket (e.g. Applications and
Job Sites both write into 'career'; all 9 Profile sub-tabs write into
'profile') — only the two main tabs are separated from each other.
"""

import time
import threading

_lock = threading.Lock()
_TAB_LOGS = {}          # {'career': [...], 'profile': [...]}
_MAX_LOGS_PER_TAB = 300  # ring buffer cap per tab


def log_event(source, message):
    """Server-side system log — console only."""
    print('[' + source + '] ' + str(message), flush=True)


def add_tab_log(tab, source, message):
    """Client-side action log for one tab. In-memory only, silent on console."""
    entry = {
        'ts': time.strftime('%Y-%m-%d %H:%M:%S'),
        'source': source,
        'message': str(message),
    }
    with _lock:
        buf = _TAB_LOGS.setdefault(tab, [])
        buf.append(entry)
        if len(buf) > _MAX_LOGS_PER_TAB:
            del buf[: len(buf) - _MAX_LOGS_PER_TAB]


def get_tab_logs(tab, limit=200):
    with _lock:
        return list(_TAB_LOGS.get(tab, [])[-limit:])
