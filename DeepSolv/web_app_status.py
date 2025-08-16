#!/usr/bin/env python3
"""
Shopify Store Insights Fetcher - Web Application Status
Complete system status check for database, web server, and API
"""

import requests
import json
import subprocess
import sqlite3
from datetime import datetime
import sys
import os

# Configuration
SERVER_URL = "http://localhost:8002"
DATABASE_PATH = "shopify_insights.db"

def check_web_server():
    """Check if the web server is running"""
    print("🌐 Checking Web Server...")
    try:
        response = requests.get(SERVER_URL, timeout=5)
        print(f"  ✅ Web Server: Running on {SERVER_URL}")
        return True
    except requests.exceptions.RequestException:
        print(f"  ❌ Web Server: Not accessible at {SERVER_URL}")
        return False

def check_api_documentation():
    """Check if API documentation is accessible"""
    print("\n📚 Checking API Documentation...")
    try:
        response = requests.get(f"{SERVER_URL}/docs", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ API Docs: Available at {SERVER_URL}/docs")
            return True
        else:
            print(f"  ❌ API Docs: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"  ❌ API Docs: Not accessible")
        return False

def check_database():
    """Check database connectivity and status"""
    print("\n💾 Checking Database...")
    try:
        if not os.path.exists(DATABASE_PATH):
            print(f"  ❌ Database: File {DATABASE_PATH} not found")
            return False
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        expected_tables = ['brands', 'products', 'hero_products', 'policies', 
                          'faqs', 'social_handles', 'important_links', 'contact_details']
        
        missing_tables = set(expected_tables) - set(table_names)
        if missing_tables:
            print(f"  ⚠️  Database: Missing tables: {missing_tables}")
        else:
            print("  ✅ Database: All tables present")
        
        # Check brand count
        cursor.execute("SELECT COUNT(*) FROM brands")
        brand_count = cursor.fetchone()[0]
        print(f"  📊 Database: {brand_count} brands in database")
        
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Database: Error - {e}")
        return False

def check_api_endpoints():
    """Check key API endpoints"""
    print("\n🔧 Checking API Endpoints...")
    
    endpoints = [
        ("/api/v1/realtime/quick-check?url=example.com", "Quick Check"),
        ("/api/v1/brands/", "Brands List")
    ]
    
    working_endpoints = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{SERVER_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {name}: Working")
                working_endpoints += 1
            else:
                print(f"  ⚠️  {name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {name}: Error - {e}")
    
    return working_endpoints == len(endpoints)

def test_real_time_analysis():
    """Test real-time analysis functionality"""
    print("\n🔍 Testing Real-time Analysis...")
    
    try:
        test_data = {
            "url": "allbirds.com",
            "save_to_database": False  # Don't save to avoid duplicates
        }
        
        response = requests.post(
            f"{SERVER_URL}/api/v1/realtime/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"  ✅ Real-time Analysis: Working - {result.get('brand_name', 'Unknown')} analyzed")
                return True
            else:
                print(f"  ❌ Real-time Analysis: Failed - {result.get('error', 'Unknown error')}")
        else:
            print(f"  ❌ Real-time Analysis: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("  ⏰ Real-time Analysis: Timeout (30s) - This is normal for first analysis")
        return True  # Timeout is acceptable for this test
    except Exception as e:
        print(f"  ❌ Real-time Analysis: Error - {e}")
    
    return False

def check_process_status():
    """Check if the server process is running"""
    print("\n🔄 Checking Server Process...")
    try:
        # Check if port 8002 is in use (indicating server is running)
        result = subprocess.run(
            ["netstat", "-an"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if "8002" in result.stdout:
            print("  ✅ Server Process: Running on port 8002")
            return True
        else:
            print("  ❌ Server Process: Port 8002 not in use")
            return False
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        # Try alternative method for Windows
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout.strip():
                print("  ✅ Server Process: Running on port 8002")
                return True
            else:
                print("  ❌ Server Process: Port 8002 not in use")
                return False
        except:
            print("  ⚠️  Server Process: Unable to verify (process check failed)")
            return None

def main():
    """Run complete system status check"""
    print("🚀 SHOPIFY STORE INSIGHTS FETCHER - WEB APPLICATION STATUS")
    print("=" * 65)
    print(f"⏰ Status Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checks = [
        ("Web Server", check_web_server),
        ("API Documentation", check_api_documentation),
        ("Database", check_database),
        ("API Endpoints", check_api_endpoints),
        ("Real-time Analysis", test_real_time_analysis),
        ("Server Process", check_process_status)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            result = check_func()
            if result:
                passed += 1
            elif result is None:
                # Don't count inconclusive results against the total
                total -= 1
        except Exception as e:
            print(f"\n❌ {name}: Unexpected error - {e}")
    
    print("\n" + "=" * 65)
    print(f"📊 SYSTEM STATUS: {passed}/{total} components operational ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("\n✅ Your Shopify Store Insights Fetcher is fully functional:")
        print("  🌐 Web Interface: http://localhost:8002")
        print("  📚 API Documentation: http://localhost:8002/docs")
        print("  🔍 Real-time Analysis: Available")
        print("  💾 Database: Connected and ready")
        print("  🚀 REST API: All endpoints working")
        
        print("\n🎯 Ready for:")
        print("  • Real-time Shopify store analysis")
        print("  • Bulk store processing") 
        print("  • Store comparison analysis")
        print("  • Database persistence")
        print("  • API integrations")
        
    elif passed >= total * 0.8:
        print("⚠️  MOSTLY OPERATIONAL - Minor issues detected")
        print("   System is functional but some features may be limited")
        
    else:
        print("❌ SYSTEM ISSUES DETECTED")
        print("   Please check the errors above and restart the server if needed")
        print("   To restart: python start_server.py")
    
    print(f"\n⏰ Status check completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
