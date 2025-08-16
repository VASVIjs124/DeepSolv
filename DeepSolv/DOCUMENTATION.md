# 🛍️ Shopify Store Insights Fetcher - Complete Documentation

## 📋 Overview

A comprehensive Python FastAPI application that extracts detailed insights from Shopify stores through intelligent web scraping, without using the official Shopify API. The application provides RESTful APIs to analyze store data and includes AI-powered data structuring capabilities.

## ✨ Features

### Mandatory Features ✅
- **🏪 Complete Product Catalog**: Extracts all products using Shopify's JSON endpoints
- **⭐ Hero Products**: Identifies featured products on homepage
- **📜 Policy Extraction**: Privacy, return/refund, shipping policies
- **❓ FAQ Analysis**: Intelligent FAQ extraction with categorization
- **📱 Social Media Links**: Finds Instagram, Facebook, TikTok, Twitter handles
- **📞 Contact Information**: Extracts emails, phone numbers, addresses
- **ℹ️ Brand Context**: About us, brand story, company information
- **🔗 Important Links**: Order tracking, contact, blog, support links

### Bonus Features 🎉
- **🏆 Competitor Analysis**: Discovers and analyzes competitor stores
- **💾 Database Persistence**: MySQL storage for all extracted data
- **🤖 AI-Powered Structuring**: Uses OpenAI to clean and organize data

## 🏗️ Architecture

```
📦 shopify-insights-fetcher/
├── 📄 main.py                    # FastAPI application entry point
├── 📁 app/
│   ├── 📁 models/               # Pydantic data models
│   │   ├── request_models.py    # Request schemas
│   │   └── response_models.py   # Response schemas
│   ├── 📁 services/             # Business logic
│   │   ├── store_analyzer.py    # Main store analysis service
│   │   ├── competitor_analyzer.py # Competitor discovery & analysis
│   │   ├── web_scraper.py       # Advanced web scraping utilities
│   │   └── ai_service.py        # AI/LLM integration
│   ├── 📁 database/             # Database layer
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   └── database.py          # Database operations
│   ├── 📁 utils/                # Utility functions
│   │   └── helpers.py           # Common helper functions
│   └── 📄 config.py             # Configuration management
├── 📁 tests/                    # Test suite
├── 📄 requirements.txt          # Python dependencies
├── 📄 demo.py                   # Demo script for testing
└── 📄 .env.example              # Environment configuration template
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd shopify-insights-fetcher

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/shopify_insights
# OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Database Setup (Optional)

```sql
-- Create MySQL database
CREATE DATABASE shopify_insights CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user and grant permissions
CREATE USER 'shopify_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON shopify_insights.* TO 'shopify_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Run the Application

```bash
# Start the server
python -m uvicorn main:app --reload

# Or use the VS Code task: "Run Shopify Insights API"
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### Core Endpoints

#### 🏪 Analyze Store
```http
POST /analyze-store
Content-Type: application/json

{
    "website_url": "https://memy.co.in"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "brand_name": "Memy",
        "website_url": "https://memy.co.in",
        "product_count": 45,
        "product_catalog": [...],
        "hero_products": [...],
        "policies": [...],
        "faqs": [...],
        "social_handles": [...],
        "contact_info": {...},
        "important_links": [...],
        "brand_context": "...",
        "analysis_duration": 12.5,
        "pages_analyzed": 8
    },
    "timestamp": "2025-01-16T10:30:00Z"
}
```

#### 🏆 Analyze Competitors (Bonus)
```http
POST /analyze-competitors
Content-Type: application/json

{
    "website_url": "https://memy.co.in",
    "max_competitors": 5
}
```

#### 🔍 Utility Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Swagger documentation
- `GET /redoc` - ReDoc documentation

## 🛠️ Usage Examples

### Python Client Example
```python
import requests

# Analyze a store
response = requests.post(
    "http://localhost:8000/analyze-store",
    json={"website_url": "https://memy.co.in"}
)

if response.status_code == 200:
    data = response.json()
    insights = data["data"]
    
    print(f"Brand: {insights['brand_name']}")
    print(f"Products: {insights['product_count']}")
    print(f"Social Handles: {len(insights['social_handles'])}")
```

### cURL Example
```bash
curl -X POST "http://localhost:8000/analyze-store" \
     -H "Content-Type: application/json" \
     -d '{"website_url": "https://memy.co.in"}'
