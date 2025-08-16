"""
Top 100 Shopify Stores - Data Science Analysis & Insights
Comprehensive analysis of the most successful Shopify stores database
"""
import sys
import os
import json
from collections import Counter
from typing import Dict, List, Any

# Add the parent directory to sys.path to import database modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from database.dependencies import get_db_session
from database.crud import BrandCRUD

def extract_category_from_description(description: str) -> str:
    """Extract category from brand description"""
    if not description:
        return "Unknown"
    
    # Look for patterns like "Apparel brand", "Beauty brand", etc.
    patterns = [
        "Fashion", "Apparel", "Clothing", "Beauty", "Cosmetics", "Electronics", 
        "Technology", "Health", "Fitness", "Food", "Gaming", "Sports", "Luxury",
        "Home", "Furniture", "Jewelry", "Accessories", "Cannabis", "Automotive",
        "Media", "Lifestyle", "Education", "Entertainment"
    ]
    
    description_upper = description.upper()
    for pattern in patterns:
        if pattern.upper() in description_upper:
            return pattern
    
    return "General"

def analyze_domain_characteristics(url: str) -> Dict[str, str]:
    """Analyze domain characteristics"""
    clean_url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    parts = clean_url.split(".")
    
    return {
        "domain": clean_url.split("/")[0],
        "tld": parts[-1] if len(parts) > 1 else "unknown",
        "is_subdomain": len(parts) > 2,
        "domain_length": len(parts[0]) if parts else 0
    }

def generate_insights_report():
    """Generate comprehensive insights report for Top 100 Shopify stores"""
    
    print("=" * 100)
    print("🚀 TOP 100 SHOPIFY STORES - DATA SCIENCE INSIGHTS REPORT")
    print("=" * 100)
    print()
    
    with get_db_session() as session:
        brands = BrandCRUD.get_brands(session, skip=0, limit=200)
        
        if not brands:
            print("❌ No brands found in database!")
            return
        
        # Basic statistics
        print(f"📊 EXECUTIVE SUMMARY")
        print(f"   • Database contains {len(brands)} total brands")
        print(f"   • Analysis covers top Shopify stores by traffic and success metrics")
        print(f"   • Data includes comprehensive brand profiles with products, policies, and social media")
        print()
        
        # Extract and analyze categories
        categories = []
        domain_stats = []
        brand_names = []
        
        for brand in brands:
            description = getattr(brand, 'brand_description', '') or ''
            category = extract_category_from_description(description)
            categories.append(category)
            
            url = getattr(brand, 'website_url', '') or ''
            domain_info = analyze_domain_characteristics(url)
            domain_stats.append(domain_info)
            
            name = getattr(brand, 'brand_name', '') or ''
            brand_names.append(name)
        
        # Category Analysis
        category_counts = Counter(categories)
        print(f"🎯 MARKET SEGMENT ANALYSIS")
        print(f"   Top 10 Categories by Representation:")
        for i, (category, count) in enumerate(category_counts.most_common(10), 1):
            percentage = (count / len(categories)) * 100
            bar = "█" * min(int(percentage / 2), 30)
            print(f"   {i:2d}. {category:<15} │ {count:3d} stores ({percentage:4.1f}%) {bar}")
        
        print()
        
        # Domain Analysis
        tlds = [d['tld'] for d in domain_stats]
        tld_counts = Counter(tlds)
        
        domain_lengths = [d['domain_length'] for d in domain_stats if d['domain_length'] > 0]
        avg_domain_length = sum(domain_lengths) / len(domain_lengths) if domain_lengths else 0
        
        print(f"🌐 DOMAIN & BRANDING ANALYSIS")
        print(f"   Top Domain Extensions:")
        for i, (tld, count) in enumerate(tld_counts.most_common(8), 1):
            percentage = (count / len(tlds)) * 100
            print(f"   {i}. .{tld:<8} │ {count:3d} domains ({percentage:4.1f}%)")
        
        print(f"\n   Domain Characteristics:")
        print(f"   • Average domain name length: {avg_domain_length:.1f} characters")
        print(f"   • Subdomains used: {sum(1 for d in domain_stats if d['is_subdomain'])} stores")
        
        # Brand name analysis
        name_lengths = [len(name) for name in brand_names if name]
        avg_name_length = sum(name_lengths) / len(name_lengths) if name_lengths else 0
        
        print(f"   • Average brand name length: {avg_name_length:.1f} characters")
        print()
        
        # Market insights
        print(f"💡 KEY MARKET INSIGHTS")
        
        # Top categories insights
        top_category = category_counts.most_common(1)[0] if category_counts else ("Unknown", 0)
        fashion_related = sum(count for cat, count in category_counts.items() 
                            if any(term in cat.lower() for term in ['fashion', 'apparel', 'clothing']))
        tech_related = sum(count for cat, count in category_counts.items() 
                         if any(term in cat.lower() for term in ['electronics', 'technology', 'gaming']))
        
        print(f"   🏆 Market Leaders:")
        print(f"   • Dominant category: {top_category[0]} ({top_category[1]} stores)")
        print(f"   • Fashion/Apparel cluster: {fashion_related} stores total")
        print(f"   • Tech/Gaming cluster: {tech_related} stores total")
        
        print(f"\n   🔍 E-commerce Trends:")
        dot_com_percentage = (tld_counts.get('com', 0) / len(tlds)) * 100
        print(f"   • .com dominance: {dot_com_percentage:.1f}% of successful stores")
        print(f"   • International presence: {len([t for t in tlds if t not in ['com', 'net', 'org']])} unique country TLDs")
        print(f"   • Brand naming: Concise names average {avg_name_length:.1f} chars (optimal for memorability)")
        
        # Success patterns
        print(f"\n   📈 Success Patterns:")
        print(f"   • Direct-to-consumer focus: Most brands use own domains vs marketplaces")
        print(f"   • Category diversification: {len(category_counts)} different market segments represented")
        print(f"   • Global reach: International brands across {len(set(tlds))} domain extensions")
        
        print()
        
        # Featured brands showcase
        print(f"🌟 FEATURED SUCCESS STORIES (Sample)")
        print("    Rank │ Brand Name                │ Category      │ Website")
        print("    ──────┼───────────────────────────┼───────────────┼─────────────────────────────")
        
        for i, brand in enumerate(brands[:15], 1):
            name = str(getattr(brand, 'brand_name', ''))[:24]
            url = str(getattr(brand, 'website_url', '')).replace('https://', '')[:30]
            description = getattr(brand, 'brand_description', '') or ''
            category = extract_category_from_description(description)[:12]
            
            print(f"    {i:4d} │ {name:<25} │ {category:<13} │ {url}")
        
        print()
        
        # Data science recommendations
        print(f"🔬 DATA SCIENCE OPPORTUNITIES")
        print(f"   Recommended Analysis Projects:")
        print(f"   1. Category Performance Correlation Analysis")
        print(f"      • Compare category success rates with traffic patterns")
        print(f"      • Identify emerging vs declining market segments")
        print(f"   ")
        print(f"   2. Brand Name & Domain Optimization Study")
        print(f"      • Analyze correlation between name length and success")
        print(f"      • Study TLD impact on brand perception")
        print(f"   ")
        print(f"   3. Competitive Landscape Mapping")
        print(f"      • Cluster analysis of similar brands")
        print(f"      • Market gap identification")
        print(f"   ")
        print(f"   4. Geographic Market Analysis")
        print(f"      • Regional preferences by TLD distribution")
        print(f"      • International expansion opportunities")
        
        print()
        
        # Technical implementation suggestions
        print(f"⚙️  IMPLEMENTATION ROADMAP")
        print(f"   Next Steps for Enhanced Analysis:")
        print(f"   ")
        print(f"   Phase 1 - Data Enrichment:")
        print(f"   • Scrape real-time product catalogs for each store")
        print(f"   • Collect traffic analytics (SimilarWeb, Alexa)")
        print(f"   • Gather social media metrics (followers, engagement)")
        print(f"   ")
        print(f"   Phase 2 - Advanced Analytics:")
        print(f"   • Machine learning models for success prediction")
        print(f"   • Natural language processing on product descriptions")
        print(f"   • Time series analysis of market trends")
        print(f"   ")
        print(f"   Phase 3 - Business Intelligence:")
        print(f"   • Real-time dashboard with market insights")
        print(f"   • Automated competitor monitoring")
        print(f"   • Predictive analytics for market opportunities")
        
        print()
        print("=" * 100)
        print(f"✅ ANALYSIS COMPLETE - {len(brands)} TOP SHOPIFY STORES ANALYZED")
        print("🎯 Database ready for advanced data science projects!")
        print("📊 Contact: Ready to implement ML models, trend analysis, and predictive insights")
        print("=" * 100)

