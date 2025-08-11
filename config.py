"""
Configuration settings for the Telegram bot.
"""

import os
from typing import Optional

class Config:
    """Configuration class for the Telegram bot."""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_BOT_USERNAME: Optional[str] = os.getenv('TELEGRAM_BOT_USERNAME')
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    
    # Webhook Configuration
    WEBHOOK_URL: str = os.getenv('WEBHOOK_URL', '')
    WEBHOOK_PATH: str = '/webhook'
    
    # Bot Settings
    MAX_CONVERSATION_HISTORY: int = 20
    MAX_MESSAGE_LENGTH: int = 4096
    MAX_IMAGE_SIZE: int = 20 * 1024 * 1024  # 20MB
    
    # Rate Limiting
    RATE_LIMIT_MESSAGES: int = 10
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'GEMINI_API_KEY'
        ]
        
        for var in required_vars:
            if not getattr(cls, var):
                return False
        return True
    
    @classmethod
    def get_bot_info(cls) -> dict:
        """Get bot configuration info for health checks."""
        return {
            'has_telegram_token': bool(cls.TELEGRAM_BOT_TOKEN),
            'has_gemini_key': bool(cls.GEMINI_API_KEY),
            'has_webhook_url': bool(cls.WEBHOOK_URL),
            'bot_username': cls.TELEGRAM_BOT_USERNAME,
            'max_history': cls.MAX_CONVERSATION_HISTORY
        }
