# PNP Television Bot Template

This project contains a Telegram bot and admin panel used to manage subscriptions for PNP Television channels. Users can purchase plans via Bold and get access to private Telegram channels.  The repository also includes a simplified subscription bot and utilities to run the admin dashboard.

## Required Environment Variables

Create a `.env` file with the following keys:

- `BOT_TOKEN` – Telegram bot token.
- `ADMIN_IDS` – comma separated list of Telegram user IDs with admin access.
- `BOLD_IDENTITY_KEY` – identity key for generating payment URLs.
- `ADMIN_PORT` – port for the FastAPI admin panel (default `8080`).
- `ADMIN_HOST` – host address for the admin panel (default `0.0.0.0`).
- `GOOGLE_CREDENTIALS_JSON` – service account JSON used by `gspread`.
- `DATABASE_URL` – PostgreSQL connection string.
- `WEEK_PAYMENT_LINK`, `MONTH_PAYMENT_LINK`, `3MONTH_PAYMENT_LINK`, `HALFYEAR_PAYMENT_LINK`, `YEAR_PAYMENT_LINK`, `LIFETIME_PAYMENT_LINK` – Bold payment links used by `run_simple_bot.py`.
- `CHANNEL_ID` – ID of the main private channel for the simplified bot.
- `CHANNEL_NAME` – name displayed by the simplified bot.
- Optional: `CHANNEL_1`, `CHANNEL_2`, `CHANNEL_3` etc. for additional private channels.

## Running Locally

1. Install Python 3.11 and run `pip install -r requirements.txt`.
2. Create the `.env` file with your configuration.
3. Launch the main bot with:

   ```bash
   python run_bot.py
   ```

4. To start the admin panel:

   ```bash
   python run_admin.py
   ```

5. The simplified subscription bot can be launched with:

   ```bash
   python run_simple_bot.py
   ```

Logs are written to the `logs/` directory.

## Deployment with Railway

A `railway.json` file is included. Deploy the repository to Railway and set the same environment variables in the project settings.  Railway will start the bot using `python run_bot.py`.  You can add a PostgreSQL plugin to obtain the `DATABASE_URL` automatically.