```

### Demo Script
```bash
# Run the interactive demo
python demo.py
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_main.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Manual Testing
1. Start the server: `python -m uvicorn main:app --reload`
2. Run demo script: `python demo.py`
3. Use Swagger UI: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables
```bash
# Database (Optional)
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/shopify_insights

# AI Features (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
```

### Customization
- **Rate Limiting**: Adjust `REQUESTS_PER_MINUTE` in config
- **Timeout Settings**: Modify `REQUEST_TIMEOUT` for slow sites
- **Concurrent Requests**: Change `MAX_CONCURRENT_REQUESTS` based on your needs

## 📊 Data Models

### Store Insights Structure
```python
{
    "brand_name": "string",
    "website_url": "string", 
    "product_catalog": [
        {
            "id": "string",
            "title": "string",
            "price": float,
            "vendor": "string",
            "available": boolean,
            "images": ["string"],
            "url": "string"
        }
    ],
    "social_handles": [
        {
            "platform": "instagram|facebook|tiktok|twitter",
            "url": "string",
            "username": "string"
        }
    ],
    "contact_info": {
        "emails": ["string"],
        "phone_numbers": ["string"]
    },
    "faqs": [
        {
            "question": "string",
            "answer": "string",
            "category": "string"
        }
    ]
}
```

## 💾 Database Schema

### Core Tables
- **store_analyses**: Main store information
- **products**: Product catalog
- **hero_products**: Featured products
- **policies**: Store policies
- **faqs**: Frequently asked questions
- **social_handles**: Social media links
- **contact_info**: Contact information
- **important_links**: Navigation links
- **competitor_analyses**: Competitor relationships

## 🤖 AI Integration

### Features
- **FAQ Structuring**: Cleans and categorizes FAQ content
- **Brand Story Extraction**: Extracts key brand narrative
- **Competitor Relevance**: Scores competitor similarity

### Setup
1. Get OpenAI API key from https://platform.openai.com/
2. Set `OPENAI_API_KEY` in `.env` file
3. AI features will activate automatically

## 🚦 Error Handling

### HTTP Status Codes
- **200**: Success
- **401**: Website not found or inaccessible
- **422**: Invalid URL or request format
- **500**: Internal server error

### Error Response Format
```json
{
    "success": false,
    "error": "Description of the error",
    "status_code": 500,
    "timestamp": "2025-01-16T10:30:00Z"
}
```

## 🔍 Supported Store Examples

### Test Stores
- https://memy.co.in (Indian beauty brand)
- https://colourpop.com (US cosmetics)
- https://gymshark.com (UK fitness apparel)
- https://allbirds.com (Sustainable footwear)
- https://warbyparker.com (Eyewear)

### Store Requirements
- Must be a Shopify store
- Publicly accessible
- Not blocked by robots.txt
- Responds to `/products.json` endpoint

## 📈 Performance

### Typical Analysis Times
- **Small store** (< 50 products): 5-15 seconds
- **Medium store** (50-200 products): 15-30 seconds  
- **Large store** (200+ products): 30-60 seconds
- **Competitor analysis**: 2-5 minutes (depending on competitors found)

### Optimization Tips
- Use database caching for repeated analyses
- Adjust concurrent request limits based on server capacity
- Enable AI features selectively for production use

## 🛡️ Security & Ethics

### Respectful Scraping
- Checks robots.txt before scraping
- Implements request rate limiting
- Uses appropriate user agent headers
- Includes delays between requests

### Data Privacy
- No personal customer data is extracted
- Only public business information is collected
- Complies with website terms of service
- Database storage is optional

## 🐛 Troubleshooting

### Common Issues

**"Website not accessible" (401 error)**
- Check if URL is correct and publicly accessible
- Verify site is actually a Shopify store
- Some sites may block automated requests

**"Request timeout" errors**
- Increase `REQUEST_TIMEOUT` in config
- Check internet connection stability
- Some large stores take longer to analyze

**Database connection errors**
- Verify MySQL is running and accessible
- Check DATABASE_URL format and credentials
- Database is optional - app works without it

**Import errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment
- Check Python version (3.8+ required)

## 📚 Development

### Adding New Extractors
1. Create new method in `StoreAnalyzerService`
2. Add corresponding data models
3. Update database schema if needed
4. Add tests for new functionality

### Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Implement changes with tests
4. Submit pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for the GenAI Developer Intern Assignment**

For questions or support, please create an issue in the repository.
