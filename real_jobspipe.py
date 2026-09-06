"""
real_jobspipe.py — live JobsPipe API client.

Confirmed live via direct testing (10/10 real jobs returned full,
untruncated descriptions, 2,100–7,000 chars each — no snippet limit
like Adzuna/Jooble). This is what makes JobsPipe worth having: full
description, no separate Descriptor step needed, same treatment as
JSearch.

Auth: Authorization: Bearer jp_live_... (header-based, like JSearch —
not a URL param like Adzuna, not a URL path segment like Jooble).
Pagination: cursor-based (metadata.next_cursor), like JSearch.
Billing: 1 credit = 1 job RETURNED, not 1 credit per API call — so the
`limit` param directly controls cost. Free tier is 1,000 jobs/month
(confirmed via their own docs, which is more generous than JSearch's
200/month and resets monthly, unlike Jooble's 500-lifetime cap).

Transient 5xx errors are retried with backoff, same pattern as the
other real_*.py clients. 4xx errors are not retried.
"""

import re
import time
import requests
from jobspipe_config import JOBSPIPE_API_KEY

URL = 'https://api.jobspipe.dev/v1/jobs/search'

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5  # doubles each retry: 5s, 10s, 20s
REQUEST_TIMEOUT = 20


def _redact(message):
    if JOBSPIPE_API_KEY:
        message = message.replace(JOBSPIPE_API_KEY, '***')
    return message


def real_search(keyword, location, limit=10, cursor=None):
    headers = {
        'Authorization': 'Bearer ' + JOBSPIPE_API_KEY,
        'Content-Type': 'application/json',
    }
    body = {
        'job_title_or': [keyword],
        'job_location_or': [location],
        'limit': limit,
    }
    if cursor:
        body['cursor'] = cursor

    last_error = None
    delay = RETRY_DELAY_SECONDS
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(URL, json=body, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            last_error = e
            if status is not None and 500 <= status < 600 and attempt < MAX_RETRIES:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError('JobsPipe API request failed (' + type(e).__name__ + '): ' + _redact(str(e)))
        except requests.exceptions.RequestException as e:
            raise RuntimeError('JobsPipe API request failed (' + type(e).__name__ + '): ' + _redact(str(e)))

    raise RuntimeError('JobsPipe API request failed after ' + str(MAX_RETRIES) +
                        ' attempts (' + type(last_error).__name__ + '): ' + _redact(str(last_error)))
