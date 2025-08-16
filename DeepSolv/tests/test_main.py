import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from main import app
from app.services.store_analyzer import StoreAnalyzerService
from app.models.response_models import BrandInsights


class TestStoreAnalyzer:
    """Test cases for store analyzer service"""
    
    def test_normalize_url(self):
        """Test URL normalization"""
        analyzer = StoreAnalyzerService()
        
        # Test with http
        result = analyzer._normalize_url("http://example.com")
        assert result == "http://example.com"
        
        # Test without protocol
        result = analyzer._normalize_url("example.com")
        assert result == "https://example.com"
        
        # Test with path
        result = analyzer._normalize_url("https://example.com/path")
        assert result == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_analyze_store_invalid_url(self):
        """Test store analysis with invalid URL"""
        analyzer = StoreAnalyzerService()
        
        with pytest.raises(ValueError):
            await analyzer.analyze_store("invalid-url")
    
    def test_extract_brand_name(self):
        """Test brand name extraction"""
        analyzer = StoreAnalyzerService()
        
        # Mock BeautifulSoup object
        mock_soup = Mock()
        meta_data = {"title": "Brand Name | Online Store"}
        
        result = analyzer._extract_brand_name(mock_soup, meta_data)
        assert result == "Online Store"
    
    def test_parse_product_data(self):
        """Test product data parsing"""
        analyzer = StoreAnalyzerService()
        
        product_data = {
            "id": "123",
            "title": "Test Product",
            "handle": "test-product",
            "vendor": "Test Vendor",
            "variants": [{"price": "19.99"}],
            "images": ["https://example.com/image.jpg"],
            "tags": ["tag1", "tag2"]
        }
        
        result = analyzer._parse_product_data(product_data, "https://example.com")
        
        assert result.id == "123"
        assert result.title == "Test Product"
        assert result.price == 19.99


class TestAPI:
    """Test cases for API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "Shopify Store Insights Fetcher API" in response.json()["message"]
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_analyze_store_invalid_url(self):
        """Test analyze store with invalid URL"""
        response = self.client.post(
            "/analyze-store",
            json={"website_url": "invalid-url"}
        )
        assert response.status_code == 422
    
    @patch('app.services.store_analyzer.StoreAnalyzerService.analyze_store')
    def test_analyze_store_success(self, mock_analyze):
        """Test successful store analysis"""
        # Mock the service response
        mock_insights = BrandInsights(
            website_url="https://example.com",
            brand_name="Test Store",
            product_count=10
        )
        mock_analyze.return_value = mock_insights
        
        response = self.client.post(
            "/analyze-store",
            json={"website_url": "https://example.com"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["data"]["brand_name"] == "Test Store"


class TestUtilities:
    """Test utility functions"""
    
    def test_validate_url(self):
        """Test URL validation"""
        from app.utils.helpers import validate_url
        
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("invalid-url") is False
        assert validate_url("") is False
    
    def test_extract_price_from_text(self):
        """Test price extraction"""
        from app.utils.helpers import extract_price_from_text
        
        assert extract_price_from_text("Price: $19.99") == 19.99
        assert extract_price_from_text("₹1,999") == 1999.0
        assert extract_price_from_text("No price here") is None
    
    def test_categorize_faq_question(self):
        """Test FAQ categorization"""
        from app.utils.helpers import categorize_faq_question
        
        assert categorize_faq_question("Do you offer free shipping?") == "shipping"
        assert categorize_faq_question("What payment methods do you accept?") == "payment"
        assert categorize_faq_question("What is your return policy?") == "returns"


if __name__ == "__main__":
    pytest.main([__file__])
