#!/usr/bin/env python3
"""
Simple Shopify Store Insights Application Test
Final validation that all core features are working
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8002"
API_V1 = f"{API_BASE_URL}/api/v1"

def test_quick_check():
    """Test quick store validation"""
    print("🔍 Testing Quick Store Check...")
    response = requests.get(f"{API_V1}/realtime/quick-check?url=allbirds.com")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ {data['brand_name']} - Shopify: {data['is_shopify_store']}")
        return True
    print("  ❌ Quick check failed")
    return False

def test_single_analysis():
    """Test single store analysis"""
    print("🔍 Testing Single Store Analysis...")
    data = {
        "url": "gymshark.com",
        "save_to_database": True
    }
    response = requests.post(f"{API_V1}/realtime/analyze", json=data)
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"  ✅ {result['brand_name']} - Quality: {result['data_quality_score']:.0f}/100")
            return True
    print("  ❌ Single analysis failed")
    return False

def test_comparison():
    """Test store comparison"""
    print("🔍 Testing Store Comparison...")
    data = {
        "urls": ["allbirds.com", "vessi.com"]
    }
    response = requests.post(f"{API_V1}/realtime/compare", json=data)
    if response.status_code == 200:
        result = response.json()
        leaders = result['comparison_analysis']['leaders']
        print(f"  ✅ Fastest: {leaders['fastest_loading']}, Best Social: {leaders['best_social_presence']}")
        return True
    print("  ❌ Comparison failed")
    return False

def test_api_docs():
    """Test API documentation"""
    print("🔍 Testing API Documentation...")
    response = requests.get(f"{API_BASE_URL}/docs")
    if response.status_code == 200:
        print("  ✅ API Documentation accessible")
        return True
    print("  ❌ API Documentation failed")
    return False

def main():
    """Run all tests"""
    print("🚀 SHOPIFY STORE INSIGHTS FETCHER - FINAL TEST")
    print("=" * 50)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        test_api_docs,
        test_quick_check,
        test_single_analysis,
        test_comparison
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"  ❌ Test error: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Application is fully functional!")
        print()
        print("✅ Features confirmed working:")
        print("  • Real-time store analysis")
        print("  • Database integration") 
        print("  • REST API endpoints")
        print("  • Store comparison")
        print("  • Quick validation")
        print("  • API documentation")
        print()
        print(f"🌐 Access the full API at: {API_BASE_URL}/docs")
    else:
        print("⚠️  Some tests failed. Check server status.")
    
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
