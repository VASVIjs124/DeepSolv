#!/usr/bin/env python3
"""
Simple test script to debug RealtimeStoreAnalyzer
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.realtime_analyzer import RealtimeStoreAnalyzer

async def test_analyzer():
    print("Creating RealtimeStoreAnalyzer...")
    analyzer = RealtimeStoreAnalyzer()
    
    print("Starting analysis...")
    try:
        result = await analyzer.analyze_and_store_shop("https://allbirds.com", save_to_db=False)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analyzer())
