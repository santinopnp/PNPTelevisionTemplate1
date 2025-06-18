#!/usr/bin/env python3
import sys
import traceback
import os

def run_with_debug(script_name):
    print(f"=== Starting {script_name} ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("Environment variables:")
    
    # Print relevant environment variables (hide sensitive data)
    env_vars = ['DATABASE_URL', 'BOT_TOKEN', 'ADMIN_IDS', 'BOLD_IDENTITY_KEY', 
                'PORT', 'ADMIN_PORT', 'CHANNEL_ID']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var in ['DATABASE_URL', 'BOT_TOKEN', 'BOLD_IDENTITY_KEY']:
                # Show only first few characters for sensitive data
                print(f"  {var}: {value[:10]}... (length: {len(value)})")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: NOT SET")
    
    print("\nImporting script...")
    
    try:
        if script_name == "bot":
            print("Attempting to import bot modules...")
            # Try importing the main bot file
            import run_bot
            print("Successfully imported run_bot")
        elif script_name == "admin":
            print("Attempting to import admin modules...")
            import run_admin
            print("Successfully imported run_admin")
    except Exception as e:
        print(f"\nERROR during import: {type(e).__name__}: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\n{script_name} finished without errors")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_with_debug(sys.argv[1])
    else:
        print("Usage: python debug_wrapper.py [bot|admin]")
        sys.exit(1)