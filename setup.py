import os

# Helper script to create a minimal `.env` file with the required
# environment variables for the bot.

def setup():
    """Interactive helper to create a basic `.env` file."""

    print("PNP Television Bot Ultimate - Setup")
    print("=" * 40)

    if not os.path.exists('.env'):
        print("Creating .env file...")

        BOT_TOKEN = input("Enter your Telegram bot token: ").strip()
        ADMIN_ID = input("Enter your Telegram user ID: ").strip()

        env_content = (
            f"BOT_TOKEN={BOT_TOKEN}\n"
            f"ADMIN_IDS={ADMIN_ID}\n"
        )

        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)

        print("✅ Setup completo. ¡Listo para lanzar el bot!")

if __name__ == "__main__":
    setup()