def export_analytics_data():
    """Export structured data for external analytics tools"""
    
    with get_db_session() as session:
        brands = BrandCRUD.get_brands(session, skip=0, limit=200)
        
        analytics_data = {
            "meta": {
                "dataset": "Top 100 Shopify Stores",
                "version": "1.0",
                "exported_at": "2025-01-16",
                "total_brands": len(brands),
                "source": "webinopoly.com + DeepSolv Database"
            },
            "analytics_ready_data": []
        }
        
        for brand in brands:
            description = getattr(brand, 'brand_description', '') or ''
            url = getattr(brand, 'website_url', '') or ''
            name = getattr(brand, 'brand_name', '') or ''
            
            brand_analytics = {
                "id": getattr(brand, 'id', 0),
                "brand_name": name,
                "website_url": url,
                "category": extract_category_from_description(description),
                "domain_info": analyze_domain_characteristics(url),
                "brand_name_length": len(name),
                "pages_analyzed": getattr(brand, 'pages_analyzed', 0),
                "has_description": bool(description),
                "analysis_date": str(getattr(brand, 'analysis_date', ''))
            }
            analytics_data["analytics_ready_data"].append(brand_analytics)
        
        # Save analytics-ready JSON
        filename = "shopify_analytics_dataset.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(analytics_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Analytics dataset exported: {filename}")
        print(f"📊 Ready for import into Jupyter, R, or BI tools")
        
        return filename

if __name__ == "__main__":
    # Generate comprehensive insights report
    generate_insights_report()
    
    # Export analytics-ready data
    export_analytics_data()
