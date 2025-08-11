#!/usr/bin/env python3
"""
Telegram bot runner specifically for webhook mode with automatic setup.
"""

import logging
import os
import asyncio
import threading
import time
from app import create_app
from config import Config
from auto_webhook import AutoWebhookSetup

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def setup_webhook_after_startup():
    """Set up webhook after Flask server starts."""
    # Wait for Flask server to be ready
    await asyncio.sleep(3)
    
    logger.info("Setting up webhook automatically...")
    setup = AutoWebhookSetup()
    success = await setup.auto_setup()
    
    if success:
        logger.info("✅ Webhook configured successfully!")
    else:
        logger.warning("⚠️ Webhook setup failed, but server is still running")

def main():
    """Main entry point for webhook mode."""
    try:
        logger.info("Starting Telegram Bot in webhook mode...")
        
        # Create Flask app
        app = create_app()
        
        # Start webhook setup in background after server starts
        def setup_webhook_background():
            time.sleep(3)  # Wait for server to start
            asyncio.run(setup_webhook_after_startup())
        
        # Only set up webhook if not already configured
        current_webhook = os.getenv('WEBHOOK_URL')
        if not current_webhook:
            webhook_thread = threading.Thread(target=setup_webhook_background, daemon=True)
            webhook_thread.start()
        else:
            logger.info(f"Using existing webhook URL: {current_webhook}")
        
        # Run the webhook server
        logger.info("Starting Flask server on 0.0.0.0:5000")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running webhook bot: {e}")
        raise

if __name__ == '__main__':
    main()