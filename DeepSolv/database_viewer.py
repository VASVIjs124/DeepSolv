#!/usr/bin/env python3
"""
Database Content Viewer for Shopify Store Insights
"""
import sqlite3
import json

def view_database_contents():
    """Display detailed database contents"""
    
    conn = sqlite3.connect('shopify_insights.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print('🗄️  DETAILED DATABASE CONTENTS')
    print('=' * 60)
    
    # Brands table
    print('\n📊 BRANDS TABLE')
    print('-' * 30)
    cursor.execute('SELECT * FROM brands')
    brands = cursor.fetchall()
    for row in brands:
        print(f'ID: {row["id"]}')
        print(f'Brand Name: {row["brand_name"]}')
        print(f'Website: {row["website_url"]}')
        print(f'Description: {row["brand_description"][:200] if row["brand_description"] else "N/A"}...')
        print(f'Analysis Date: {row["analysis_date"]}')
        print(f'Pages Analyzed: {row["pages_analyzed"]}')
        print()
    
    if brands:
        brand_id = brands[0]["id"]
        
        # Social Handles
        print('\n📱 SOCIAL HANDLES')
        print('-' * 30)
        cursor.execute('SELECT platform, username, url FROM social_handles WHERE brand_id = ?', (brand_id,))
        socials = cursor.fetchall()
        for row in socials:
            print(f'{row["platform"].upper()}: @{row["username"]}')
            print(f'   URL: {row["url"]}')
        if not socials:
            print("No social handles found")
        
        # FAQs Sample
        print('\n❓ FAQ SAMPLE (First 5)')
        print('-' * 30)
        cursor.execute('SELECT question, answer FROM faqs WHERE brand_id = ? LIMIT 5', (brand_id,))
        faqs = cursor.fetchall()
        for i, row in enumerate(faqs, 1):
            print(f'{i}. Q: {row["question"]}')
            print(f'   A: {row["answer"][:150] if row["answer"] else "N/A"}...')
            print()
        if not faqs:
            print("No FAQs found")
        
        # Hero Products Sample (checking all brand_ids if none for current brand)
        print('\n🏆 HERO PRODUCTS SAMPLE (First 8)')
        print('-' * 30)
        cursor.execute('SELECT title, description, price FROM hero_products WHERE brand_id = ? LIMIT 8', (brand_id,))
        products = cursor.fetchall()
        
        if not products:
            print(f"No hero products found for brand_id {brand_id}. Checking other brands...")
            cursor.execute('SELECT title, description, price, brand_id FROM hero_products LIMIT 8')
            products_other = cursor.fetchall()
            for i, row in enumerate(products_other, 1):
                print(f'{i}. {row[0]} (Brand ID: {row[3]})')
                print(f'   Price: {row[2] if row[2] else "N/A"}')
                print(f'   Description: {row[1][:100] if row[1] else "N/A"}...')
                print()
        else:
            for i, row in enumerate(products, 1):
                print(f'{i}. {row["title"]}')
                print(f'   Price: {row["price"] if row["price"] else "N/A"}')
                print(f'   Description: {row["description"][:100] if row["description"] else "N/A"}...')
                print()
        
        # Policies Sample (checking all brand_ids if none for current brand)
        print('\n📋 POLICIES SAMPLE (First 5)')
        print('-' * 30)
        cursor.execute('SELECT policy_type, content FROM policies WHERE brand_id = ? LIMIT 5', (brand_id,))
        policies = cursor.fetchall()
        
        if not policies:
            print(f"No policies found for brand_id {brand_id}. Checking other brands...")
            cursor.execute('SELECT policy_type, content, brand_id FROM policies LIMIT 5')
            policies_other = cursor.fetchall()
            for i, row in enumerate(policies_other, 1):
                print(f'{i}. Type: {row[0]} (Brand ID: {row[2]})')
                print(f'   Content: {row[1][:150] if row[1] else "N/A"}...')
                print()
        else:
            for i, row in enumerate(policies, 1):
                print(f'{i}. Type: {row["policy_type"]}')
                print(f'   Content: {row["content"][:200] if row["content"] else "N/A"}...')
                print()
        
        # Important Links Sample
        print('\n🔗 IMPORTANT LINKS SAMPLE (First 5)')
        print('-' * 30)
        cursor.execute('SELECT title, url, link_type FROM important_links WHERE brand_id = ? LIMIT 5', (brand_id,))
        links = cursor.fetchall()
        for i, row in enumerate(links, 1):
            print(f'{i}. {row["title"]}')
            print(f'   URL: {row["url"]}')
            print(f'   Type: {row["link_type"] if row["link_type"] else "N/A"}')
            print()
        if not links:
            print("No important links found")
        
        # Contact Details
        print('\n📞 CONTACT DETAILS SAMPLE (First 5)')
        print('-' * 30)
        cursor.execute('SELECT contact_type, value FROM contact_details WHERE brand_id = ? LIMIT 5', (brand_id,))
        contacts = cursor.fetchall()
        for i, row in enumerate(contacts, 1):
            print(f'{i}. {row["contact_type"]}: {row["value"]}')
        if not contacts:
            print("No contact details found")
    
    # Summary statistics
    print('\n📈 SUMMARY STATISTICS')
    print('-' * 30)
    tables = ['brands', 'products', 'hero_products', 'policies', 'faqs', 'social_handles', 'important_links', 'contact_details']
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'{table.replace("_", " ").title()}: {count} records')
    
    conn.close()
    print('\n✅ Database contents displayed successfully!')

if __name__ == "__main__":
    view_database_contents()
