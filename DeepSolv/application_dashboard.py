#!/usr/bin/env python3
"""
Comprehensive Application and Database Display Dashboard
Real-time monitoring of the Shopify Store Insights Fetcher application
"""
import requests
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

class ApplicationDashboard:
    def __init__(self):
        self.api_base_url = "http://localhost:8002"
        self.db_path = "shopify_insights.db"
        
    def check_server_status(self) -> Dict[str, Any]:
        """Check if the FastAPI server is running"""
        try:
            response = requests.get(f"{self.api_base_url}/info", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "✅ RUNNING",
                    "info": response.json(),
                    "url": self.api_base_url
                }
            else:
                return {
                    "status": "❌ NOT RUNNING",
                    "error": f"Status code: {response.status_code}",
                    "url": self.api_base_url
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "❌ NOT RUNNING",
                "error": str(e),
                "url": self.api_base_url
            }
        
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        if not os.path.exists(self.db_path):
            return {"status": "❌ DATABASE NOT FOUND", "path": self.db_path}
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all table statistics
            tables = [
                'brands', 'products', 'hero_products', 'policies', 
                'faqs', 'social_handles', 'important_links', 'contact_details'
            ]
            
            stats = {
                "status": "✅ CONNECTED",
                "path": self.db_path,
                "tables": {}
            }
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats["tables"][table] = count
                
            # Get recent activity
            cursor.execute("""
                SELECT brand_name, website_url, analysis_date, pages_analyzed 
                FROM brands 
                ORDER BY analysis_date DESC 
                LIMIT 5
            """)
            recent_brands = cursor.fetchall()
            stats["recent_activity"] = recent_brands
            
            conn.close()
            return stats
            
        except Exception as e:
            return {"status": "❌ DATABASE ERROR", "error": str(e)}
    
    def get_brand_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about analyzed brands"""
        if not os.path.exists(self.db_path):
            return []
            
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Get comprehensive brand information
            cursor.execute("""
                SELECT 
                    b.id,
                    b.brand_name,
                    b.website_url,
                    b.brand_description,
                    b.analysis_date,
                    b.pages_analyzed,
                    COUNT(DISTINCT p.id) as product_count,
                    COUNT(DISTINCT sh.id) as social_count,
                    COUNT(DISTINCT f.id) as faq_count,
                    COUNT(DISTINCT cd.id) as contact_count
                FROM brands b
                LEFT JOIN products p ON b.id = p.brand_id
                LEFT JOIN social_handles sh ON b.id = sh.brand_id  
                LEFT JOIN faqs f ON b.id = f.brand_id
                LEFT JOIN contact_details cd ON b.id = cd.brand_id
                GROUP BY b.id
                ORDER BY b.analysis_date DESC
            """)
            
            brands = []
            for row in cursor.fetchall():
                brands.append({
                    "id": row["id"],
                    "brand_name": row["brand_name"],
                    "website_url": row["website_url"],
                    "description": row["brand_description"][:100] + "..." if row["brand_description"] else "N/A",
                    "analysis_date": row["analysis_date"],
                    "pages_analyzed": row["pages_analyzed"],
                    "product_count": row["product_count"],
                    "social_count": row["social_count"], 
                    "faq_count": row["faq_count"],
                    "contact_count": row["contact_count"]
                })
                
            conn.close()
            return brands
            
        except Exception as e:
            return [{"error": f"Database error: {str(e)}"}]
    
    def test_api_endpoint(self, test_url: str = "beard.com") -> Dict[str, Any]:
        """Test the API with a sample analysis"""
        try:
            payload = {
                "website_url": test_url,
                "force_refresh": False  # Use cached data if available
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/v1/analyze",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                brand_data = data.get('brand_data', {})
                return {
                    "status": "✅ API WORKING",
                    "test_url": test_url,
                    "success": data.get('success', False),
                    "cached": data.get('cached', False),
                    "brand_name": brand_data.get('brand_name', 'N/A'),
                    "product_count": brand_data.get('product_count', 0),
                    "social_handles": len(brand_data.get('social_handles', [])),
                    "response_time": "< 1s" if data.get('cached') else "~30s"
                }
            else:
                return {
                    "status": "❌ API ERROR",
                    "test_url": test_url,
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
                
        except Exception as e:
            return {
                "status": "❌ API ERROR",
                "test_url": test_url,
                "error": str(e)
            }
    
    def display_comprehensive_dashboard(self):
        """Display the complete application and database dashboard"""
        
        print("🚀 SHOPIFY STORE INSIGHTS FETCHER - APPLICATION DASHBOARD")
        print("=" * 70)
        print(f"📅 Dashboard Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Server Status
        print("🖥️  SERVER STATUS")
        print("-" * 30)
        server_status = self.check_server_status()
        print(f"Status: {server_status['status']}")
        print(f"URL: {server_status['url']}")
        if "info" in server_status:
            info = server_status["info"]
            print(f"Title: {info.get('message', 'N/A')}")
            print(f"Version: {info.get('version', 'N/A')}")
            print(f"Documentation: {server_status['url']}{info.get('docs', '/docs')}")
        print()
        
        # 2. Database Status
        print("💾 DATABASE STATUS")
        print("-" * 30)
        db_stats = self.get_database_stats()
        print(f"Status: {db_stats['status']}")
        if "path" in db_stats:
            print(f"Database: {db_stats['path']}")
        
        if "tables" in db_stats:
            print("\n📊 Table Statistics:")
            for table, count in db_stats["tables"].items():
                print(f"   {table.title().replace('_', ' ')}: {count} records")
                
        if "recent_activity" in db_stats and db_stats["recent_activity"]:
            print("\n📈 Recent Analysis Activity:")
            for brand in db_stats["recent_activity"]:
                brand_name, url, date, pages = brand
                print(f"   • {brand_name} ({url}) - {pages} pages - {date}")
        print()
        
        # 3. API Test
        print("🧪 API FUNCTIONALITY TEST")
        print("-" * 30)
        api_test = self.test_api_endpoint()
        print(f"Status: {api_test['status']}")
        print(f"Test URL: {api_test['test_url']}")
        if "brand_name" in api_test:
            print(f"Brand Found: {api_test['brand_name']}")
            print(f"Products: {api_test['product_count']}")
            print(f"Social Handles: {api_test['social_handles']}")
            print(f"Cached Response: {api_test['cached']}")
            print(f"Response Time: {api_test['response_time']}")
        elif "error" in api_test:
            print(f"Error: {api_test['error']}")
        print()
        
        # 4. Brand Analysis Summary
        print("🏪 ANALYZED BRANDS SUMMARY")
        print("-" * 30)
        brands = self.get_brand_details()
        if brands and "error" not in brands[0]:
            for brand in brands:
                print(f"🔹 {brand['brand_name']}")
                print(f"   URL: {brand['website_url']}")
                print(f"   Products: {brand['product_count']} | Social: {brand['social_count']} | FAQs: {brand['faq_count']}")
                print(f"   Analysis: {brand['analysis_date']} ({brand['pages_analyzed']} pages)")
                print(f"   Description: {brand['description']}")
                print()
        else:
            print("No brands analyzed yet or database error")
            if brands and "error" in brands[0]:
                print(f"Error: {brands[0]['error']}")
        print()
        
        # 5. System Health Summary
        print("💚 SYSTEM HEALTH SUMMARY")
        print("-" * 30)
        server_ok = server_status['status'].startswith("✅")
        db_ok = db_stats['status'].startswith("✅") 
        api_ok = api_test['status'].startswith("✅")
        
        overall_status = "🟢 ALL SYSTEMS OPERATIONAL" if all([server_ok, db_ok, api_ok]) else "🟡 SOME ISSUES DETECTED"
        
        print(f"Overall Status: {overall_status}")
        print(f"FastAPI Server: {'✅' if server_ok else '❌'}")
        print(f"SQLite Database: {'✅' if db_ok else '❌'}")
        print(f"API Endpoints: {'✅' if api_ok else '❌'}")
        print()
        
        # 6. Quick Actions
        print("⚡ QUICK ACTIONS")
        print("-" * 30)
        print(f"🌐 Web Interface: {self.api_base_url}/")
        print(f"📚 API Documentation: {self.api_base_url}/docs")
        print(f"🔍 API Alternative Docs: {self.api_base_url}/redoc")
        print(f"📊 Health Check: {self.api_base_url}/api/v1/health")
        print()
        
        print("🎯 Sample API Calls:")
        print(f"""   curl -X POST "{self.api_base_url}/api/v1/analyze" \\
        -H "Content-Type: application/json" \\
        -d '{{"website_url": "beard.com"}}'""")
        print()
        
        print("✨ Application ready for comprehensive brand analysis!")
        print("=" * 70)

def main():
    """Main dashboard execution"""
    dashboard = ApplicationDashboard()
    dashboard.display_comprehensive_dashboard()

if __name__ == "__main__":
    main()
