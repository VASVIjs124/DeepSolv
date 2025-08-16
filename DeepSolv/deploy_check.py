#!/usr/bin/env python3
"""
Pre-deployment checklist for Shopify Store Insights Fetcher
"""

import os
import sys
import sqlite3
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    
    required_files = [
        'main.py',
        'config.py', 
        'requirements.txt',
        '.env'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def check_database():
    """Check database connectivity"""
    print("🔍 Checking database...")
    
    try:
        # Check if database file exists
        db_file = "shopify_insights.db"
        if not Path(db_file).exists():
            print("⚠️  Database file not found, will be created on first run")
            return True
            
        # Test database connectivity
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        if tables:
            print(f"✅ Database connected, found {len(tables)} tables")
        else:
            print("⚠️  Database connected but no tables found")
            
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_python_dependencies():
    """Check Python dependencies"""
    print("🔍 Checking Python dependencies...")
    
    try:
        # Check critical imports
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        import aiohttp
        import requests
        
        print("✅ Core dependencies available")
        
        # Check versions
        print(f"   FastAPI: {fastapi.__version__}")
        print(f"   Uvicorn: {uvicorn.__version__}")
        print(f"   SQLAlchemy: {sqlalchemy.__version__}")
        print(f"   Pydantic: {pydantic.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def check_port_availability():
    """Check if default port is available"""
    print("🔍 Checking port availability...")
    
    import socket
    
    def is_port_available(host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0
        except:
            return False
    
    default_port = 8002
    if is_port_available('localhost', default_port):
        print(f"✅ Port {default_port} is available")
        return True
    else:
        print(f"⚠️  Port {default_port} is in use, consider changing PORT in .env")
        return True  # Not critical

def main():
    """Run all checks"""
    print("🚀 Shopify Store Insights Fetcher - Deployment Check")
    print("=" * 50)
    
    checks = [
        check_environment,
        check_python_dependencies, 
        check_database,
        check_port_availability
    ]
    
    results = []
    for check in checks:
        result = check()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print("📋 DEPLOYMENT CHECK SUMMARY")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All checks passed! Application ready for deployment.")
        print("\nTo start the application:")
        print("   python start.py")
        print("   # OR")
        print("   python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload")
        print("\nAPI will be available at:")
        print("   http://localhost:8002")
        print("   http://localhost:8002/docs (API Documentation)")
        
    else:
        failed = total - passed
        print(f"⚠️  {failed} check(s) failed. Please resolve issues above.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
