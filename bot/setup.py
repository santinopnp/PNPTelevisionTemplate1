#!/usr/bin/env python3
import os
import json

def create_initial_files():
    """Create initial configuration files"""
    print("🎬 PNP Television Bot Ultimate - Setup")
    print("=" * 50)
    
    # Create .env if it doesn't exist
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file...")
        
        bot_token = input("🤖 Enter your Telegram bot token: ").strip()
        admin_id = input("👤 Enter your Telegram user ID: ").strip()
        
        env_content = f"""# Bot Configuration
BOT_TOKEN={bot_token}
ADMIN_IDS={admin_id}

# Admin Panel
ADMIN_PORT=8080
ADMIN_HOST=0.0.0.0

# Database
GOOGLE_CREDENTIALS_JSON=credentials.json

# Channels (update with your channel IDs)
CHANNEL_ID=-1002068120499

"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created!")
    
    # Create initial users.json
    if not os.path.exists('users.json'):
        initial_data = {
            "users": {},
            "stats": {
                "total_users": 0,
                "active_subscriptions": 0,
                "total_revenue": 0
            },
            "last_updated": ""
        }
        
        with open('users.json', 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        print("✅ Initial database created!")
    
    print("\n🎯 Setup completed!")
    print("Next steps:")
    print("1. Run: python run_bot.py")
    print("2. Run: python run_admin.py (in another terminal)")
    print("3. Access admin panel: http://localhost:8080")

if __name__ == "__main__":
    create_initial_files()
