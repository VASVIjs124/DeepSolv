"""
Top 100 Shopify Stores Database Fixture
Data source: https://webinopoly.com/blogs/news/top-100-most-successful-shopify-stores
"""
import sys
import os

# Add the parent directory to sys.path to import database modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from datetime import datetime
from sqlalchemy.orm import Session
from database.dependencies import get_db_session
from database.crud import BrandCRUD
from models.brand_data import (
    BrandContext, Product, HeroProduct, Policy, FAQ, 
    SocialHandle, ImportantLink, ContactInfo, PolicyType
)

# Top 100 Shopify Stores Data
TOP_100_STORES = [
    {"rank": 1, "domain": "colourpop.com", "brand_name": "ColourPop Cosmetics", "alexa_rank": 3311, "country": "US", "category": "Beauty & Cosmetics"},
    {"rank": 2, "domain": "jeffreestarcosmetics.com", "brand_name": "Jeffree Star Cosmetics", "alexa_rank": 4262, "country": "US", "category": "Beauty & Cosmetics"},
    {"rank": 3, "domain": "fashionnova.com", "brand_name": "Fashion Nova", "alexa_rank": 5015, "country": "US", "category": "Fashion & Apparel"},
    {"rank": 4, "domain": "reddressboutique.com", "brand_name": "Red Dress Boutique", "alexa_rank": 8014, "country": "US", "category": "Fashion & Apparel"},
    {"rank": 5, "domain": "gymshark.com", "brand_name": "Gymshark", "alexa_rank": 9848, "country": "UK", "category": "Fitness & Sports"},
    {"rank": 6, "domain": "cupshe.com", "brand_name": "Cupshe", "alexa_rank": 15785, "country": "US", "category": "Fashion & Swimwear"},
    {"rank": 7, "domain": "omaze.com", "brand_name": "Omaze", "alexa_rank": 16579, "country": "US", "category": "Entertainment & Experiences"},
    {"rank": 8, "domain": "mnml.la", "brand_name": "mnml", "alexa_rank": 17065, "country": "-", "category": "Fashion & Streetwear"},
    {"rank": 9, "domain": "yeezysupply.com", "brand_name": "YEEZY SUPPLY", "alexa_rank": 18729, "country": "UK", "category": "Fashion & Footwear"},
    {"rank": 10, "domain": "kith.com", "brand_name": "Kith", "alexa_rank": 18733, "country": "US", "category": "Fashion & Streetwear"},
    {"rank": 11, "domain": "fangamer.com", "brand_name": "Fangamer", "alexa_rank": 19971, "country": "US", "category": "Gaming & Collectibles"},
    {"rank": 12, "domain": "allbirds.com", "brand_name": "Allbirds", "alexa_rank": 20500, "country": "US", "category": "Fashion & Footwear"},
    {"rank": 13, "domain": "bulletproof.com", "brand_name": "Bulletproof", "alexa_rank": 20676, "country": "US", "category": "Health & Supplements"},
    {"rank": 14, "domain": "gfuel.com", "brand_name": "G FUEL", "alexa_rank": 20869, "country": "US", "category": "Gaming & Energy Drinks"},
    {"rank": 15, "domain": "decathlon.com", "brand_name": "Decathlon", "alexa_rank": 21640, "country": "FR", "category": "Sports & Equipment"},
    {"rank": 16, "domain": "cettire.com", "brand_name": "Cettire", "alexa_rank": 22948, "country": "AU", "category": "Luxury Fashion"},
    {"rank": 17, "domain": "untilgone.com", "brand_name": "UntilGone", "alexa_rank": 23326, "country": "-", "category": "Daily Deals"},
    {"rank": 18, "domain": "inspireuplift.com", "brand_name": "Inspire Uplift", "alexa_rank": 23763, "country": "US", "category": "Home & Lifestyle"},
    {"rank": 19, "domain": "citiesocial.com", "brand_name": "citiesocial", "alexa_rank": 24066, "country": "TW", "category": "Lifestyle Products"},
    {"rank": 20, "domain": "loreta.com.au", "brand_name": "LORETA", "alexa_rank": 25268, "country": "-", "category": "Fashion & Swimwear"},
    {"rank": 21, "domain": "stevemadden.com", "brand_name": "Steve Madden", "alexa_rank": 26367, "country": "US", "category": "Fashion & Footwear"},
    {"rank": 22, "domain": "spigen.com", "brand_name": "Spigen", "alexa_rank": 26698, "country": "US", "category": "Electronics & Accessories"},
    {"rank": 23, "domain": "beeinspiredclothing.com", "brand_name": "Be Inspired", "alexa_rank": 26700, "country": "GB", "category": "Fashion & Streetwear"},
    {"rank": 24, "domain": "fleshlight.com", "brand_name": "Fleshlight", "alexa_rank": 28074, "country": "US", "category": "Adult Products"},
    {"rank": 25, "domain": "usatuan.com", "brand_name": "美国团购网", "alexa_rank": 28259, "country": "US", "category": "Group Buying"},
    {"rank": 26, "domain": "misthub.com", "brand_name": "MistHub", "alexa_rank": 29962, "country": "US", "category": "Vaping Products"},
    {"rank": 27, "domain": "eightvape.com", "brand_name": "EightVape", "alexa_rank": 30667, "country": "US", "category": "Vaping Products"},
    {"rank": 28, "domain": "ripndipclothing.com", "brand_name": "RIPNDIP", "alexa_rank": 30993, "country": "US", "category": "Fashion & Streetwear"},
    {"rank": 29, "domain": "bohme.com", "brand_name": "böhme", "alexa_rank": 32662, "country": "US", "category": "Fashion & Apparel"},
    {"rank": 30, "domain": "creativebooster.net", "brand_name": "CreativeBooster", "alexa_rank": 32798, "country": "PA", "category": "Digital Assets"},
    {"rank": 31, "domain": "bungiestore.com", "brand_name": "Bungie Store", "alexa_rank": 33109, "country": "US", "category": "Gaming & Merchandise"},
    {"rank": 32, "domain": "peakdesign.com", "brand_name": "Peak Design", "alexa_rank": 33666, "country": "US", "category": "Photography & Equipment"},
    {"rank": 33, "domain": "kbdfans.cn", "brand_name": "KBDfans", "alexa_rank": 33866, "country": "-", "category": "Electronics & Keyboards"},
    {"rank": 34, "domain": "sokoglam.com", "brand_name": "Soko Glam", "alexa_rank": 34277, "country": "US", "category": "Beauty & K-Beauty"},
    {"rank": 35, "domain": "huel.com", "brand_name": "Huel", "alexa_rank": 34744, "country": "PA", "category": "Health & Nutrition"},
    {"rank": 36, "domain": "bajaao.com", "brand_name": "Bajaao", "alexa_rank": 36014, "country": "US", "category": "Musical Instruments"},
    {"rank": 37, "domain": "theyetee.com", "brand_name": "The Yetee", "alexa_rank": 36239, "country": "US", "category": "Apparel & Pop Culture"},
    {"rank": 38, "domain": "mavi.com", "brand_name": "Mavi Jeans", "alexa_rank": 36345, "country": "US", "category": "Fashion & Denim"},
    {"rank": 39, "domain": "gouletpens.com", "brand_name": "The Goulet Pen Company", "alexa_rank": 37445, "country": "CA", "category": "Stationery & Pens"},
    {"rank": 40, "domain": "culturekings.com.au", "brand_name": "Culture Kings", "alexa_rank": 37456, "country": "AU", "category": "Fashion & Streetwear"},
    {"rank": 41, "domain": "bettersnatch.com", "brand_name": "BetterSnatch", "alexa_rank": 38154, "country": "US", "category": "Daily Deals"},
    {"rank": 42, "domain": "williampainter.com", "brand_name": "William Painter", "alexa_rank": 38429, "country": "US", "category": "Fashion & Sunglasses"},
    {"rank": 43, "domain": "quickmobilefix.com", "brand_name": "Quick Mobile Fix", "alexa_rank": 38576, "country": "GB", "category": "Electronics & Repair"},
    {"rank": 44, "domain": "ridgewallet.com", "brand_name": "The Ridge Wallet", "alexa_rank": 38812, "country": "US", "category": "Fashion & Accessories"},
    {"rank": 45, "domain": "ocs.ca", "brand_name": "Ontario Cannabis Store", "alexa_rank": 38941, "country": "-", "category": "Cannabis Products"},
    {"rank": 46, "domain": "outdoorvoices.com", "brand_name": "Outdoor Voices", "alexa_rank": 39654, "country": "US", "category": "Fitness & Apparel"},
    {"rank": 47, "domain": "chubbiesshorts.com", "brand_name": "Chubbies Shorts", "alexa_rank": 40157, "country": "US", "category": "Fashion & Swimwear"},
    {"rank": 48, "domain": "bombas.com", "brand_name": "Bombas", "alexa_rank": 40595, "country": "US", "category": "Fashion & Socks"},
    {"rank": 49, "domain": "shopmrbeast.com", "brand_name": "ShopMrBeast", "alexa_rank": 41209, "country": "US", "category": "Entertainment & Merchandise"},
    {"rank": 50, "domain": "islamicity.org", "brand_name": "IslamiCity", "alexa_rank": 41564, "country": "US", "category": "Religious & Community"},
    {"rank": 51, "domain": "kyliecosmetics.com", "brand_name": "Kylie Cosmetics", "alexa_rank": 42262, "country": "US", "category": "Beauty & Cosmetics"},
    {"rank": 52, "domain": "secretlab.co", "brand_name": "Secretlab", "alexa_rank": 42412, "country": "US", "category": "Gaming & Furniture"},
    {"rank": 53, "domain": "teefury.com", "brand_name": "TeeFury", "alexa_rank": 43319, "country": "US", "category": "Apparel & Pop Culture"},
    {"rank": 54, "domain": "manscaped.com", "brand_name": "Manscaped", "alexa_rank": 43501, "country": "US", "category": "Health & Grooming"},
    {"rank": 55, "domain": "halobeauty.com", "brand_name": "HALO BEAUTY", "alexa_rank": 43665, "country": "US", "category": "Beauty & Supplements"},
    {"rank": 56, "domain": "popsockets.com", "brand_name": "PopSockets", "alexa_rank": 43833, "country": "US", "category": "Electronics & Accessories"},
    {"rank": 57, "domain": "bdgastore.com", "brand_name": "Bodega", "alexa_rank": 44309, "country": "US", "category": "Fashion & Streetwear"},
    {"rank": 58, "domain": "vicicollection.com", "brand_name": "VICI", "alexa_rank": 44411, "country": "US", "category": "Fashion & Apparel"},
    {"rank": 59, "domain": "alrugaibfurniture.com", "brand_name": "Al Rugaib Furniture", "alexa_rank": 44495, "country": "IN", "category": "Furniture & Home"},
    {"rank": 60, "domain": "morphebrushes.com", "brand_name": "Morphe", "alexa_rank": 44753, "country": "US", "category": "Beauty & Cosmetics"},
    {"rank": 61, "domain": "puravidabracelets.com", "brand_name": "Pura Vida Bracelets", "alexa_rank": 45080, "country": "US", "category": "Fashion & Jewelry"},
    {"rank": 62, "domain": "deadstock.ca", "brand_name": "Deadstock", "alexa_rank": 46378, "country": "CA", "category": "Fashion & Footwear"},
    {"rank": 63, "domain": "blacktailor.store", "brand_name": "BLACKTAILOR", "alexa_rank": 46674, "country": "-", "category": "Fashion & Streetwear"},
    {"rank": 64, "domain": "wearfigs.com", "brand_name": "FIGS", "alexa_rank": 47121, "country": "US", "category": "Medical & Scrubs"},
    {"rank": 65, "domain": "aloyoga.com", "brand_name": "Alo Yoga", "alexa_rank": 47199, "country": "US", "category": "Fitness & Yoga"},
    {"rank": 66, "domain": "thepihut.com", "brand_name": "The Pi Hut", "alexa_rank": 47753, "country": "GB", "category": "Electronics & Raspberry Pi"},
    {"rank": 67, "domain": "headphonezone.in", "brand_name": "Headphone Zone", "alexa_rank": 47823, "country": "IN", "category": "Electronics & Audio"},
    {"rank": 68, "domain": "fanjoy.co", "brand_name": "Fanjoy", "alexa_rank": 48197, "country": "US", "category": "Entertainment & Merchandise"},
    {"rank": 69, "domain": "soylent.com", "brand_name": "Soylent", "alexa_rank": 48387, "country": "FR", "category": "Health & Nutrition"},
    {"rank": 70, "domain": "havenshop.com", "brand_name": "HAVEN", "alexa_rank": 48704, "country": "CA", "category": "Fashion & Streetwear"},
    {"rank": 71, "domain": "fab.com", "brand_name": "Fab", "alexa_rank": 49294, "country": "IE", "category": "Health & Wellness"},
    {"rank": 72, "domain": "timbuk2.com", "brand_name": "Timbuk2", "alexa_rank": 49477, "country": "US", "category": "Bags & Accessories"},
    {"rank": 73, "domain": "mediamarkt.pt", "brand_name": "Media Markt Portugal", "alexa_rank": 50328, "country": "-", "category": "Electronics & Retail"},
    {"rank": 74, "domain": "victoryhangers.com", "brand_name": "Victory Hangers", "alexa_rank": 50525, "country": "US", "category": "Sports & Awards"},
    {"rank": 75, "domain": "brooklinen.com", "brand_name": "Brooklinen", "alexa_rank": 50726, "country": "US", "category": "Home & Bedding"},
    {"rank": 76, "domain": "behearty.com", "brand_name": "Behearty", "alexa_rank": 50990, "country": "US", "category": "Fashion & Jewelry"},
    {"rank": 77, "domain": "sisterjane.com", "brand_name": "Sister Jane", "alexa_rank": 51029, "country": "JP", "category": "Fashion & Apparel"},
    {"rank": 78, "domain": "heatonist.com", "brand_name": "HEATONIST", "alexa_rank": 51237, "country": "US", "category": "Food & Hot Sauces"},
    {"rank": 79, "domain": "unique-vintage.com", "brand_name": "Unique Vintage", "alexa_rank": 51505, "country": "US", "category": "Fashion & Vintage"},
    {"rank": 80, "domain": "untuckit.com", "brand_name": "UNTUCKit", "alexa_rank": 51609, "country": "US", "category": "Fashion & Apparel"},
    {"rank": 81, "domain": "lackofcolor.com.au", "brand_name": "Lack of Color", "alexa_rank": 53058, "country": "JP", "category": "Fashion & Hats"},
    {"rank": 82, "domain": "crownandcaliber.com", "brand_name": "Crown & Caliber", "alexa_rank": 53178, "country": "US", "category": "Luxury & Watches"},
    {"rank": 83, "domain": "kingice.com", "brand_name": "King Ice", "alexa_rank": 53366, "country": "US", "category": "Fashion & Jewelry"},
    {"rank": 84, "domain": "mirascreen.com", "brand_name": "MiraScreen", "alexa_rank": 53506, "country": "PA", "category": "Electronics & Mirroring"},
    {"rank": 85, "domain": "shethinx.com", "brand_name": "THINX", "alexa_rank": 53547, "country": "US", "category": "Health & Feminine Care"},
    {"rank": 86, "domain": "naturalbabyshower.co.uk", "brand_name": "Natural Baby Shower", "alexa_rank": 54285, "country": "GB", "category": "Baby & Natural Products"},
    {"rank": 87, "domain": "ruggable.com", "brand_name": "Ruggable", "alexa_rank": 54375, "country": "US", "category": "Home & Rugs"},
    {"rank": 88, "domain": "dailysteals.com", "brand_name": "Daily Steals", "alexa_rank": 54511, "country": "US", "category": "Daily Deals & Electronics"},
    {"rank": 89, "domain": "mous.co", "brand_name": "Mous", "alexa_rank": 55224, "country": "FR", "category": "Electronics & Phone Cases"},
    {"rank": 90, "domain": "zoofashions.com", "brand_name": "ZOOFASHIONS", "alexa_rank": 55244, "country": "GB", "category": "Fashion & Menswear"},
    {"rank": 91, "domain": "limitedrungames.com", "brand_name": "Limited Run Games", "alexa_rank": 55326, "country": "US", "category": "Gaming & Collectibles"},
    {"rank": 92, "domain": "teddyfresh.com", "brand_name": "Teddy Fresh", "alexa_rank": 57118, "country": "US", "category": "Fashion & Streetwear"},
    {"rank": 93, "domain": "indestructibleshoes.com", "brand_name": "Indestructible Shoes", "alexa_rank": 57219, "country": "US", "category": "Fashion & Footwear"},
    {"rank": 94, "domain": "livefitapparel.com", "brand_name": "Live Fit Apparel", "alexa_rank": 57512, "country": "US", "category": "Fitness & Apparel"},
    {"rank": 95, "domain": "racedayquads.com", "brand_name": "RaceDayQuads", "alexa_rank": 57788, "country": "CA", "category": "Electronics & Drones"},
    {"rank": 96, "domain": "thebrick.com", "brand_name": "The Brick", "alexa_rank": 58058, "country": "CA", "category": "Furniture & Home"},
    {"rank": 97, "domain": "onewheel.com", "brand_name": "Onewheel", "alexa_rank": 58094, "country": "CA", "category": "Sports & Electric Boards"},
    {"rank": 98, "domain": "mondotees.com", "brand_name": "Mondo", "alexa_rank": 58161, "country": "US", "category": "Art & Collectibles"},
    {"rank": 99, "domain": "hanon-shop.com", "brand_name": "Hanon", "alexa_rank": 58206, "country": "-", "category": "Fashion & Footwear"},
    {"rank": 100, "domain": "pimaxvr.com", "brand_name": "Pimax Technology", "alexa_rank": 58431, "country": "-", "category": "Electronics & VR"}
]

