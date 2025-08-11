#!/usr/bin/env python3
"""
Quick test for automatic webhook setup
"""

import asyncio
import logging
from auto_webhook import AutoWebhookSetup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_auto_setup():
    """Test the automatic webhook setup."""
    logger.info("Testing automatic webhook setup...")
    
    setup = AutoWebhookSetup()
    
    # Detect URLs
    urls = setup.detect_public_urls()
    print(f"Detected URLs: {urls}")
    
    if urls:
        # Test the first URL
        test_url = urls[0]
        print(f"Testing URL: {test_url}")
        
        # Wait a moment for server to be ready
        await asyncio.sleep(2)
        
        is_accessible = setup.test_url_accessibility(test_url)
        print(f"URL accessible: {is_accessible}")
        
        if is_accessible:
            webhook_url = f"{test_url}/webhook"
            print(f"Would set webhook to: {webhook_url}")
        else:
            print("URL not accessible yet - may need more time")
    else:
        print("No URLs detected")

if __name__ == "__main__":
    asyncio.run(test_auto_setup())