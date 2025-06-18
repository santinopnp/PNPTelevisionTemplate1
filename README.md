# PNP Television Bot

This project powers a Telegram bot that provides access to PNP Television content.

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and fill in your own bot token, database credentials, payment links and channel IDs.
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python run_bot.py
   ```

The example environment file contains placeholders only. You must supply valid values obtained from your own Telegram bot, payment provider and database.

`setup.py` provides a simple script to generate a basic `.env` file interactively if preferred.
