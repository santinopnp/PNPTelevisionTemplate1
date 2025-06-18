import os

def setup():
    print("PNP Television Bot Ultimate - Setup")
    print("=" * 40)

    if not os.path.exists('.env'):
        print("Creating .env file...")

        BOT_TOKEN = input("Enter your Telegram bot token: ").strip()
        ADMIN_ID = input("Enter your Telegram user ID: ").strip()

        env_content = f"""BOT_TOKEN={BOT_TOKEN}
ADMIN_IDS=7940478393
ADMIN_PORT=8080
ADMIN_HOST=0.0.0.0
GOOGLE_CREDENTIALS_JSON=credentials.json
"""  # triple comillas escapadas

        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)

        print("✅ Setup completo. ¡Listo para lanzar el bot!")

if __name__ == "__main__":
    setup()
