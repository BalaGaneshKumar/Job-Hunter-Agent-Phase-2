# Setup Guide — Clone & API Keys

## 1. Clone the repo

```
git clone https://github.com/<your-username>/Job-Hunter-Agent-Phase-2.git
cd Job-Hunter-Agent-Phase-2
```

## 2. Install Python & dependencies

Requires Python 3.9+ (see README's Setup section for install steps).

```
pip install requests
```

## 3. Create your `.env` file

Copy the example file and fill in the keys you get in steps 4–6 below:

```
cp env.example .env
```

`.env` should end up looking like:
```
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
JSEARCH_API_KEY=your_rapidapi_key
JOBSPIPE_API_KEY=jp_live_your_key
```

Never commit `.env` — it's already in `.gitignore`.

## 4. Adzuna API key

1. Go to [developer.adzuna.com](https://developer.adzuna.com/) and register
   for a free account.
2. Once logged in, go to your **Dashboard** — it shows your `app_id` and
   `app_key` immediately (no separate "create app" step).
3. Copy both into `.env` as `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`.

## 5. JSearch (RapidAPI) key

1. Go to [rapidapi.com](https://rapidapi.com/) and create a free account.
2. Search for **"JSearch"** in the RapidAPI marketplace and open its page.
3. Subscribe to the **free tier** (200 requests/month).
4. On the API's "Endpoints" tab, your key appears under **X-RapidAPI-Key**
   in the code snippets panel — copy it.
5. Paste it into `.env` as `JSEARCH_API_KEY`.

## 6. JobsPipe API key

1. Go to [jobspipe.dev](https://jobspipe.dev/) and sign up for a free account.
2. From your account/dashboard, generate an API key (starts with `jp_live_`).
3. Paste it into `.env` as `JOBSPIPE_API_KEY`.

## 7. Verify credentials loaded

Run the server:
```
python dashboard_server.py
```
Each config file prints a confirmation line to the console on startup, e.g.:
```
[adzuna_config] Loaded credentials OK (app_id ends with ...1234)
[jsearch_config] Loaded credentials OK (key ends with ...abcd)
[jobspipe_config] Loaded credentials OK (key ends with ...wxyz)
```
If you see a `WARNING: ... missing or still placeholders` line instead,
double-check the matching line in `.env`.

## 8. Open the dashboard

```
http://localhost:8080
```
