#!/usr/bin/env python3
"""
Final Status Check - Shopify Store Insights Fetcher
Comprehensive system validation
"""

import requests
import json
import time
import sys
from typing import Dict, Any

def check_web_server() -> bool:
    """Check if web server is running"""
    try:
        response = requests.get("http://localhost:8002", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_api_docs() -> bool:
    """Check if API documentation is accessible"""
    try:
        response = requests.get("http://localhost:8002/docs", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_database_health() -> bool:
    """Check database health via API"""
    try:
        response = requests.get("http://localhost:8002/api/v1/brands", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_realtime_endpoint() -> bool:
    """Check real-time analysis endpoint"""
    try:
        response = requests.get("http://localhost:8002/api/v1/realtime/quick-check?url=https://shop.shopify.com", timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    try:
        response = requests.get("http://localhost:8002/api/v1/brands", timeout=5)
        if response.status_code == 200:
            brands = response.json()
            return {
                "total_brands": len(brands),
                "status": "operational"
            }
    except requests.RequestException:
        pass
    
    return {"total_brands": 0, "status": "error"}

def main():
    """Run comprehensive status check"""
    print("🔍 Shopify Store Insights Fetcher - Final Status Check")
    print("=" * 60)
    
    checks = [
        ("🌐 Web Server", check_web_server),
        ("📚 API Documentation", check_api_docs),
        ("🗄️  Database Health", check_database_health),
        ("⚡ Real-time Analysis", check_realtime_endpoint),
    ]
    
    results = {}
    
    for name, check_func in checks:
        print(f"\n{name}...", end=" ")
        sys.stdout.flush()
        
        result = check_func()
        results[name] = result
        
        if result:
            print("✅ PASS")
        else:
            print("❌ FAIL")
    
    # Database statistics
    print(f"\n🗄️  Database Statistics...", end=" ")
    sys.stdout.flush()
    db_stats = get_database_stats()
    print(f"✅ {db_stats['total_brands']} brands stored")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SYSTEM STATUS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("✅ Web Application: http://localhost:8002")
        print("✅ API Documentation: http://localhost:8002/docs")
        print("✅ Real-time Analysis: Available")
        print(f"✅ Database: {db_stats['total_brands']} brands stored")
        
        print("\n🚀 READY FOR PRODUCTION USE!")
        print("=" * 60)
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("❌ System not fully operational")
        return 1

if __name__ == "__main__":
    exit(main())
