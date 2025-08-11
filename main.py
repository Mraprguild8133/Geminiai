#!/usr/bin/env python3
"""
Main entry point for Telegram bot - supports both polling and webhook modes.
"""

import os
import sys
import logging
import asyncio
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    # Check command line arguments
    mode = os.getenv('BOT_MODE', 'auto')
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    
    # Validate configuration
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is required")
        sys.exit(1)
        
    if not Config.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is required")
        sys.exit(1)
    
    # Determine mode
    if mode == 'auto':
        # Auto-detect mode based on environment
        if Config.WEBHOOK_URL or os.getenv('REPLIT_DB_URL'):
            mode = 'webhook'
        else:
            mode = 'polling'
    
    logger.info(f"Starting bot in {mode} mode...")
    
    if mode == 'polling':
        # Import and run polling mode
        from polling_bot import main as polling_main
        polling_main()
        
    elif mode == 'webhook':
        # Import and run webhook mode
        from webhook_bot import main as webhook_main
        webhook_main()
        
    else:
        logger.error(f"Invalid mode: {mode}. Use 'polling' or 'webhook'")
        print("Usage: python main.py [polling|webhook]")
        sys.exit(1)

if __name__ == '__main__':
    main()