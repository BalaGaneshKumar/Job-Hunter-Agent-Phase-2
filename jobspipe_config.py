"""
jobspipe_config.py — loads the JobsPipe API key from .env (never
hardcoded here, never logged). Add .env to .gitignore before committing.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')


def _load_env(path):
    if not os.path.exists(path):
        return
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()


_load_env(ENV_PATH)

JOBSPIPE_API_KEY = os.environ.get('JOBSPIPE_API_KEY', '')

if not JOBSPIPE_API_KEY:
    print('[jobspipe_config] WARNING: JOBSPIPE_API_KEY missing — check .env at', ENV_PATH)
else:
    print('[jobspipe_config] Loaded credentials OK (key ends with ...' + JOBSPIPE_API_KEY[-4:] + ')')