def create_brand_context(store_data: dict) -> BrandContext:
    """Create a BrandContext object with realistic sample data for a store"""
    
    # Generate sample products based on category
    products = []
    category = store_data["category"]
    
    if "Beauty" in category or "Cosmetics" in category:
        products = [
            Product(
                title=f"{store_data['brand_name']} Signature Lipstick",
                description="Long-lasting, highly pigmented lipstick",
                price=24.99,
                available=True,
                url=f"https://{store_data['domain']}/products/signature-lipstick",
                images=[f"https://{store_data['domain']}/images/lipstick.jpg"],
                vendor=store_data['brand_name']
            ),
            Product(
                title=f"{store_data['brand_name']} Foundation",
                description="Full coverage liquid foundation",
                price=42.00,
                available=True,
                url=f"https://{store_data['domain']}/products/foundation",
                images=[f"https://{store_data['domain']}/images/foundation.jpg"],
                vendor=store_data['brand_name']
            )
        ]
    elif "Fashion" in category or "Apparel" in category:
        products = [
            Product(
                title=f"{store_data['brand_name']} Classic T-Shirt",
                description="Premium cotton comfortable fit",
                price=29.99,
                available=True,
                url=f"https://{store_data['domain']}/products/classic-tshirt",
                images=[f"https://{store_data['domain']}/images/tshirt.jpg"],
                vendor=store_data['brand_name']
            ),
            Product(
                title=f"{store_data['brand_name']} Denim Jeans",
                description="Slim fit premium denim",
                price=89.99,
                available=True,
                url=f"https://{store_data['domain']}/products/denim-jeans",
                images=[f"https://{store_data['domain']}/images/jeans.jpg"],
                vendor=store_data['brand_name']
            )
        ]
    elif "Electronics" in category:
        products = [
            Product(
                title=f"{store_data['brand_name']} Wireless Headphones",
                description="High-quality wireless audio experience",
                price=199.99,
                available=True,
                url=f"https://{store_data['domain']}/products/wireless-headphones",
                images=[f"https://{store_data['domain']}/images/headphones.jpg"],
                vendor=store_data['brand_name']
            )
        ]
    elif "Health" in category or "Supplements" in category:
        products = [
            Product(
                title=f"{store_data['brand_name']} Daily Vitamin",
                description="Complete daily nutritional support",
                price=39.99,
                available=True,
                url=f"https://{store_data['domain']}/products/daily-vitamin",
                images=[f"https://{store_data['domain']}/images/vitamin.jpg"],
                vendor=store_data['brand_name']
            )
        ]
    else:
        # Generic products for other categories
        products = [
            Product(
                title=f"{store_data['brand_name']} Bestseller",
                description="Our most popular product",
                price=49.99,
                available=True,
                url=f"https://{store_data['domain']}/products/bestseller",
                images=[f"https://{store_data['domain']}/images/bestseller.jpg"],
                vendor=store_data['brand_name']
            )
        ]

    # Hero products (featured items)
    hero_products = [
        HeroProduct(
            title=f"Featured: {products[0].title}" if products else f"{store_data['brand_name']} Featured Product",
            description="Our top-selling product this season",
            image_url=f"https://{store_data['domain']}/images/hero-banner.jpg",
            product_url=f"https://{store_data['domain']}/collections/featured"
        )
    ]

    # Policies
    policies = [
        Policy(
            type=PolicyType.RETURN,
            title="Return Policy",
            content=f"At {store_data['brand_name']}, we offer 30-day returns on all items. Items must be in original condition with tags attached."
        ),
        Policy(
            type=PolicyType.SHIPPING,
            title="Shipping Policy",
            content=f"Free shipping on orders over $50. Express shipping available. International shipping to select countries."
        ),
        Policy(
            type=PolicyType.PRIVACY,
            title="Privacy Policy",
            content=f"We respect your privacy and protect your personal information according to GDPR and local regulations."
        )
    ]

    # FAQs
    faqs = [
        FAQ(
            question="How long does shipping take?",
            answer="Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days."
        ),
        FAQ(
            question="What is your return policy?",
            answer="We offer 30-day returns on all items in original condition."
        )
    ]

    # Social handles
    social_handles = [
        SocialHandle(
            platform="instagram",
            username=f"@{store_data['brand_name'].lower().replace(' ', '')}",
            url=f"https://instagram.com/{store_data['brand_name'].lower().replace(' ', '')}",
            followers_count=50000 + (store_data['rank'] * 1000)  # Simulate follower count
        ),
        SocialHandle(
            platform="facebook",
            username=f"{store_data['brand_name']}",
            url=f"https://facebook.com/{store_data['brand_name'].lower().replace(' ', '')}",
            followers_count=30000 + (store_data['rank'] * 800)
        )
    ]

    # Important links
    important_links = [
        ImportantLink(
            title="Size Guide",
            url=f"https://{store_data['domain']}/pages/size-guide",
            type="help"
        ),
        ImportantLink(
            title="Track Order",
            url=f"https://{store_data['domain']}/pages/track-order",
            type="service"
        )
    ]

    # Contact information
    contact_info = ContactInfo(
        email=f"support@{store_data['domain']}",
        phone="+1-555-0123",
        address=f"{store_data['brand_name']} Store, {store_data['country']}",
        business_hours="Mon-Fri: 9AM-6PM",
        support_email=f"help@{store_data['domain']}"
    )

    return BrandContext(
        brand_name=store_data["brand_name"],
        website_url=f"https://{store_data['domain']}",
        description=f"{store_data['brand_name']} - {category} brand ranked #{store_data['rank']} among top Shopify stores",
        category=category,
        country=store_data["country"] if store_data["country"] != "-" else "Unknown",
        alexa_rank=store_data["alexa_rank"],
        shopify_rank=store_data["rank"],
        pages_analyzed=8,
        analysis_date=datetime.now(),
        products=products,
        hero_products=hero_products,
        policies=policies,
        faqs=faqs,
        social_handles=social_handles,
        important_links=important_links,
        contact_info=contact_info
    )

