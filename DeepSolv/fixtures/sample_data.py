"""
Sample data fixtures for testing the Shopify Store Insights application
"""
from datetime import datetime, timezone
from database.crud import BrandCRUD
from database.dependencies import get_db_session
from models.brand_data import (
    BrandContext, Product, HeroProduct, Policy, FAQ, 
    SocialHandle, ContactInfo, ImportantLink, PolicyType,
    ProductVariant
)


def load_sample_data():
    """
    Load sample brand data for demonstration purposes
    """
    # Sample brand context data
    sample_brands = [
        BrandContext(
            website_url="https://allbirds.com",
            brand_name="Allbirds",
            brand_description="Sustainable footwear made from natural materials",
            product_catalog=[
                Product(
                    id="123456789",
                    title="Tree Runners",
                    description="Our most comfortable shoe yet",
                    price=98.00,
                    compare_at_price=120.00,
                    url="https://allbirds.com/products/mens-tree-runners",
                    available=True,
                    variants=[
                        ProductVariant(
                            id=1,
                            title="Size 9 / Natural White",
                            price="98.00",
                            available=True
                        )
                    ]
                )
            ],
            hero_products=[
                HeroProduct(
                    title="Tree Runners",
                    price="$98",
                    description="Made from eucalyptus tree fiber",
                    image_url="https://cdn.allbirds.com/hero-runner.jpg",
                    product_url="/collections/mens-tree-runners"
                )
            ],
            policies=[
                Policy(
                    type=PolicyType.SHIPPING,
                    title="Free Shipping",
                    content="We offer free shipping on all orders over $75 within the continental United States.",
                    url="/pages/shipping-policy"
                ),
                Policy(
                    type=PolicyType.RETURN,
                    title="30-Day Returns",
                    content="Return your shoes within 30 days for a full refund, no questions asked.",
                    url="/pages/return-policy"
                )
            ],
            faqs=[
                FAQ(
                    question="Are Allbirds machine washable?",
                    answer="Yes! Most Allbirds can be machine washed in cold water on a gentle cycle.",
                    category="Care"
                ),
                FAQ(
                    question="What sizes do you offer?",
                    answer="We offer sizes from 8-14 for men and 5-11 for women in most styles.",
                    category="Sizing"
                )
            ],
            social_handles=[
                SocialHandle(
                    platform="instagram",
                    username="allbirds",
                    url="https://instagram.com/allbirds",
                    followers_count=500000
                ),
                SocialHandle(
                    platform="twitter",
                    username="allbirds",
                    url="https://twitter.com/allbirds",
                    followers_count=75000
                )
            ],
            contact_info=ContactInfo(
                emails=["help@allbirds.com"],
                phone_numbers=["+1-888-963-8944"],
                support_hours="Mon-Fri 9AM-6PM PST"
            ),
            important_links=[
                ImportantLink(
                    title="Our Materials",
                    url="/pages/our-materials",
                    type="about"
                ),
                ImportantLink(
                    title="Store Locator", 
                    url="/pages/stores",
                    type="contact"
                )
            ],
            competitors=[
                "https://bombas.com",
                "https://rothy.com",
                "https://atoms.com"
            ],
            analysis_date=datetime.now(),
            pages_analyzed=12
        ),
        BrandContext(
            website_url="https://warbyparker.com",
            brand_name="Warby Parker",
            brand_description="High-quality prescription glasses, sunglasses, and eye exams",
            product_catalog=[
                Product(
                    id="987654321",
                    title="The Percey",
                    description="Classic rectangular frames",
                    price=95.00,
                    url="https://warbyparker.com/eyeglasses/women/percey",
                    available=True,
                    variants=[
                        ProductVariant(
                            id=2,
                            title="Whiskey Tortoise",
                            price="95.00",
                            available=True
                        )
                    ]
                )
            ],
            hero_products=[
                HeroProduct(
                    title="The Percey",
                    price="$95",
                    description="Stylish frames for every face",
                    image_url="https://cdn.warbyparker.com/hero-percey.jpg",
                    product_url="/eyeglasses/women/percey"
                )
            ],
            policies=[
                Policy(
                    type=PolicyType.RETURN,
                    title="30-Day Return Policy",
                    content="Don't love your glasses? Return them within 30 days for a full refund.",
                    url="/return-policy"
                )
            ],
            faqs=[
                FAQ(
                    question="How do I know if glasses will fit me?",
                    answer="Use our Virtual Try-On feature or order our Home Try-On kit with 5 frames.",
                    category="Fitting"
                )
            ],
            social_handles=[
                SocialHandle(
                    platform="instagram",
                    username="warbyparker",
                    url="https://instagram.com/warbyparker",
                    followers_count=800000
                )
            ],
            contact_info=ContactInfo(
                emails=["help@warbyparker.com"]
            ),
            important_links=[
                ImportantLink(
                    title="Home Try-On",
                    url="/home-try-on",
                    type="order_tracking"
                )
            ],
            competitors=[
                "https://zenni.com",
                "https://eyebuydirect.com"
            ],
            analysis_date=datetime.now(),
            pages_analyzed=15
        )
    ]
    
    # Load data into database
    with get_db_session() as db:
        for brand_context in sample_brands:
            try:
                existing_brand = BrandCRUD.get_brand_by_url(db, brand_context.website_url)
                if not existing_brand:
                    BrandCRUD.create_or_update_brand(db, brand_context)
                    print(f"Added sample data for {brand_context.brand_name}")
                else:
                    print(f"Sample data for {brand_context.brand_name} already exists")
            except Exception as e:
                print(f"Error adding sample data for {brand_context.brand_name}: {e}")


if __name__ == "__main__":
    print("Loading sample brand data...")
    load_sample_data()
    print("Sample data loading complete!")
