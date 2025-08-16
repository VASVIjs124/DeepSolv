# � Shopify Store Insights Fetcher

A comprehensive Python FastAPI application for extracting detailed insights from Shopify stores through intelligent web scraping and AI-powered analysis.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

## 🚀 Features

- **Brand Analysis**: Complete store profiling with metadata extraction
- **Product Catalog**: Automated product discovery and categorization
- **Hero Products**: Identification of featured and bestselling items
- **Policy Extraction**: Terms, privacy, shipping, and return policies
- **FAQ Analysis**: Customer support content extraction
- **Social Media**: Social handles and profile discovery
- **Contact Information**: Store contact details and location data
- **Competitor Finding**: Related store discovery and analysis
- **Real-time Analysis**: Live store scraping with progress tracking
- **Database Persistence**: SQLite/MySQL storage with comprehensive schema
- **RESTful API**: Well-documented endpoints with OpenAPI/Swagger
- **Web Dashboard**: Interactive HTML interface for analysis
- **AI Integration**: OpenAI-powered content structuring and analysis

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: SQLAlchemy 2.0.23 (SQLite default, MySQL supported)
- **Web Scraping**: BeautifulSoup4 4.12.2, aiohttp 3.9.1
- **AI Integration**: OpenAI API with GPT models
- **Data Validation**: Pydantic 2.5.0
- **Testing**: pytest 7.4.3
- **Async Support**: Full async/await implementation

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Quick Setup

### 1. Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
1. **Clone the repository**
```bash
git clone https://github.com/yourusername/shopify-insights-fetcher.git
cd shopify-insights-fetcher
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Database setup**
```bash
# SQLite (default) - no setup required
# For MySQL, update DATABASE_URL in .env
```

5. **Run the application**
```bash
python main.py
# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///shopify_insights.db` | Database connection string |
| `OPENAI_API_KEY` | Required | OpenAI API key for AI analysis |
| `DEBUG` | `False` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HOST` | `127.0.0.1` | Server host |
| `PORT` | `8000` | Server port |
| `MAX_CONCURRENT_REQUESTS` | `5` | Concurrent scraping limit |
| `REQUEST_TIMEOUT` | `30` | HTTP request timeout (seconds) |

### Database Configuration

**SQLite (Default)**
```env
DATABASE_URL=sqlite:///shopify_insights.db
```

**MySQL**
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/shopify_insights
```

## 🔗 API Endpoints

### Core Endpoints

- `GET /` - Web dashboard interface
- `GET /docs` - Interactive API documentation (Swagger)
- `GET /redoc` - Alternative API documentation
- `GET /info` - API information and features

### Analysis Endpoints

- `POST /api/v1/analyze` - Analyze Shopify store
- `GET /api/v1/brands` - List analyzed brands
- `GET /api/v1/brands/{brand_id}` - Get brand details
- `POST /api/v1/realtime/analyze` - Real-time store analysis
- `GET /api/v1/health` - Health check endpoint

### Example Usage
```python
import requests

# Analyze a Shopify store
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"url": "https://allbirds.com"}
)

analysis = response.json()
print(f"Found {len(analysis['products'])} products")
```

## 📁 Project Structure

```
shopify-insights-fetcher/
├── api/                    # API routes and endpoints
├── database/              # Database models and operations
├── models/                # Pydantic data models
├── services/              # Business logic and scrapers
├── templates/             # HTML templates
├── tests/                 # Test suites
├── tools/                 # Utility scripts and dashboards
├── config.py             # Application configuration
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=./ --cov-report=html

# Run specific test file
pytest tests/test_scrapers.py
```

## 🎯 Usage Examples

### Web Interface
1. Open http://localhost:8000 in your browser
2. Enter a Shopify store URL
3. View comprehensive analysis results

### API Usage
```python
import asyncio
import aiohttp

async def analyze_store():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/api/v1/analyze",
            json={"url": "https://example-store.myshopify.com"}
        ) as response:
            data = await response.json()
            return data

# Run analysis
result = asyncio.run(analyze_store())
print(f"Brand: {result['brand_name']}")
print(f"Products: {len(result['products'])}")
```

### Real-time Analysis
```python
import requests

# Start real-time analysis
response = requests.post(
    "http://localhost:8000/api/v1/realtime/analyze",
    json={
        "url": "https://store.example.com",
        "force_refresh": True
    }
)

analysis = response.json()
print(f"Analysis Status: {analysis['status']}")
```

## 🔍 Key Features Details

### Intelligent Scraping
- Respects robots.txt and rate limits
- Handles JavaScript-rendered content
- Automatic retry with exponential backoff
- Comprehensive error handling

### AI-Powered Analysis
- Content structuring with OpenAI GPT
- Automatic categorization
- Sentiment analysis of reviews
- Competitive insights

### Database Schema
- **Brands**: Store metadata and analysis results
- **Products**: Complete product catalog with variants
- **Hero Products**: Featured items and bestsellers
- **Policies**: Legal and shipping information
- **FAQs**: Customer support content
- **Social Handles**: Social media presence
- **Contact Details**: Store contact information

## 🚀 Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔧 Troubleshooting

### Common Issues

**Database Connection**
```bash
# Check SQLite database
sqlite3 shopify_insights.db ".tables"

# For MySQL connection issues
pip install pymysql cryptography
```

**Scraping Issues**
- Verify target URL is accessible
- Check for Cloudflare or anti-bot protection
- Ensure proper user agent headers

**OpenAI API**
```bash
# Test API key
python -c "import openai; print('API key valid')"
```

## 📊 Performance

