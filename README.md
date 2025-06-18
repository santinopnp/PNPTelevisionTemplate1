=======
# PNP Television Bot Template

This repository contains a Telegram bot for managing paid subscriptions to several channels.  It includes a standard bot with an admin panel as well as a simplified subscription bot.

## Requirements

* Python 3.11
* The packages listed in [`requirements.txt`](requirements.txt)

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file (or set these variables in your hosting environment) with at least the following values:

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram bot token. **Required.** |
| `ADMIN_IDS` | Comma separated list of Telegram user IDs allowed to use admin commands. |
| `BOLD_IDENTITY_KEY` | Bold.co payment identity key. |
| `ADMIN_PORT` | Port for the admin FastAPI application (default `8080`). |
| `ADMIN_HOST` | Host address for the admin application (default `0.0.0.0`). |
| `GOOGLE_CREDENTIALS_JSON` | Path or JSON credentials for Google Sheets. |
| `DATABASE_URL` | PostgreSQL connection string. |
| `CHANNEL_ID` | ID of the Telegram channel for the simplified bot. |
| `CHANNEL_NAME` | Display name for the simplified bot channel. |
| `WEEK_PAYMENT_LINK` | Payment link for the week plan. |
| `MONTH_PAYMENT_LINK` | Payment link for the month plan. |
| `3MONTH_PAYMENT_LINK` | Payment link for the 3‑month plan. |
| `HALFYEAR_PAYMENT_LINK` | Payment link for the half‑year plan. |
| `YEAR_PAYMENT_LINK` | Payment link for the yearly plan. |
| `LIFETIME_PAYMENT_LINK` | Payment link for the lifetime plan. |

Other channel IDs can be defined in `bot/config.py` if multiple channels are used.

## Common commands

* `python setup.py` – helper to generate a minimal `.env` file.
* `python run_bot.py` – start the main subscription bot.
* `python run_admin.py` – launch the FastAPI admin panel.
* `python run_simple_bot.py` – start the simplified subscription bot.

## Deploying on Railway

A [`railway.json`](railway.json) configuration is provided.  To deploy:

1. Create a new project on [Railway](https://railway.app/) and link this repository.
2. Set all required environment variables in the Railway dashboard.
3. The project will build using Python 3.11 and run `python run_bot.py` as specified in `railway.json`.
4. Deploy the service.  Railway will restart the bot on failure as configured.

Railway automatically installs the dependencies listed in
[`requirements.txt`](requirements.txt) when building the project. If the bot
fails with `No module named 'asyncpg'` it usually means the dependencies were
not installed. Re‑deploy or run `pip install -r requirements.txt` locally to
verify the environment.

If the bot exits with `ConnectionRefusedError` during startup, the PostgreSQL
server may not be reachable. Verify that `DATABASE_URL` points to a running
database that accepts connections.

