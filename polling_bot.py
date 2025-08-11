#!/usr/bin/env python3
"""
Alternative Telegram bot runner using polling instead of webhooks.
This can be used when webhook setup is not possible.
"""

import logging
import os
import asyncio
from telegram.ext import Application
from telegram_bot import TelegramBot
from gemini_service import GeminiService
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot with polling."""
    try:
        # Validate required environment variables
        required_vars = ['TELEGRAM_BOT_TOKEN', 'GEMINI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return
        
        # Initialize services
        gemini_service = GeminiService(Config.GEMINI_API_KEY)
        telegram_bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN, gemini_service)
        
        logger.info("Starting Telegram Bot with polling...")
        logger.info(f"Bot username: @{Config.TELEGRAM_BOT_USERNAME or 'Unknown'}")
        
        # Start the bot with polling
        application = telegram_bot.application
        
        # Test the connection
        bot_info = await application.bot.get_me()
        logger.info(f"Bot connected successfully: {bot_info.first_name} (@{bot_info.username})")
        
        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=False  # Process pending messages
        )
        
        logger.info("Bot is now running and polling for updates...")
        logger.info("Press Ctrl+C to stop the bot")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise
    finally:
        if 'application' in locals():
            await application.stop()
            await application.shutdown()

if __name__ == '__main__':
    asyncio.run(main())