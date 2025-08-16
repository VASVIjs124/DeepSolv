#!/usr/bin/env python3
"""
Debug the product_catalog to products conversion
"""
import requests
import sqlite3

def debug_product_conversion():
    """Debug why products field is empty"""
    
    print("🔍 Debugging product_catalog to products conversion...")
    
    # Clear cache first
    conn = sqlite3.connect('shopify_insights.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE brand_id IN (SELECT id FROM brands WHERE website_url LIKE "%allbirds%")')
    cursor.execute('DELETE FROM social_handles WHERE brand_id IN (SELECT id FROM brands WHERE website_url LIKE "%allbirds%")')
    cursor.execute('DELETE FROM brands WHERE website_url LIKE "%allbirds%"')
    conn.commit()
    conn.close()
    
    url = "http://localhost:8002/api/v1/analyze"
    payload = {
        "website_url": "allbirds.com",
        "force_refresh": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            brand_data = data.get('brand_data', {})
            
            product_catalog = brand_data.get('product_catalog', [])
            products_legacy = brand_data.get('products', [])
            
            print(f"📦 Product Catalog: {len(product_catalog)} items")
            print(f"📦 Products Legacy: {len(products_legacy)} items")
            
            if product_catalog and len(product_catalog) > 0:
                print(f"\n🔍 Sample Product Catalog Item:")
                sample_pc = product_catalog[0]
                for key, value in sample_pc.items():
                    print(f"   {key}: {value}")
                    
            if products_legacy and len(products_legacy) > 0:
                print(f"\n🔍 Sample Products Legacy Item:")
                sample_p = products_legacy[0]
                for key, value in sample_p.items():
                    print(f"   {key}: {value}")
            else:
                print(f"\n❌ Products legacy is empty!")
                print(f"   This means the list comprehension is not working")
                
                if product_catalog:
                    print(f"\n🔧 Let's check the structure of product_catalog items:")
                    sample = product_catalog[0]
                    print(f"   Type: {type(sample)}")
                    print(f"   Keys: {list(sample.keys()) if isinstance(sample, dict) else 'Not a dict'}")
                    
            # Test the specific field mappings
            print(f"\n🧪 Testing field mappings from product_catalog:")
            if product_catalog:
                sample = product_catalog[0]
                print(f"   title: {sample.get('title', 'MISSING')}")
                print(f"   price: {sample.get('price', 'MISSING')}")  
                print(f"   vendor: {sample.get('vendor', 'MISSING')}")
                print(f"   product_type: {sample.get('product_type', 'MISSING')}")
                print(f"   url: {sample.get('url', 'MISSING')}")
                print(f"   available: {sample.get('available', 'MISSING')}")
                print(f"   images: {sample.get('images', 'MISSING')}")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_product_conversion()
