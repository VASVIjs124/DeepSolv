"""
Real-time Shopify Store Analysis Demo & Testing Script
Demonstrates comprehensive real-time analysis capabilities
"""
import asyncio
import aiohttp
import json
import time
from typing import List, Dict, Any

class RealtimeAnalysisDemo:
    """Demo script for real-time Shopify store analysis"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        
    async def demo_single_store_analysis(self, store_url: str):
        """Demo single store comprehensive analysis"""
        
        print(f"🔍 REAL-TIME ANALYSIS DEMO: {store_url}")
        print("=" * 80)
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Quick check
            print("1️⃣ Quick Store Validation...")
            quick_check_url = f"{self.base_url}/api/v1/realtime/quick-check"
            async with session.get(quick_check_url, params={'url': store_url}) as response:
                if response.status == 200:
                    quick_data = await response.json()
                    print(f"   ✅ Store: {quick_data.get('brand_name', 'Unknown')}")
                    print(f"   ✅ Shopify Store: {quick_data.get('is_shopify_store', False)}")
                    print(f"   ✅ Accessible: {quick_data.get('accessible', False)}")
                    print(f"   ✅ Has Products API: {quick_data.get('has_products_json', False)}")
                else:
                    print(f"   ❌ Quick check failed: {response.status}")
                    return
            
            print()
            
            # Step 2: Full analysis
            print("2️⃣ Comprehensive Analysis (this may take 15-30 seconds)...")
            analysis_url = f"{self.base_url}/api/v1/realtime/analyze"
            
            analysis_payload = {
                "url": store_url,
                "save_to_database": True,
                "include_recommendations": True
            }
            
            start_time = time.time()
            
            async with session.post(analysis_url, json=analysis_payload) as response:
                if response.status == 200:
                    analysis_data = await response.json()
                    analysis_time = time.time() - start_time
                    
                    print(f"   ✅ Analysis completed in {analysis_time:.2f} seconds")
                    print(f"   📊 Data Quality Score: {analysis_data.get('data_quality_score', 0):.1f}/100")
                    print(f"   💾 Saved to Database: {analysis_data.get('saved_to_database', False)}")
                    
                    # Display key insights
                    insights = analysis_data.get('insights', {})
                    self._display_analysis_insights(insights)
                    
                    # Display recommendations
                    recommendations = analysis_data.get('recommendations', [])
                    self._display_recommendations(recommendations)
                    
                    # Display competitive metrics
                    competitive_metrics = analysis_data.get('competitive_metrics', {})
                    self._display_competitive_metrics(competitive_metrics)
                    
                else:
                    print(f"   ❌ Analysis failed: {response.status}")
                    error_data = await response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        print("✅ Single Store Analysis Demo Complete!")
        
    async def demo_store_comparison(self, store_urls: List[str]):
        """Demo store comparison functionality"""
        
        print(f"⚖️  STORE COMPARISON DEMO")
        print(f"Comparing {len(store_urls)} stores...")
        print("=" * 80)
        
        async with aiohttp.ClientSession() as session:
            comparison_url = f"{self.base_url}/api/v1/realtime/compare"
            
            comparison_payload = {
                "urls": store_urls,
                "include_detailed_metrics": True
            }
            
            print("🔄 Analyzing and comparing stores (this may take 30-60 seconds)...")
            start_time = time.time()
            
            async with session.post(comparison_url, json=comparison_payload) as response:
                if response.status == 200:
                    comparison_data = await response.json()
                    analysis_time = time.time() - start_time
                    
                    print(f"✅ Comparison completed in {analysis_time:.2f} seconds")
                    print(f"📊 Stores analyzed: {comparison_data.get('stores_compared', 0)}")
                    
                    # Display comparison insights
                    comparison_analysis = comparison_data.get('comparison_analysis', {})
                    self._display_comparison_insights(comparison_analysis)
                    
                else:
                    print(f"❌ Comparison failed: {response.status}")
                    error_data = await response.json()
                    print(f"Error: {error_data.get('detail', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        print("✅ Store Comparison Demo Complete!")
    
    async def demo_bulk_analysis(self, store_urls: List[str]):
        """Demo bulk analysis functionality"""
        
        print(f"🔄 BULK ANALYSIS DEMO")
        print(f"Analyzing {len(store_urls)} stores in bulk...")
        print("=" * 80)
        
        async with aiohttp.ClientSession() as session:
            bulk_url = f"{self.base_url}/api/v1/realtime/analyze/bulk"
            
            bulk_payload = {
                "urls": store_urls,
                "save_to_database": True,
                "max_concurrent": 3
            }
            
            print("🚀 Starting bulk analysis (this may take several minutes)...")
            start_time = time.time()
            
            async with session.post(bulk_url, json=bulk_payload) as response:
                if response.status == 200:
                    bulk_data = await response.json()
                    analysis_time = time.time() - start_time
                    
                    print(f"✅ Bulk analysis completed in {analysis_time:.2f} seconds")
                    
                    # Display bulk summary
                    summary = bulk_data.get('bulk_analysis_summary', {})
                    self._display_bulk_summary(summary, bulk_data)
                    
                else:
                    print(f"❌ Bulk analysis failed: {response.status}")
                    error_data = await response.json()
                    print(f"Error: {error_data.get('detail', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        print("✅ Bulk Analysis Demo Complete!")
    
    async def check_analyzer_status(self):
        """Check the status of the real-time analyzer"""
        
        print("🔧 ANALYZER STATUS CHECK")
        print("=" * 80)
        
        async with aiohttp.ClientSession() as session:
            status_url = f"{self.base_url}/api/v1/realtime/status"
            
            async with session.get(status_url) as response:
                if response.status == 200:
                    status_data = await response.json()
                    
                    print(f"Status: {status_data.get('status', 'unknown').upper()}")
                    print(f"Analyzer Ready: {status_data.get('analyzer_ready', False)}")
                    print(f"Last Check: {status_data.get('last_check', 'unknown')}")
                    
                    capabilities = status_data.get('capabilities', {})
                    print(f"\n🛠️  CAPABILITIES:")
                    for capability, available in capabilities.items():
                        status_icon = "✅" if available else "❌"
                        print(f"   {status_icon} {capability.replace('_', ' ').title()}")
                    
                    limits = status_data.get('limits', {})
                    print(f"\n📏 LIMITS:")
                    for limit, value in limits.items():
                        print(f"   • {limit.replace('_', ' ').title()}: {value}")
                    
                else:
                    print(f"❌ Status check failed: {response.status}")
        
        print("\n" + "=" * 80)
        print("✅ Status Check Complete!")
    
    def _display_analysis_insights(self, insights: Dict[str, Any]):
        """Display analysis insights in formatted way"""
        
        print("\n📊 ANALYSIS INSIGHTS:")
        print("-" * 40)
        
        # Store overview
        store_overview = insights.get('store_overview', {})
        print(f"🏪 Store Overview:")
        print(f"   • Brand: {store_overview.get('brand_name', 'Unknown')}")
        print(f"   • Shopify Store: {store_overview.get('is_shopify_store', False)}")
        print(f"   • Products: {store_overview.get('total_products', 0)}")
        print(f"   • Collections: {store_overview.get('total_collections', 0)}")
        print(f"   • Apps Detected: {len(store_overview.get('apps_detected', []))}")
        print(f"   • Shopify Plus: {store_overview.get('is_shopify_plus', False)}")
        
        # SEO analysis
        seo_analysis = insights.get('seo_analysis', {})
        print(f"\n🔍 SEO Analysis:")
        print(f"   • Title Optimized: {seo_analysis.get('title_optimization', False)}")
        print(f"   • Meta Description Optimized: {seo_analysis.get('meta_description_optimization', False)}")
        print(f"   • Images with Alt Tags: {seo_analysis.get('images_with_alt_tags', 0):.1f}%")
        print(f"   • Has Schema Markup: {seo_analysis.get('has_schema_markup', False)}")
        print(f"   • Page Load Time: {seo_analysis.get('page_load_time', 0):.2f}s")
        
        # Performance analysis
        performance = insights.get('performance_analysis', {})
        print(f"\n⚡ Performance Analysis:")
        print(f"   • Load Time: {performance.get('load_time', 0):.2f}s")
        print(f"   • Page Size: {performance.get('page_size_kb', 0):.1f} KB")
        print(f"   • Compression Enabled: {performance.get('compression_enabled', False)}")
        
        resources = performance.get('resources_count', {})
        print(f"   • Stylesheets: {resources.get('stylesheets', 0)}")
        print(f"   • Scripts: {resources.get('scripts', 0)}")
        print(f"   • Images: {resources.get('images', 0)}")
        
        # Social media presence
        social_media = insights.get('social_media_presence', {})
        print(f"\n📱 Social Media Presence:")
        print(f"   • Platforms Found: {social_media.get('platforms_found', 0)}")
        platforms = social_media.get('platforms', [])
        if platforms:
            print(f"   • Platforms: {', '.join(platforms)}")
        
        # E-commerce features
        ecommerce = insights.get('ecommerce_features', {})
        print(f"\n🛒 E-commerce Features:")
        payment_methods = ecommerce.get('payment_methods', [])
        if payment_methods:
            print(f"   • Payment Methods: {', '.join(payment_methods[:5])}")
        
        shipping_features = ecommerce.get('shipping_features', {})
        if shipping_features:
            print(f"   • Free Shipping: {shipping_features.get('free_shipping', False)}")
            print(f"   • International Shipping: {shipping_features.get('international_shipping', False)}")
    
    def _display_recommendations(self, recommendations: List[Dict[str, str]]):
        """Display actionable recommendations"""
        
        print(f"\n💡 RECOMMENDATIONS ({len(recommendations)} total):")
        print("-" * 40)
        
        if not recommendations:
            print("   No specific recommendations at this time.")
            return
        
        # Group by priority
        high_priority = [r for r in recommendations if r.get('priority') == 'High']
        medium_priority = [r for r in recommendations if r.get('priority') == 'Medium']
        
        if high_priority:
            print("🔴 HIGH PRIORITY:")
            for i, rec in enumerate(high_priority, 1):
                print(f"   {i}. {rec.get('category', 'General')}: {rec.get('recommendation', '')}")
        
        if medium_priority:
            print("\n🟡 MEDIUM PRIORITY:")
            for i, rec in enumerate(medium_priority, 1):
                print(f"   {i}. {rec.get('category', 'General')}: {rec.get('recommendation', '')}")
    
    def _display_competitive_metrics(self, metrics: Dict[str, Any]):
        """Display competitive analysis metrics"""
        
        print(f"\n🏆 COMPETITIVE METRICS:")
        print("-" * 40)
        
        # Product portfolio
        product_portfolio = metrics.get('product_portfolio', {})
        print(f"📦 Product Portfolio:")
        print(f"   • Total Products: {product_portfolio.get('total_products', 0)}")
        print(f"   • Categories: {product_portfolio.get('categories', 0)}")
        print(f"   • Average Price: ${product_portfolio.get('avg_price', 0):.2f}")
        print(f"   • Price Range: ${product_portfolio.get('price_range_span', 0):.2f}")
        
        # Market positioning
        positioning = metrics.get('market_positioning', {})
        print(f"\n🎯 Market Positioning:")
        print(f"   • Price Tier: {positioning.get('price_tier', 'Unknown')}")
        print(f"   • Primary Category: {positioning.get('primary_category', 'Unknown')}")
        print(f"   • Social Media Presence: {positioning.get('social_media_presence', 0)} platforms")
        
        # Technical performance
        technical = metrics.get('technical_performance', {})
        print(f"\n⚙️  Technical Performance:")
        print(f"   • Load Time: {technical.get('load_time', 0):.2f}s")
        print(f"   • Apps Count: {technical.get('apps_count', 0)}")
        print(f"   • Mobile Optimized: {technical.get('mobile_optimized', False)}")
    
    def _display_comparison_insights(self, analysis: Dict[str, Any]):
        """Display store comparison insights"""
        
        print(f"\n📊 COMPARISON INSIGHTS:")
        print("-" * 40)
        
        leaders = analysis.get('leaders', {})
        if leaders:
            print("🏆 CATEGORY LEADERS:")
            for category, leader in leaders.items():
                print(f"   • {category.replace('_', ' ').title()}: {leader}")
        
        insights = analysis.get('insights', {})
        if insights:
            print(f"\n🎯 KEY INSIGHTS:")
            for insight_key, insight_value in insights.items():
                print(f"   • {insight_key.replace('_', ' ').title()}: {insight_value}")
    
    def _display_bulk_summary(self, summary: Dict[str, Any], bulk_data: Dict[str, Any]):
        """Display bulk analysis summary"""
        
        print(f"\n📈 BULK ANALYSIS SUMMARY:")
        print("-" * 40)
        
        print(f"Total Stores: {bulk_data.get('total_stores', 0)}")
        print(f"Successful Analyses: {bulk_data.get('successful_analyses', 0)}")
        print(f"Success Rate: {bulk_data.get('success_rate', 0):.1f}%")
        
        aggregate_metrics = summary.get('aggregate_metrics', {})
        if aggregate_metrics:
            print(f"\n🔢 AGGREGATE METRICS:")
            print(f"   • Total Products: {aggregate_metrics.get('total_products_across_stores', 0)}")
            print(f"   • Average Load Time: {aggregate_metrics.get('average_load_time', 0):.2f}s")
            print(f"   • Unique Categories: {aggregate_metrics.get('unique_categories', 0)}")
            print(f"   • Unique Apps: {aggregate_metrics.get('unique_apps_detected', 0)}")
        
        quality_metrics = summary.get('quality_metrics', {})
        if quality_metrics:
            print(f"\n📊 QUALITY METRICS:")
            print(f"   • Average Quality Score: {quality_metrics.get('avg_data_quality_score', 0):.1f}/100")
            print(f"   • High Quality Stores (>80): {quality_metrics.get('stores_above_80_quality', 0)}")
            print(f"   • Stores Needing Improvement (<60): {quality_metrics.get('stores_needing_improvement', 0)}")

async def main():
    """Main demo function"""
    
    demo = RealtimeAnalysisDemo()
    
    print("🛍️  SHOPIFY STORE REAL-TIME ANALYSIS DEMO")
    print("=" * 80)
    print("This demo showcases comprehensive real-time analysis capabilities")
    print("=" * 80)
    print()
    
    # Check analyzer status first
    await demo.check_analyzer_status()
    print()
    
    # Demo stores for testing
    demo_stores = [
        "allbirds.com",
        "warbyparker.com", 
        "colourpop.com"
    ]
    
    print("🎯 DEMO OVERVIEW:")
    print("1. Single Store Analysis - Comprehensive analysis of one store")
    print("2. Store Comparison - Compare multiple stores side by side") 
    print("3. Bulk Analysis - Analyze multiple stores with summary")
    print()
    
    # Demo 1: Single store analysis
    print("🔸 Starting Demo 1: Single Store Analysis")
    await demo.demo_single_store_analysis(demo_stores[0])
    print()
    
    # Demo 2: Store comparison
    print("🔸 Starting Demo 2: Store Comparison")
    await demo.demo_store_comparison(demo_stores[:2])
    print()
    
    # Demo 3: Bulk analysis
    print("🔸 Starting Demo 3: Bulk Analysis")
    await demo.demo_bulk_analysis(demo_stores)
    print()
    
    print("🎉 ALL DEMOS COMPLETED!")
    print("=" * 80)
    print("✅ The Shopify Store Insights Fetcher is now ready for production use!")
    print("🔗 API Documentation: http://localhost:8002/docs")
    print("📊 Database: Populated with real-time analysis data")
    print("🚀 Ready for advanced analytics and insights!")

if __name__ == "__main__":
    print("🚀 Starting Real-time Analysis Demo...")
    print("⚠️  Make sure the FastAPI server is running on localhost:8002")
    print()
    
    # Run the demo
    asyncio.run(main())
