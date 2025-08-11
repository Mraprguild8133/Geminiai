#!/usr/bin/env python3
"""
Automatic webhook setup for Telegram bot.
Detects public URL and configures webhook automatically.
"""

import os
import sys
import time
import logging
import asyncio
import requests
from urllib.parse import urlparse
from config import Config

logger = logging.getLogger(__name__)

class AutoWebhookSetup:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.base_urls = []
        
    def detect_public_urls(self):
        """Detect possible public URLs for this environment."""
        urls = []
        
        # Replit detection
        repl_id = os.getenv('REPL_ID')
        repl_slug = os.getenv('REPL_SLUG')
        repl_owner = os.getenv('REPL_OWNER')
        
        if repl_slug and repl_owner:
            urls.append(f"https://{repl_slug}.{repl_owner}.repl.co")
        
        if repl_id:
            urls.append(f"https://{repl_id}.replit.app")
            
        # Check for custom domain in environment
        custom_domain = os.getenv('CUSTOM_DOMAIN')
        if custom_domain:
            if not custom_domain.startswith('http'):
                custom_domain = f"https://{custom_domain}"
            urls.append(custom_domain)
            
        # Check for webhook URL in config
        if Config.WEBHOOK_URL:
            parsed = urlparse(Config.WEBHOOK_URL)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            if base_url not in urls:
                urls.append(base_url)
        
        self.base_urls = urls
        return urls
    
    def test_url_accessibility(self, url, timeout=10):
        """Test if URL is accessible from outside."""
        try:
            test_url = f"{url}/health"
            response = requests.get(test_url, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    logger.info(f"URL {url} is accessible and healthy")
                    return True
            
            logger.warning(f"URL {url} responded with status {response.status_code}")
            return False
            
        except Exception as e:
            logger.warning(f"URL {url} is not accessible: {e}")
            return False
    
    async def set_webhook_url(self, webhook_url):
        """Set webhook URL with Telegram."""
        api_url = f"https://api.telegram.org/bot{self.bot_token}/setWebhook"
        
        data = {
            'url': webhook_url,
            'allowed_updates': ['message', 'callback_query', 'inline_query'],
            'drop_pending_updates': False,
            'max_connections': 100
        }
        
        try:
            response = requests.post(api_url, data=data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Webhook set successfully to: {webhook_url}")
                return True
            else:
                logger.error(f"Failed to set webhook: {result.get('description', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    async def auto_setup(self, retry_count=3, wait_time=5):
        """Automatically detect and set up webhook."""
        logger.info("Starting automatic webhook setup...")
        
        # Detect possible URLs
        urls = self.detect_public_urls()
        
        if not urls:
            logger.error("No public URLs detected. Cannot set up webhook automatically.")
            return False
        
        logger.info(f"Detected possible URLs: {urls}")
        
        # Wait a bit for server to be ready
        logger.info(f"Waiting {wait_time} seconds for server to be ready...")
        await asyncio.sleep(wait_time)
        
        # Test each URL
        working_url = None
        for url in urls:
            logger.info(f"Testing URL: {url}")
            
            for attempt in range(retry_count):
                if self.test_url_accessibility(url):
                    working_url = url
                    break
                
                if attempt < retry_count - 1:
                    logger.info(f"Retry {attempt + 1}/{retry_count} for {url}")
                    await asyncio.sleep(2)
            
            if working_url:
                break
        
        if not working_url:
            logger.error("No accessible URLs found. Webhook setup failed.")
            return False
        
        # Set up webhook
        webhook_url = f"{working_url}/webhook"
        logger.info(f"Setting webhook to: {webhook_url}")
        
        success = await self.set_webhook_url(webhook_url)
        
        if success:
            logger.info("Automatic webhook setup completed successfully!")
            
            # Update environment variable for future use
            os.environ['WEBHOOK_URL'] = webhook_url
            
            return True
        else:
            logger.error("Webhook setup failed.")
            return False

async def main():
    """Main function for standalone execution."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is required")
        sys.exit(1)
    
    setup = AutoWebhookSetup()
    success = await setup.auto_setup()
    
    if success:
        print("✅ Webhook setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Webhook setup failed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())