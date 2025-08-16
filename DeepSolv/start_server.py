"""
Shopify Store Insights Fetcher - Startup Script
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Shopify Store Insights Fetcher...")
    print("📡 API Server: http://localhost:8002")
    print("📚 Documentation: http://localhost:8002/docs")
    print("🔍 Real-time Analysis: http://localhost:8002/api/v1/realtime/")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
