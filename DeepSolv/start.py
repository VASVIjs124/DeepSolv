#!/usr/bin/env python3
"""
Interactive startup script for Shopify Store Insights Fetcher application
"""

import subprocess
import sys
import os
import requests
import json
import time
from pathlib import Path
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_user_website_url():
    """Get website URL from user input with validation"""
    print("=" * 60)
    print("🌟 SHOPIFY STORE INSIGHTS FETCHER")
    print("=" * 60)
    print()
    print("📝 Enter a Shopify store URL to analyze, or press Enter to start server only:")
    print()
    print("Examples:")
    print("  • https://allbirds.com")
    print("  • https://warbyparker.com") 
    print("  • https://gymshark.com")
    print("  • https://beardbrand.com")
    print()
    
    while True:
        user_input = input("🔗 Website URL (or Enter to skip): ").strip()
        
        if not user_input:
            return None
            
        # Add https:// if not present
        if not user_input.startswith(('http://', 'https://')):
            user_input = 'https://' + user_input
            
        if is_valid_url(user_input):
            return user_input
        else:
            print("❌ Invalid URL format. Please try again.")
            print("   Example: https://example.com")

def analyze_website(url: str):
    """Send analysis request to the running application"""
    try:
        print(f"\n� Analyzing {url}...")
        print("⏳ This may take a few moments...")
        
        # Wait for server to be ready
        time.sleep(2)
        
        # Check if server is running
        try:
            health_response = requests.get("http://localhost:8002/api/v1/health", timeout=5)
            if health_response.status_code != 200:
                print("❌ Server not ready yet. Please try the analysis manually.")
                return
        except requests.exceptions.RequestException:
            print("❌ Server not ready yet. Please try the analysis manually.")
            return
        
        # Send analysis request
        analysis_data = {
            "website_url": url,
            "analysis_depth": "comprehensive",
            "force_refresh": True
        }
        
        response = requests.post(
            "http://localhost:8002/api/v1/analyze",
            json=analysis_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis complete for {url}")
            print(f"📊 Brand: {result.get('brand_data', {}).get('brand_name', 'Unknown')}")
            print(f"🛍️  Products found: {len(result.get('brand_data', {}).get('products', []))}")
            print(f"📄 Pages analyzed: {result.get('brand_data', {}).get('pages_analyzed', 0)}")
            print(f"💾 Data saved to database")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}...")
                
    except requests.exceptions.Timeout:
        print("⏰ Analysis request timed out. The process may still be running in the background.")
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")

def main():
    """Start the application with interactive features"""
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Get website URL from user (optional)
    website_url = None
    if "--no-input" not in sys.argv:
        website_url = get_user_website_url()
    
    # Check if virtual environment should be activated
    if "--venv" in sys.argv:
        print("\n📦 Note: Make sure you have activated your virtual environment")
        print("Example: source venv/bin/activate  # On Linux/Mac")
        print("Example: venv\\Scripts\\activate     # On Windows")
        print("")
    
    print("\n🚀 Starting Shopify Store Insights Fetcher...")
    
    # Start the application
    try:
        print("🌟 Application starting on http://0.0.0.0:8002")
        print("📚 API Documentation: http://localhost:8002/docs")
        print("🔍 Health Check: http://localhost:8002/api/v1/health")
        if website_url:
            print(f"🔍 Will analyze: {website_url} once server is ready")
        print("")
        print("Press Ctrl+C to stop the application")
        print("=" * 50)
        
        # Start uvicorn with the main application in the background if we have a URL to analyze
        if website_url:
            print("🚀 Starting server in background for analysis...")
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", "8002"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Give server time to start
            time.sleep(5)
            
            # Run analysis
            analyze_website(website_url)
            
            print("\n" + "=" * 50)
            print("🎯 Analysis complete! Server is still running.")
            print("📚 View results: http://localhost:8002/api/v1/brands")
            print("💻 Interactive docs: http://localhost:8002/docs")
            print("Press Ctrl+C to stop the server")
            print("=" * 50)
            
            # Wait for user to stop
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                process.wait()
        else:
            # Start server normally with reload for development
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", "8002", 
                "--reload"
            ])
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except FileNotFoundError:
        print("❌ Error: uvicorn not found. Please install requirements:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
