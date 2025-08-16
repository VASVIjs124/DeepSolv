#!/usr/bin/env python3
"""
Production deployment configuration for Shopify Store Insights Fetcher
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from main import app

# Set production environment variables
os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8000")

# For ASGI servers like Gunicorn
application = app

if __name__ == "__main__":
    import uvicorn
    
    # Production settings
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        workers=1,  # Single worker for SQLite
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True
    )
