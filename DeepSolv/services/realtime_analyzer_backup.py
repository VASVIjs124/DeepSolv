"""
Real-time Shopify Store Database Integration
Integrates real-time fetched data with the database and provides comprehensive analysis
"""
import sys
import os

# A    def _convert_insights_to_brand_context(self, insights: StoreInsights) -> BrandContext:
        """Convert StoreInsights to database format"""
        
        # Null-safe attribute access
        def safe_get(obj, key, default=None):
            """Safely get attribute from object, handling None values"""
            if obj is None:
                return default
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)
        
        # Basic brand information with null safety
        basic_info = safe_get(insights, 'basic_info', {})
        brand_name = safe_get(basic_info, 'brand_name', 'Unknown Brand')
        website_url = safe_get(basic_info, 'website_url', '')
        description = safe_get(basic_info, 'description', '')arent directory to sys.path to import database modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from sqlalchemy.orm import Session
from database.dependencies import SessionLocal
from database.crud import BrandCRUD
from models.brand_data import (
    BrandContext, Product, HeroProduct, Policy, FAQ, 
    SocialHandle, ImportantLink, ContactInfo, PolicyType
)
from services.realtime_fetcher import ShopifyStoreFetcher, StoreInsights
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeStoreAnalyzer:
    """Real-time Shopify store analyzer with database integration"""
    
    def __init__(self):
        self.fetcher = ShopifyStoreFetcher()
    
    def analyze_and_store_shop(self, url: str, save_to_db: bool = True) -> Dict[str, Any]:
        """Analyze a Shopify store in real-time and optionally save to database"""
        
        logger.info(f"🔍 Starting real-time analysis of: {url}")
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            # Fetch comprehensive insights
            insights = self.fetcher.fetch_comprehensive_insights(url)
            
            # Convert insights to database format
            brand_context = self._convert_insights_to_brand_context(insights)
            
            # Save to database if requested
            if save_to_db:
                session = SessionLocal()
                try:
                    # Check if brand already exists
                    existing_brand = BrandCRUD.get_brand_by_url(session, url)
                    
                    if existing_brand:
                        logger.info(f"📝 Updating existing brand: {brand_context.brand_name}")
                        updated_brand = BrandCRUD.create_or_update_brand(session, brand_context)
                        brand_id = updated_brand.id
                    else:
                        logger.info(f"🆕 Creating new brand: {brand_context.brand_name}")
                        new_brand = BrandCRUD.create_or_update_brand(session, brand_context)
                        brand_id = new_brand.id
                    
                    session.commit()
                except Exception as db_error:
                    session.rollback()
                    logger.error(f"Database operation failed: {db_error}")
                    brand_id = None
                finally:
                    session.close()
            else:
                brand_id = None
            
            # Generate comprehensive analysis report
            analysis_report = self._generate_analysis_report(insights, brand_context)
            
            logger.info(f"✅ Analysis completed for {brand_context.brand_name}")
            
            return {
                'success': True,
                'brand_id': brand_id,
                'brand_name': brand_context.brand_name,
                'website_url': url,
                'analysis_timestamp': datetime.now().isoformat(),
                'insights': analysis_report,
                'saved_to_database': save_to_db,
                'data_quality_score': self._calculate_data_quality_score(insights),
                'competitive_metrics': self._generate_competitive_metrics(insights),
                'recommendations': self._generate_recommendations(insights)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'website_url': url,
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def bulk_analyze_stores(self, urls: List[str], save_to_db: bool = True) -> List[Dict[str, Any]]:
        """Analyze multiple stores in bulk"""
        
        logger.info(f"🔄 Starting bulk analysis of {len(urls)} stores")
        
        results = []
        successful_analyses = 0
        
        for i, url in enumerate(urls, 1):
            logger.info(f"📊 Analyzing store {i}/{len(urls)}: {url}")
            
            try:
                result = self.analyze_and_store_shop(url, save_to_db)
                results.append(result)
                
                if result['success']:
                    successful_analyses += 1
                    
            except Exception as e:
                logger.error(f"❌ Failed to analyze {url}: {str(e)}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'website_url': url,
                    'analysis_timestamp': datetime.now().isoformat()
                })
        
        logger.info(f"🎉 Bulk analysis completed: {successful_analyses}/{len(urls)} successful")
        
        # Generate bulk analysis summary
        summary = self._generate_bulk_analysis_summary(results)
        
        return {
            'bulk_analysis_summary': summary,
            'individual_results': results,
            'total_stores': len(urls),
            'successful_analyses': successful_analyses,
            'success_rate': successful_analyses / len(urls) * 100 if urls else 0
        }
    
    def get_real_time_comparison(self, urls: List[str]) -> Dict[str, Any]:
        """Compare multiple stores in real-time without saving to database"""
        
        logger.info(f"⚖️ Starting real-time comparison of {len(urls)} stores")
        
        store_data = []
        
        for url in urls:
            try:
                insights = self.fetcher.fetch_comprehensive_insights(url)
                analysis = self._generate_analysis_report(insights, None)
                store_data.append({
                    'url': url,
                    'brand_name': insights.basic_info.get('brand_name', 'Unknown'),
                    'analysis': analysis
                })
            except Exception as e:
                logger.error(f"Error analyzing {url} for comparison: {e}")
                continue
        
        # Generate comparison analysis
        comparison_analysis = self._generate_comparison_analysis(store_data)
        
        return {
            'comparison_timestamp': datetime.now().isoformat(),
            'stores_compared': len(store_data),
            'comparison_analysis': comparison_analysis,
            'store_details': store_data
        }
    
    def _convert_insights_to_brand_context(self, insights: StoreInsights) -> BrandContext:
        """Convert StoreInsights to BrandContext for database storage"""
        
        # Basic brand information
        basic_info = insights.basic_info
        brand_name = basic_info.get('brand_name', 'Unknown Brand')
        website_url = basic_info.get('website_url', '')
        description = basic_info.get('description', '')
        
        # Convert products
        products = []
        for product_data in insights.products[:20]:  # Limit to 20 products
            try:
                product = Product(
                    title=product_data.get('title', '')[:100],  # Limit title length
                    description=product_data.get('description', '')[:500],  # Limit description
                    price=product_data.get('price_min', 0.0),
                    available=True,  # Assume available if in products.json
                    url=product_data.get('url', ''),
                    images=[product_data.get('featured_image', '')] if product_data.get('featured_image') else [],
                    vendor=product_data.get('vendor', brand_name)
                )
                products.append(product)
            except Exception as e:
                logger.warning(f"Error converting product: {e}")
                continue
        
        # Convert hero products (use first few products as hero products)
        hero_products = []
        for product_data in insights.products[:3]:  # Use first 3 as hero products
            try:
                hero_product = HeroProduct(
                    title=product_data.get('title', '')[:100],
                    description=product_data.get('description', '')[:200],
                    image_url=product_data.get('featured_image', ''),
                    product_url=product_data.get('url', '')
                )
                hero_products.append(hero_product)
            except Exception as e:
                logger.warning(f"Error converting hero product: {e}")
                continue
        
        # Convert policies
        policies = []
        policy_mapping = {
            'privacy': PolicyType.PRIVACY,
            'terms': PolicyType.TERMS,
            'shipping': PolicyType.SHIPPING,
            'returns': PolicyType.RETURN,
            'refunds': PolicyType.RETURN
        }
        
        for policy_key, policy_content in insights.policies.items():
            if policy_key in policy_mapping:
                try:
                    policy = Policy(
                        type=policy_mapping[policy_key],
                        title=policy_key.replace('_', ' ').title() + ' Policy',
                        content=policy_content[:1000]  # Limit content length
                    )
                    policies.append(policy)
                except Exception as e:
                    logger.warning(f"Error converting policy {policy_key}: {e}")
                    continue
        
        # Create FAQs from analysis insights
        faqs = []
        try:
            seo_analysis = insights.seo_analysis
            performance = insights.performance_metrics
            
            if 'load_time' in performance:
                faqs.append(FAQ(
                    question="How fast does the website load?",
                    answer=f"The website loads in {performance['load_time']:.2f} seconds."
                ))
            
            if seo_analysis.get('title', {}).get('length'):
                title_len = seo_analysis['title']['length']
                faqs.append(FAQ(
                    question="Is the website optimized for search engines?",
                    answer=f"The page title is {title_len} characters long, which is {'optimal' if 30 <= title_len <= 60 else 'not optimal'} for SEO."
                ))
        except Exception as e:
            logger.warning(f"Error creating FAQs: {e}")
        
        # Convert social media handles
        social_handles = []
        social_media_data = getattr(insights, 'social_media', {})
        
        # Handle different social media data structures
        if hasattr(social_media_data, 'items'):
            # If it's a dictionary
            for platform, social_data in social_media_data.items():
                try:
                    if isinstance(social_data, dict):
                        social_handle = SocialHandle(
                            platform=platform,
                            username=social_data.get('username', ''),
                            url=social_data.get('url', ''),
                            followers_count=0  # Real follower count would require additional API calls
                        )
                        social_handles.append(social_handle)
                    elif isinstance(social_data, str):
                        # If social_data is a string (URL), create a simple social handle
                        social_handle = SocialHandle(
                            platform=platform,
                            username=platform,
                            url=social_data,
                            followers_count=0
                        )
                        social_handles.append(social_handle)
                except Exception as e:
                    logger.warning(f"Error processing social media data for {platform}: {e}")
        elif hasattr(insights, 'social_media_presence') and hasattr(insights.social_media_presence, 'platforms'):
            # Handle social_media_presence structure
            for platform in insights.social_media_presence.platforms:
                try:
                    social_handle = SocialHandle(
                        platform=platform,
                        username=platform,
                        url=f"https://{platform}.com/{insights.brand_name or ''}",
                        followers_count=0
                    )
                    social_handles.append(social_handle)
                except Exception as e:
                    logger.warning(f"Error processing social media platform {platform}: {e}")
        
        # Create important links
        important_links = []
        try:
            for collection in insights.collections[:5]:  # Top 5 collections as important links
                link = ImportantLink(
                    title=collection.get('title', ''),
                    url=collection.get('url', ''),
                    type='collection'
                )
                important_links.append(link)
        except Exception as e:
            logger.warning(f"Error creating important links: {e}")
        
        # Create contact info
        contact_info = None
        try:
            contact_data = basic_info.get('contact_info', {})
            emails = contact_data.get('emails', [])
            phones = contact_data.get('phones', [])
            
            if emails or phones:
                contact_info = ContactInfo(
                    emails=emails,
                    phone_numbers=phones,
                    addresses=[],  # Would need additional scraping
                    support_hours=None  # Would need additional scraping
                )
        except Exception as e:
            logger.warning(f"Error creating contact info: {e}")
        
        # Extract additional metadata
        shopify_analysis = insights.shopify_analysis
        theme_name = shopify_analysis.get('theme', {}).get('theme_name', 'Unknown')
        apps_detected = shopify_analysis.get('apps_detected', [])
        
        return BrandContext(
            brand_name=brand_name,
            website_url=website_url,
            brand_description=description,
            about_us=f"Real-time analysis completed on {datetime.now().strftime('%Y-%m-%d')}",
            brand_story=f"Shopify store using {theme_name} theme with {len(apps_detected)} detected apps",
            shopify_theme=theme_name,
            apps_detected=apps_detected,
            pages_analyzed=len([insights.basic_info, insights.products, insights.collections, 
                             insights.seo_analysis, insights.performance_metrics]),
            analysis_date=datetime.now(),
            product_catalog=products,
            product_count=len(products),
            hero_products=hero_products,
            policies=policies,
            faqs=faqs,
            social_handles=social_handles,
            important_links=important_links,
            contact_info=contact_info
        )
    
    def _generate_analysis_report(self, insights: StoreInsights, brand_context: Optional[BrandContext]) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        basic_info = insights.basic_info
        products = insights.products
        seo_analysis = insights.seo_analysis
        performance = insights.performance_metrics
        shopify_analysis = insights.shopify_analysis
        social_media = insights.social_media
        competitive_analysis = insights.competitive_analysis
        
        return {
            'store_overview': {
                'brand_name': basic_info.get('brand_name', 'Unknown'),
                'is_shopify_store': basic_info.get('is_shopify', False),
                'theme': shopify_analysis.get('theme', {}),
                'total_products': len(products),
                'total_collections': len(insights.collections),
                'apps_detected': shopify_analysis.get('apps_detected', []),
                'is_shopify_plus': shopify_analysis.get('is_shopify_plus', False)
            },
            'seo_analysis': {
                'title_optimization': seo_analysis.get('title', {}).get('optimal', False),
                'meta_description_optimization': seo_analysis.get('meta_description', {}).get('optimal', False),
                'images_with_alt_tags': seo_analysis.get('images', {}).get('alt_optimization', 0),
                'page_load_time': seo_analysis.get('page_load_time', 0),
                'has_schema_markup': seo_analysis.get('schema_markup', {}).get('has_schema', False)
            },
            'performance_analysis': {
                'load_time': performance.get('load_time', 0),
                'page_size_kb': performance.get('response_size', 0) / 1024,
                'resources_count': {
                    'stylesheets': performance.get('resources', {}).get('stylesheets', 0),
                    'scripts': performance.get('resources', {}).get('scripts', 0),
                    'images': performance.get('resources', {}).get('images', 0)
                },
                'compression_enabled': performance.get('compression', {}).get('gzip_enabled', False)
            },
            'product_analysis': {
                'total_products': len(products),
                'price_range': competitive_analysis.get('price_analysis', {}),
                'category_distribution': competitive_analysis.get('category_distribution', {}),
                'products_with_images': competitive_analysis.get('product_metrics', {}).get('products_with_images', 0),
                'content_quality': competitive_analysis.get('content_analysis', {})
            },
            'social_media_presence': {
                'platforms_found': len(social_media),
                'platforms': list(social_media.keys())
            },
            'ecommerce_features': {
                'payment_methods': shopify_analysis.get('payment_methods', []),
                'shipping_features': shopify_analysis.get('shipping_info', {}),
                'cart_features': shopify_analysis.get('cart_features', {}),
                'api_accessibility': shopify_analysis.get('api_endpoints_accessible', {})
            }
        }
    
    def _calculate_data_quality_score(self, insights: StoreInsights) -> float:
        """Calculate a data quality score based on available information"""
        
        score = 0
        max_score = 100
        
        # Basic info completeness (20 points)
        basic_info = insights.basic_info
        if basic_info.get('brand_name'):
            score += 5
        if basic_info.get('description'):
            score += 5
        if basic_info.get('favicon_url'):
            score += 5
        if basic_info.get('is_shopify'):
            score += 5
        
        # Product data quality (30 points)
        products = insights.products
        if products:
            score += 10
            products_with_prices = sum(1 for p in products if 'price_min' in p and p['price_min'] > 0)
            if products_with_prices > len(products) * 0.5:  # More than 50% have prices
                score += 10
            products_with_images = sum(1 for p in products if 'featured_image' in p and p['featured_image'])
            if products_with_images > len(products) * 0.5:  # More than 50% have images
                score += 10
        
        # SEO quality (20 points)
        seo = insights.seo_analysis
        if seo.get('title', {}).get('optimal'):
            score += 5
        if seo.get('meta_description', {}).get('optimal'):
            score += 5
        if seo.get('images', {}).get('alt_optimization', 0) > 70:  # More than 70% images have alt tags
            score += 5
        if seo.get('schema_markup', {}).get('has_schema'):
            score += 5
        
        # Social media presence (15 points)
        if len(insights.social_media) >= 3:
            score += 15
        elif len(insights.social_media) >= 1:
            score += 8
        
        # Performance (15 points)
        performance = insights.performance_metrics
        load_time = performance.get('load_time', 10)
        if load_time < 2:
            score += 10
        elif load_time < 4:
            score += 5
        
        if performance.get('compression', {}).get('gzip_enabled'):
            score += 5
        
        return min(score, max_score)
    
    def _generate_competitive_metrics(self, insights: StoreInsights) -> Dict[str, Any]:
        """Generate competitive analysis metrics"""
        
        competitive = insights.competitive_analysis
        products = insights.products
        
        metrics = {
            'product_portfolio': {
                'total_products': len(products),
                'categories': len(competitive.get('category_distribution', {})),
                'avg_price': competitive.get('price_analysis', {}).get('avg_price', 0),
                'price_range_span': competitive.get('price_analysis', {}).get('price_range', 0)
            },
            'content_quality': {
                'avg_title_length': competitive.get('content_analysis', {}).get('avg_title_length', 0),
                'products_with_descriptions': competitive.get('content_analysis', {}).get('products_with_descriptions', 0),
                'seo_optimization_score': self._calculate_seo_score(insights.seo_analysis)
            },
            'technical_performance': {
                'load_time': insights.performance_metrics.get('load_time', 0),
                'mobile_optimized': insights.seo_analysis.get('mobile_friendly', True),  # Assume mobile friendly
                'apps_count': len(insights.shopify_analysis.get('apps_detected', []))
            },
            'market_positioning': {
                'price_tier': self._classify_price_tier(competitive.get('price_analysis', {})),
                'primary_category': max(competitive.get('category_distribution', {}).items(), 
                                      key=lambda x: x[1])[0] if competitive.get('category_distribution') else 'Unknown',
                'social_media_presence': len(insights.social_media)
            }
        }
        
        return metrics
    
    def _generate_recommendations(self, insights: StoreInsights) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # SEO recommendations
        seo = insights.seo_analysis
        if not seo.get('title', {}).get('optimal'):
            recommendations.append({
                'category': 'SEO',
                'priority': 'High',
                'issue': 'Page title length is not optimal',
                'recommendation': 'Optimize page title to be between 30-60 characters for better search engine visibility'
            })
        
        if not seo.get('meta_description', {}).get('optimal'):
            recommendations.append({
                'category': 'SEO',
                'priority': 'High',
                'issue': 'Meta description length is not optimal',
                'recommendation': 'Create compelling meta descriptions between 120-160 characters'
            })
        
        # Performance recommendations
        performance = insights.performance_metrics
        load_time = performance.get('load_time', 0)
        if load_time > 3:
            recommendations.append({
                'category': 'Performance',
                'priority': 'High',
                'issue': f'Page load time is {load_time:.2f} seconds',
                'recommendation': 'Optimize images, enable compression, and minimize JavaScript to improve load times'
            })
        
        # Product recommendations
        competitive = insights.competitive_analysis
        products_with_images = competitive.get('product_metrics', {}).get('products_with_images', 0)
        total_products = len(insights.products)
        
        if total_products > 0 and products_with_images / total_products < 0.8:
            recommendations.append({
                'category': 'Product Management',
                'priority': 'Medium',
                'issue': 'Some products missing featured images',
                'recommendation': 'Add high-quality featured images to all products to improve conversion rates'
            })
        
        # Social media recommendations
        if len(insights.social_media) < 3:
            recommendations.append({
                'category': 'Marketing',
                'priority': 'Medium',
                'issue': 'Limited social media presence',
                'recommendation': 'Expand social media presence to Instagram, Facebook, and other relevant platforms'
            })
        
        # Apps and features recommendations
        apps = insights.shopify_analysis.get('apps_detected', [])
        if not any('review' in app.lower() for app in apps):
            recommendations.append({
                'category': 'Customer Experience',
                'priority': 'Medium',
                'issue': 'No product review system detected',
                'recommendation': 'Implement a product review system to build trust and improve conversions'
            })
        
        return recommendations
    
    def _calculate_seo_score(self, seo_analysis: Dict) -> float:
        """Calculate SEO score"""
        score = 0
        
        if seo_analysis.get('title', {}).get('optimal'):
            score += 25
        if seo_analysis.get('meta_description', {}).get('optimal'):
            score += 25
        if seo_analysis.get('images', {}).get('alt_optimization', 0) > 80:
            score += 25
        if seo_analysis.get('schema_markup', {}).get('has_schema'):
            score += 25
        
        return score
    
    def _classify_price_tier(self, price_analysis: Dict) -> str:
        """Classify store into price tier"""
        avg_price = price_analysis.get('avg_price', 0)
        
        if avg_price < 25:
            return 'Budget'
        elif avg_price < 100:
            return 'Mid-range'
        elif avg_price < 300:
            return 'Premium'
        else:
            return 'Luxury'
    
    def _generate_bulk_analysis_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate summary for bulk analysis"""
        
        successful_results = [r for r in results if r.get('success')]
        
        if not successful_results:
            return {'error': 'No successful analyses to summarize'}
        
        # Aggregate metrics
        total_products = sum(r.get('insights', {}).get('store_overview', {}).get('total_products', 0) 
                           for r in successful_results)
        
        avg_load_time = sum(r.get('insights', {}).get('performance_analysis', {}).get('load_time', 0) 
                          for r in successful_results) / len(successful_results)
        
        all_categories = []
        all_apps = []
        
        for result in successful_results:
            insights = result.get('insights', {})
            product_analysis = insights.get('product_analysis', {})
            store_overview = insights.get('store_overview', {})
            
            all_categories.extend(product_analysis.get('category_distribution', {}).keys())
            all_apps.extend(store_overview.get('apps_detected', []))
        
        return {
            'summary_timestamp': datetime.now().isoformat(),
            'stores_analyzed': len(successful_results),
            'aggregate_metrics': {
                'total_products_across_stores': total_products,
                'average_load_time': avg_load_time,
                'unique_categories': len(set(all_categories)),
                'unique_apps_detected': len(set(all_apps)),
                'stores_with_social_media': len([r for r in successful_results 
                                               if r.get('insights', {}).get('social_media_presence', {}).get('platforms_found', 0) > 0])
            },
            'quality_metrics': {
                'avg_data_quality_score': sum(r.get('data_quality_score', 0) for r in successful_results) / len(successful_results),
                'stores_above_80_quality': len([r for r in successful_results if r.get('data_quality_score', 0) > 80]),
                'stores_needing_improvement': len([r for r in successful_results if r.get('data_quality_score', 0) < 60])
            },
            'top_recommendations': self._aggregate_recommendations(successful_results)
        }
    
    def _aggregate_recommendations(self, results: List[Dict]) -> List[Dict]:
        """Aggregate recommendations from multiple analyses"""
        
        recommendation_counts = {}
        
        for result in results:
            recommendations = result.get('recommendations', [])
            for rec in recommendations:
                key = f"{rec['category']} - {rec['issue']}"
                if key not in recommendation_counts:
                    recommendation_counts[key] = {
                        'count': 0,
                        'recommendation': rec
                    }
                recommendation_counts[key]['count'] += 1
        
        # Sort by frequency and return top 5
        top_recommendations = sorted(recommendation_counts.items(), 
                                   key=lambda x: x[1]['count'], reverse=True)[:5]
        
        return [{
            'recommendation': item[1]['recommendation'],
            'frequency': item[1]['count'],
            'percentage': item[1]['count'] / len(results) * 100
        } for item in top_recommendations]
    
    def _generate_comparison_analysis(self, store_data: List[Dict]) -> Dict[str, Any]:
        """Generate comparison analysis between multiple stores"""
        
        if len(store_data) < 2:
            return {'error': 'Need at least 2 stores for comparison'}
        
        # Compare key metrics
        comparison_metrics = {
            'load_times': {},
            'product_counts': {},
            'seo_scores': {},
            'social_media_presence': {},
            'price_tiers': {}
        }
        
        for store in store_data:
            brand_name = store['brand_name']
            analysis = store['analysis']
            
            comparison_metrics['load_times'][brand_name] = analysis.get('performance_analysis', {}).get('load_time', 0)
            comparison_metrics['product_counts'][brand_name] = analysis.get('store_overview', {}).get('total_products', 0)
            comparison_metrics['seo_scores'][brand_name] = analysis.get('seo_analysis', {})
            comparison_metrics['social_media_presence'][brand_name] = analysis.get('social_media_presence', {}).get('platforms_found', 0)
        
        # Find leaders in each category
        leaders = {
            'fastest_loading': min(comparison_metrics['load_times'].items(), key=lambda x: x[1])[0],
            'most_products': max(comparison_metrics['product_counts'].items(), key=lambda x: x[1])[0],
            'best_social_presence': max(comparison_metrics['social_media_presence'].items(), key=lambda x: x[1])[0]
        }
        
        return {
            'comparison_metrics': comparison_metrics,
            'leaders': leaders,
            'insights': {
                'performance_leader': leaders['fastest_loading'],
                'product_catalog_leader': leaders['most_products'],
                'social_media_leader': leaders['best_social_presence']
            }
        }

# CLI Interface for easy testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Shopify Store Analyzer')
    parser.add_argument('--url', type=str, help='Single store URL to analyze')
    parser.add_argument('--urls', nargs='+', help='Multiple store URLs for bulk analysis')
    parser.add_argument('--compare', nargs='+', help='URLs to compare (no database save)')
    parser.add_argument('--no-save', action='store_true', help='Don\'t save to database')
    
    args = parser.parse_args()
    
    analyzer = RealtimeStoreAnalyzer()
    
    if args.url:
        # Single store analysis
        result = analyzer.analyze_and_store_shop(args.url, not args.no_save)
        print(json.dumps(result, indent=2, default=str))
    
    elif args.urls:
        # Bulk analysis
        result = analyzer.bulk_analyze_stores(args.urls, not args.no_save)
        print(json.dumps(result, indent=2, default=str))
    
    elif args.compare:
        # Comparison analysis
        result = analyzer.get_real_time_comparison(args.compare)
        print(json.dumps(result, indent=2, default=str))
    
    else:
        # Interactive mode
        print("🛍️  Real-time Shopify Store Analyzer")
        print("Enter a store URL to analyze (or 'quit' to exit):")
        
        while True:
            url = input("> ").strip()
            if url.lower() == 'quit':
                break
            
            if url:
                try:
                    result = analyzer.analyze_and_store_shop(url)
                    print(f"\n✅ Analysis completed for: {result.get('brand_name', url)}")
                    print(f"📊 Data Quality Score: {result.get('data_quality_score', 0):.1f}/100")
                    print(f"🔧 Recommendations: {len(result.get('recommendations', []))}")
                    print(f"💾 Saved to database: {result.get('saved_to_database', False)}")
                    print("-" * 50)
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("Please enter a valid URL")
