"""
Application validation script to check all components are working
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.dependencies import check_db_connection, get_db_session
from database.crud import BrandCRUD
from services.scraper import WebScraper
from services.parser import ShopifyParser
from services.competitor_finder import get_competitor_finder
from models.brand_data import BrandContext
from config import settings

def test_database():
    """Test database connection and operations"""
    print("🔍 Testing database connection...")
    
    try:
        if not check_db_connection():
            print("❌ Database connection failed")
            return False
        
        # Test basic CRUD operations
        with get_db_session() as db:
            brands = BrandCRUD.get_brands(db, skip=0, limit=10)
            print(f"✅ Database connected successfully. Found {len(brands)} brands.")
            return True
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

async def test_scraper():
    """Test web scraper"""
    print("🔍 Testing web scraper...")
    
    try:
        test_url = "https://httpbin.org/html"
        async with WebScraper() as scraper:
            content = await scraper.fetch_html(test_url)
            
        if content and len(content) > 100:
            print("✅ Web scraper working correctly")
            return True
        else:
            print("❌ Web scraper returned insufficient content")
            return False
            
    except Exception as e:
        print(f"❌ Web scraper error: {e}")
        return False

def test_parser():
    """Test content parser"""
    print("🔍 Testing content parser...")
    
    try:
        parser = ShopifyParser("https://example.com")
        
        # Test parsing empty data (should not crash)
        _ = parser.parse_products_json({})
        _ = parser.parse_hero_products_from_html("")
        _ = parser.parse_social_handles_from_html("")
        
        print("✅ Content parser working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Content parser error: {e}")
        return False

async def test_competitor_finder():
    """Test competitor finder service"""
    print("🔍 Testing competitor finder...")
    
    try:
        competitor_finder = get_competitor_finder()
        competitors = await competitor_finder.find_competitors("https://allbirds.com", limit=3)
        
        if isinstance(competitors, list) and len(competitors) > 0:
            print(f"✅ Competitor finder working correctly. Found {len(competitors)} competitors.")
            return True
        else:
            print("❌ Competitor finder returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Competitor finder error: {e}")
        return False

def test_models():
    """Test Pydantic models"""
    print("🔍 Testing data models...")
    
    try:
        # Test creating a basic BrandContext
        brand_context = BrandContext(
            website_url="https://test.com",
            brand_name="Test Brand"
        )
        
        # Test serialization
        json_data = brand_context.model_dump()
        
        if json_data and "website_url" in json_data:
            print("✅ Data models working correctly")
            return True
        else:
            print("❌ Data models serialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Data models error: {e}")
        return False

def test_config():
    """Test configuration settings"""
    print("🔍 Testing configuration...")
    
    try:
        # Check essential settings
        if not settings.DATABASE_URL:
            print("❌ DATABASE_URL not configured")
            return False
            
        if not settings.USER_AGENT:
            print("❌ USER_AGENT not configured")
            return False
            
        print("✅ Configuration loaded successfully")
        print(f"   Database: {settings.DATABASE_URL}")
        print(f"   Debug: {settings.DEBUG}")
        print(f"   Port: {settings.PORT}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def run_validation():
    """Run all validation tests"""
    print("🚀 Starting application validation...\n")
    
    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("Data Models", test_models),
        ("Web Scraper", test_scraper),
        ("Content Parser", test_parser),
        ("Competitor Finder", test_competitor_finder)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
            
        results.append((test_name, result))
        print()
    
    # Summary
    print(f"{'='*50}")
    print("🏁 VALIDATION SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Application is ready to use.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues above.")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_validation())
    sys.exit(0 if success else 1)
