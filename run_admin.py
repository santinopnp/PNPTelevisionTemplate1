import os
import sys
from fastapi import FastAPI
import uvicorn

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your admin module - adjust this based on your actual structure
try:
    from bot.admin import app  # If your FastAPI app is in bot/admin.py
except ImportError:
    try:
        from admin import app  # If your FastAPI app is in admin.py
    except ImportError:
        # Create a minimal FastAPI app if imports fail
        app = FastAPI(title="Telegram Bot Admin Panel")
        
        @app.get("/")
        async def root():
            return {"message": "Admin panel is running", "status": "ok"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}



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
    
    print(f"Starting admin panel on {host}:{port}")
    
    # Run with uvicorn
    uvicorn.run(
        app,  # Use the app object directly, not a string
        host=host,
        port=port,
        reload=False  # Don't use reload in production
    )
