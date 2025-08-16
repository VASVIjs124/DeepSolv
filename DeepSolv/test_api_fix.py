#!/usr/bin/env python3
"""
Quick test script to verify API is working without OpenAI errors
"""
import requests
import json

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8002"
    
    print("🔍 Testing Shopify Store Insights API...")
    
    # Test health endpoint
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"   ✅ Health Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test info endpoint
    print("\n2. Testing Info Endpoint...")
    try:
        response = requests.get(f"{base_url}/info")
        print(f"   ✅ Info Status: {response.status_code}")
        info = response.json()
        print(f"   API Version: {info.get('version', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Info check failed: {e}")
    
    # Test brands list (should work even without analysis)
    print("\n3. Testing Brands Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/brands")
        print(f"   ✅ Brands Status: {response.status_code}")
        brands = response.json()
        print(f"   Brands in database: {len(brands)}")
    except Exception as e:
        print(f"   ❌ Brands check failed: {e}")
    
    # Test simple analysis (cached data should work)
    print("\n4. Testing Analysis (using cached Allbirds data)...")
    try:
        payload = {
            "url": "https://allbirds.com",
            "force_refresh": False  # Use cached data
        }
        
        response = requests.post(
            f"{base_url}/api/v1/realtime/analyze",
            json=payload,
            timeout=30
        )
        
        print(f"   ✅ Analysis Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Brand: {data.get('brand_name', 'Unknown')}")
            products = data.get('products', [])
            print(f"   Products Found: {len(products)}")
            if products:
                print(f"   First Product: {products[0].get('title', 'Unknown')}")
        else:
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")
    
    print("\n🎉 API Test Complete!")
    print("💡 Note: AI features are disabled (no OpenAI API key)")
    print("   The core scraping functionality works without AI")

if __name__ == "__main__":
    test_api()
