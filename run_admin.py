import os
from fastapi import FastAPI
import uvicorn

# Your existing imports and code here...

if __name__ == "__main__":
    # Railway provides PORT, but fallback to ADMIN_PORT or 8080
    port = int(os.getenv("PORT", os.getenv("ADMIN_PORT", "8080")))
    host = os.getenv("ADMIN_HOST", "0.0.0.0")
    
    print(f"Starting admin panel on {host}:{port}")
    
    # Assuming you're using FastAPI with uvicorn
    uvicorn.run(
        "your_admin_app:app",  # Replace with your actual app module
        host=host,
        port=port,
        reload=False  # Don't use reload in production
    )