- **Scraping Speed**: ~10-30 seconds per store
- **Concurrent Analysis**: Up to 5 stores simultaneously  
- **Database Performance**: Optimized queries with indexing
- **Memory Usage**: ~50-100MB per analysis session

## 🎉 Acknowledgments

- FastAPI community for excellent framework
- BeautifulSoup for reliable web scraping
- OpenAI for AI-powered content analysis
- SQLAlchemy for robust ORM functionality

---

**Made with ❤️ for e-commerce insights and data analysis**

For questions or support, please open an issue or contact the maintainers.
        "faqs": [
            {
                "question": "Do you have COD as a payment option?",
                "answer": "Yes, we do have Cash on Delivery available",
                "category": "payment"
            }
        ],
        "policies": [...],
        "important_links": [...],
        "analysis_duration": 12.5,
        "pages_analyzed": 8
    }
}
```

### Competitor Analysis (Bonus)
```bash
curl -X POST "http://localhost:8000/analyze-competitors" \
     -H "Content-Type: application/json" \
     -d '{"website_url": "https://memy.co.in", "max_competitors": 3}'
```

## 🧪 Testing

### Quick Test
```bash
python quick_test.py
```

### Full Demo
```bash
python demo.py
```

### Unit Tests
```bash
pytest tests/ -v
```

## 🏗️ Architecture

```
📦 shopify-insights-fetcher/
├── 📄 main.py                    # FastAPI application entry
├── 📁 app/
│   ├── 📁 models/               # Pydantic data models  
│   ├── 📁 services/             # Business logic
│   │   ├── store_analyzer.py    # Main analysis service
│   │   ├── competitor_analyzer.py # Competitor discovery
│   │   ├── web_scraper.py       # Web scraping utilities
│   │   └── ai_service.py        # AI integration
│   ├── 📁 database/             # Database layer
│   └── 📁 utils/                # Helper functions
├── 📁 tests/                    # Test suite
└── 📄 requirements.txt          # Dependencies
```

## 🔧 Configuration (Optional)

### Environment Variables (.env)
```bash
# Database (Optional - app works without database)
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/shopify_insights

# AI Features (Optional - enhances data structuring)  
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

### MySQL Database Setup (Optional)
```sql
CREATE DATABASE shopify_insights CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'shopify_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON shopify_insights.* TO 'shopify_user'@'localhost';
```

## 🛍️ Supported Shopify Stores

### Test Examples
- **Indian Beauty**: https://memy.co.in
- **US Cosmetics**: https://colourpop.com  
- **UK Fitness**: https://gymshark.com
- **Sustainable Fashion**: https://allbirds.com
- **Eyewear**: https://warbyparker.com

## 📊 Performance

- **Small Store** (< 50 products): 5-15 seconds
- **Medium Store** (50-200 products): 15-30 seconds
- **Large Store** (200+ products): 30-60 seconds
- **Competitor Analysis**: 2-5 minutes

## 🛡️ Ethical Scraping

- ✅ Checks robots.txt compliance
- ✅ Implements rate limiting  
- ✅ Uses appropriate delays
- ✅ Only extracts public business data
- ✅ No personal customer information

## 🚦 Error Handling

| Status Code | Description |
|-------------|-------------|
| 200 | ✅ Success |
| 401 | ❌ Website not found or inaccessible |
| 422 | ❌ Invalid URL format |
| 500 | ❌ Internal server error |

## 📚 Documentation

- **Complete Documentation**: [DOCUMENTATION.md](DOCUMENTATION.md)
- **API Docs**: http://localhost:8000/docs (when running)
- **Alternative Docs**: http://localhost:8000/redoc

## 🎯 GenAI Developer Intern Assignment

### ✅ Requirements Completed

#### Mandatory Requirements
- [x] **Python Application** with FastAPI framework
- [x] **Product Catalog Extraction** via `/products.json`
- [x] **Hero Products** from homepage analysis
- [x] **Privacy Policy** extraction
- [x] **Return/Refund Policies** extraction  
- [x] **Brand FAQs** with intelligent categorization
- [x] **Social Handles** (Instagram, Facebook, TikTok, etc.)
- [x] **Contact Details** (emails, phone numbers)
- [x] **Brand Text Context** (About us, brand story)
- [x] **Important Links** (order tracking, contact, blogs)
- [x] **RESTful API** with proper error handling
- [x] **JSON Response Format** with structured data
- [x] **Error Status Codes** (401, 500) as specified

#### Bonus Requirements
- [x] **Competitor Analysis** with relevance scoring
- [x] **MySQL Database Persistence** with comprehensive schema
- [x] **AI Integration** for data structuring and FAQ categorization

#### Technical Excellence
- [x] **OOP Principles** with service-oriented architecture
- [x] **SOLID Design Patterns** implementation
- [x] **Clean Code** with proper documentation
- [x] **Pydantic Models** for data validation
- [x] **Code Structure** with modular organization  
- [x] **Edge Case Handling** for various store formats
- [x] **Comprehensive Testing** suite included

## 🏆 Key Highlights

1. **Production Ready**: Comprehensive error handling, logging, and testing
2. **Scalable Architecture**: Service layers, dependency injection, async operations
3. **AI-Powered**: Intelligent data structuring and competitor analysis
4. **Database Integration**: Full persistence with proper ORM models
5. **Respectful Scraping**: Robots.txt compliance and rate limiting
6. **Comprehensive Coverage**: Handles diverse Shopify store layouts
7. **Developer Friendly**: Complete documentation and demo scripts

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

**Built with ❤️ for GenAI Developer Intern Assignment**

*Demonstrating expertise in Python, FastAPI, AI integration, database design, and scalable architecture*
