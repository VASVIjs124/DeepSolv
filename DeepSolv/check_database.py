#!/usr/bin/env python3
"""
Check database contents
"""
import sqlite3

def check_database():
    conn = sqlite3.connect('shopify_insights.db')
    cursor = conn.cursor()
    
    print("🔍 CHECKING DATABASE CONTENTS:")
    print("=" * 50)
    
    # Check brands
    cursor.execute('SELECT brand_name, website_url, pages_analyzed FROM brands ORDER BY id DESC LIMIT 5')
    results = cursor.fetchall()
    print(f"\n📊 Recent Brands ({len(results)}):")
    for row in results:
        print(f"  • {row[0]} ({row[1]}) - {row[2]} pages")
    
    # Check allbirds specifically
    cursor.execute('SELECT id, brand_name, pages_analyzed FROM brands WHERE website_url LIKE "%allbirds%"')
    allbirds = cursor.fetchall()
    if allbirds:
        print(f"\n🎯 ALLBIRDS DATA:")
        for row in allbirds:
            brand_id, name, pages = row
            print(f"  Brand ID: {brand_id}, Name: {name}, Pages: {pages}")
            
            # Check products for this brand
            cursor.execute('SELECT COUNT(*) FROM products WHERE brand_id = ?', (brand_id,))
            product_count = cursor.fetchone()[0]
            print(f"  Products in database: {product_count}")
    else:
        print("\n❌ No Allbirds data found in database")
    
    # Check beard.com
    cursor.execute('SELECT id, brand_name, pages_analyzed FROM brands WHERE website_url LIKE "%beard%"')
    beard = cursor.fetchall()
    if beard:
        print(f"\n🧔 BEARD.COM DATA:")
        for row in beard:
            brand_id, name, pages = row
            print(f"  Brand ID: {brand_id}, Name: {name}, Pages: {pages}")
            
            # Check products for this brand
            cursor.execute('SELECT COUNT(*) FROM products WHERE brand_id = ?', (brand_id,))
            product_count = cursor.fetchone()[0]
            print(f"  Products in database: {product_count}")
    else:
        print("\n❌ No Beard.com data found in database")
    
    conn.close()

if __name__ == "__main__":
    check_database()
