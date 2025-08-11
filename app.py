"""
Flask application for webhook handling and bot management.
"""

import logging
import os
from flask import Flask, request, jsonify
from telegram import Update
import asyncio
from functools import wraps

from telegram_bot import TelegramBot
from gemini_service import GeminiService
from config import Config

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Validate configuration
    if not Config.validate():
        logger.error("Invalid configuration. Please check environment variables.")
        raise ValueError("Configuration validation failed")
    
    # Initialize services
    gemini_service = GeminiService(Config.GEMINI_API_KEY)
    telegram_bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN, gemini_service)
    
    # Store bot instance for webhook handling
    app.telegram_bot = telegram_bot
    
    def async_route(f):
        """Decorator to handle async functions in Flask routes."""
        @wraps(f)
        def wrapper(*args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(f(*args, **kwargs))
            finally:
                loop.close()
        return wrapper
    
    @app.route('/')
    def home():
        """Health check endpoint."""
        try:
            bot_info = Config.get_bot_info()
            gemini_health = gemini_service.health_check()
            
            return jsonify({
                'status': 'healthy',
                'service': 'Telegram Bot with AI',
                'version': '1.0.0',
                'bot_configured': bot_info['has_telegram_token'],
                'ai_configured': bot_info['has_gemini_key'],
                'gemini_status': gemini_health['status'],
                'features': [
                    'AI Conversations',
                    'Image Analysis',
                    'Image Generation',
                    'Group Chat Support'
                ]
            })
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/health')
    def health():
        """Detailed health check endpoint."""
        try:
            bot_info = Config.get_bot_info()
            gemini_health = gemini_service.health_check()
            bot_stats = telegram_bot.stats.to_dict()
            
            return jsonify({
                'timestamp': str(datetime.now()),
                'bot': {
                    'status': 'running',
                    'configuration': bot_info,
                    'statistics': bot_stats
                },
                'gemini': gemini_health,
                'system': {
                    'webhook_configured': bool(Config.WEBHOOK_URL),
                    'rate_limiting': True,
                    'conversation_history': True
                }
            })
        except Exception as e:
            logger.error(f"Detailed health check error: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/webhook', methods=['POST'])
    @async_route
    async def webhook():
        """Handle incoming Telegram webhook updates."""
        try:
            # Get update data
            update_data = request.get_json()
            
            if not update_data:
                logger.warning("Received empty webhook data")
                return jsonify({'status': 'error', 'message': 'No data received'}), 400
            
            logger.info(f"Received webhook update: {update_data.get('update_id', 'unknown')}")
            
            # Initialize application if not already done
            if not telegram_bot.application.running:
                await telegram_bot.application.initialize()
                await telegram_bot.application.start()
            
            # Create Telegram Update object
            update = Update.de_json(update_data, telegram_bot.application.bot)
            
            if not update:
                logger.warning("Failed to parse update data")
                return jsonify({'status': 'error', 'message': 'Invalid update data'}), 400
            
            # Process the update
            await telegram_bot.application.process_update(update)
            
            return jsonify({'status': 'ok'})
            
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Internal server error'
            }), 500
    
    @app.route('/set_webhook', methods=['POST'])
    @async_route
    async def set_webhook():
        """Set webhook URL for the bot."""
        try:
            data = request.get_json() or {}
            webhook_url = data.get('webhook_url')
            
            if not webhook_url:
                return jsonify({
                    'status': 'error',
                    'message': 'webhook_url is required'
                }), 400
            
            # Actually set the webhook with Telegram
            bot = telegram_bot.application.bot
            webhook_info = await bot.set_webhook(
                url=webhook_url,
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=False
            )
            
            if webhook_info:
                logger.info(f"Webhook successfully set to: {webhook_url}")
                return jsonify({
                    'status': 'success',
                    'message': f'Webhook set to {webhook_url}',
                    'webhook_url': webhook_url
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to set webhook'
                }), 500
            
        except Exception as e:
            logger.error(f"Set webhook error: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/bot_info')
    def bot_info():
        """Get bot information and statistics."""
        try:
            bot_info = Config.get_bot_info()
            bot_stats = telegram_bot.stats.to_dict()
            
            return jsonify({
                'configuration': bot_info,
                'statistics': bot_stats,
                'active_conversations': len(telegram_bot.conversations),
                'commands': [
                    {'command': '/start', 'description': 'Welcome message'},
                    {'command': '/help', 'description': 'Show help'},
                    {'command': '/image', 'description': 'Generate AI image'},
                    {'command': '/clear', 'description': 'Clear conversation'},
                    {'command': '/health', 'description': 'Bot health check'}
                ]
            })
            
        except Exception as e:
            logger.error(f"Bot info error: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    
    logger.info("Flask application created successfully")
    return app

# Import datetime at module level
from datetime import datetime
