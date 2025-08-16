"""
Simple Top 100 Shopify Stores Database Analysis Script
"""
import sys
import os

# Add the parent directory to sys.path to import database modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from database.dependencies import get_db_session
from database.crud import BrandCRUD

def simple_analysis():
    """Simple database analysis"""
    
    print("=" * 80)
    print("🛍️  TOP 100 SHOPIFY STORES - DATABASE ANALYSIS")
    print("=" * 80)
    print()
    
    with get_db_session() as session:
        # Get all brands
        brands = BrandCRUD.get_brands(session, skip=0, limit=200)
        
        if not brands:
            print("❌ No brands found in database!")
            return
        
        print(f"📊 DATABASE OVERVIEW")
        print(f"   • Total Brands in Database: {len(brands)}")
        print()
        
        # Show first 10 brands
        print(f"🏆 TOP BRANDS IN DATABASE")
        print("    ID  | Brand Name                    | Website URL")
        print("    ----|-------------------------------|----------------------------------")
        
        for i, brand in enumerate(brands[:10]):
            brand_name_str = str(brand.brand_name)[:28]
            website_str = str(brand.website_url).replace("https://", "")[:35]
            print(f"    {i+1:3d} | {brand_name_str:29} | {website_str}")
        
        print()
        
        # Sample brand details
        if brands:
            sample_brand = brands[0]
            print(f"🔍 SAMPLE BRAND SHOWCASE")
            print(f"   Brand: {sample_brand.brand_name}")
            print(f"   Website: {sample_brand.website_url}")
            print(f"   Description: {sample_brand.brand_description}")
            print(f"   Pages Analyzed: {sample_brand.pages_analyzed}")
            print(f"   Analysis Date: {sample_brand.analysis_date}")
        
        print()
        print("=" * 80)
        print("✅ ANALYSIS COMPLETE - Database successfully populated!")
        print("🚀 Ready for data science analysis!")
        print("=" * 80)

if __name__ == "__main__":
    simple_analysis()
