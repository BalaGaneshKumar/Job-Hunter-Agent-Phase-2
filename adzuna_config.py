"""
adzuna_config.py — loads Adzuna credentials from .env (never hardcoded
here, never logged). Add .env to .gitignore before committing this repo.
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

ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID', '')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY', '')

if not ADZUNA_APP_ID or not ADZUNA_APP_KEY or 'PASTE_YOUR' in ADZUNA_APP_ID:
    print('[adzuna_config] WARNING: credentials missing or still placeholders — check .env at', ENV_PATH)
else:
    print('[adzuna_config] Loaded credentials OK (app_id ends with ...' + ADZUNA_APP_ID[-4:] + ')')