def load_top_100_shopify_stores():
    """Load all top 100 Shopify stores into the database"""
    
    print("🚀 Loading Top 100 Shopify Stores Database...")
    print("=" * 60)
    
    # Get database session using context manager
    with get_db_session() as session:
        loaded_count = 0
        categories = set()
        countries = set()
        
        for store_data in TOP_100_STORES:
            print(f"Loading #{store_data['rank']}: {store_data['brand_name']} ({store_data['domain']})")
            
            # Check if brand already exists
            existing_brand = BrandCRUD.get_brand_by_url(session, f"https://{store_data['domain']}")
            if existing_brand:
                print(f"  ⚠️  Brand already exists, skipping...")
                continue
            
            # Create brand context
            brand_context = create_brand_context(store_data)
            
            # Save to database
            try:
                saved_brand = BrandCRUD.create_or_update_brand(session, brand_context)
                loaded_count += 1
                categories.add(store_data['category'])
                countries.add(store_data['country'])
                print(f"  ✅ Successfully loaded!")
            except Exception as e:
                print(f"  ❌ Error loading: {str(e)}")
                continue
        
        print("=" * 60)
        print(f"🎉 Database Loading Complete!")
        print(f"📊 Statistics:")
        print(f"   • Total Brands Loaded: {loaded_count}")
        print(f"   • Categories: {len(categories)}")
        print(f"   • Countries: {len([c for c in countries if c != '-'])}")
        print(f"   • Top Category: Fashion & Apparel")
        print(f"   • Top Country: US")
        
        print(f"\n📈 Top Categories:")
        category_counts = {}
        for store in TOP_100_STORES:
            cat = store['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {cat}: {count} stores")
            
        print(f"\n🌍 Top Countries:")
        country_counts = {}
        for store in TOP_100_STORES:
            country = store['country']
            if country != '-':
                country_counts[country] = country_counts.get(country, 0) + 1
        
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {country}: {count} stores")
            
        print(f"\n🏆 Top 10 Brands by Alexa Rank:")
        for store in TOP_100_STORES[:10]:
            print(f"   #{store['rank']}: {store['brand_name']} ({store['domain']}) - Alexa: {store['alexa_rank']:,}")
            
        return loaded_count

if __name__ == "__main__":
    loaded_count = load_top_100_shopify_stores()
    print(f"\n✨ Database population complete! Loaded {loaded_count} brands.")
