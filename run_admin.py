# -*- coding: utf-8 -*-
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    try:
        from bot.admin_panel import app
    except (ModuleNotFoundError, ImportError) as e:
        if getattr(e, 'name', '') == 'asyncpg':
            print("❌ Error: asyncpg is not installed. Run 'pip install -r requirements.txt'")
        else:
            print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    port = int(os.getenv("ADMIN_PORT", 8080))
    host = os.getenv("ADMIN_HOST", "0.0.0.0")
    
    print(f"Starting admin panel on http://{host}:{port}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info"
    )
