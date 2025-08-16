# 🚀 Enhanced Shopify Store Insights Fetcher - User Guide

## 🌟 New Interactive Features

The application now includes **two ways** to input website URLs for analysis:

### 1. 🖥️ **Web Interface** (Recommended)
Access the beautiful web interface at: **http://localhost:8002/**

**Features:**
- ✅ Clean, modern interface with gradient design
- ✅ Pre-filled examples of popular Shopify stores
- ✅ Real-time analysis with loading indicators
- ✅ Instant results display with success/error feedback
- ✅ Links to API documentation and all analyzed brands
- ✅ Responsive design that works on all devices

**Popular Stores to Try:**
- **Allbirds** - https://allbirds.com
- **Warby Parker** - https://warbyparker.com  
- **Gymshark** - https://gymshark.com
- **Beardbrand** - https://beardbrand.com

### 2. 📟 **Interactive Command Line**
Start the application with interactive prompts:

```bash
python start.py
```

**Features:**
- ✅ Prompts for website URL input at startup
- ✅ URL validation with helpful error messages
- ✅ Automatic analysis once server starts
- ✅ Background server management
- ✅ Real-time analysis progress

**Options:**
```bash
python start.py --no-input    # Skip input prompt, start server only
python start.py --venv        # Show virtual environment reminder
```

## 🎯 **How to Use**

### Method 1: Web Interface
1. **Start the server**: `python start.py --no-input`
2. **Open browser**: Navigate to http://localhost:8002/
3. **Enter URL**: Type or click an example Shopify store URL
4. **Click Analyze**: Watch the real-time analysis progress
5. **View Results**: See comprehensive brand insights instantly

### Method 2: Command Line
1. **Run the script**: `python start.py`
2. **Enter URL**: When prompted, enter a Shopify store URL
3. **Wait for analysis**: The system will start server and analyze automatically
4. **View results**: Results saved to database and displayed

## 📊 **Analysis Results**

Both methods provide:

**✅ Brand Information**
- Brand name and description
- Website URL and pages analyzed
- Analysis timestamp

**✅ Product Data**
- Complete product catalog
- Product variants and pricing
- Hero/featured products

**✅ Store Policies**
- Return and refund policies
- Shipping information
- Privacy policy

**✅ Social Media**
- Instagram, Twitter, Facebook handles
- Social media engagement data

**✅ Contact Information**
- Support email and phone
- Business hours and location

**✅ FAQ Section**
- Frequently asked questions
- Customer support information

## 🔗 **Quick Access Links**

| Feature | URL |
|---------|-----|
| **Web Interface** | http://localhost:8002/ |
| **API Documentation** | http://localhost:8002/docs |
| **Health Check** | http://localhost:8002/api/v1/health |
| **All Brands** | http://localhost:8002/api/v1/brands |
| **API Info** | http://localhost:8002/info |

## 🛠️ **Advanced Usage**

### API Endpoint Testing
```bash
# Analyze a store via API
curl -X POST "http://localhost:8002/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "website_url": "https://allbirds.com",
    "analysis_depth": "comprehensive",
    "force_refresh": false
  }'

# Get all analyzed brands
curl "http://localhost:8002/api/v1/brands"

# Get specific brand details  
curl "http://localhost:8002/api/v1/brands/1"
```

### Background Analysis
```bash
# Start server and analyze in background
python start.py
# Enter: https://gymshark.com
# Server runs analysis automatically
```

## 🎨 **Web Interface Features**

### **Visual Design**
- Modern gradient background (purple to blue)
- Clean white card layout with rounded corners
- Responsive design for mobile and desktop
- Smooth animations and hover effects

### **Interactive Elements**
- Click-to-fill example store URLs
- Real-time form validation
- Loading spinner during analysis
- Color-coded success/error messages
- Quick links to API documentation

### **User Experience**
- Single-click example selection
- Instant feedback on URL validation  
- Progress indicators during analysis
- Clear success/error messaging
- Easy navigation to results

## 💡 **Tips for Best Results**

1. **Use HTTPS URLs**: Always include https:// in your URLs
2. **Try Popular Stores**: Start with known Shopify stores for best results
3. **Check Results**: Visit /api/v1/brands to see all analyzed data
4. **Use Force Refresh**: Add `force_refresh: true` for latest data
5. **Monitor Health**: Check /api/v1/health for server status

## 🚀 **Ready to Analyze!**

Your Shopify Store Insights Fetcher now provides **multiple intuitive ways** to analyze stores:

- 🌐 **Beautiful web interface** for visual users
- 💻 **Command line interaction** for developers  
- 🔗 **Direct API access** for integrations

**Start exploring Shopify stores today!**
