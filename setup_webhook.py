#!/usr/bin/env python3
"""
Script to set up Telegram webhook for the bot.
"""

import os
import requests
import sys

def setup_webhook():
    """Set up the Telegram webhook."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in environment variables")
        sys.exit(1)
    
    # Get Replit URL - try different environment variables
    webhook_url = None
    possible_domains = [
        os.getenv('REPL_SLUG'),
        os.getenv('REPLIT_SLUG'),
        os.getenv('REPL_ID')
    ]
    
    replit_user = os.getenv('REPL_OWNER') or os.getenv('REPLIT_USER')
    
    if replit_user and possible_domains[0]:
        webhook_url = f"https://{possible_domains[0]}.{replit_user}.repl.co/webhook"
    else:
        # Use the public domain format
        webhook_url = "https://your-repl-domain.replit.app/webhook"
    
    print(f"Setting webhook URL to: {webhook_url}")
    
    # Set the webhook
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    data = {
        'url': webhook_url,
        'allowed_updates': ['message', 'callback_query']
    }
    
    try:
        response = requests.post(telegram_api_url, data=data)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook set successfully!")
            print(f"Webhook URL: {webhook_url}")
            return True
        else:
            print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def get_webhook_info():
    """Get current webhook information."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found")
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url)
        result = response.json()
        
        if result.get('ok'):
            webhook_info = result['result']
            print("📋 Current Webhook Information:")
            print(f"URL: {webhook_info.get('url', 'Not set')}")
            print(f"Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
            print(f"Pending update count: {webhook_info.get('pending_update_count', 0)}")
            
            if webhook_info.get('last_error_date'):
                print(f"Last error: {webhook_info.get('last_error_message', 'Unknown')}")
                print(f"Last error date: {webhook_info.get('last_error_date')}")
        else:
            print(f"Failed to get webhook info: {result}")
            
    except Exception as e:
        print(f"Error getting webhook info: {e}")

def delete_webhook():
    """Delete the current webhook."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found")
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        response = requests.post(url)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook deleted successfully!")
        else:
            print(f"❌ Failed to delete webhook: {result}")
            
    except Exception as e:
        print(f"Error deleting webhook: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "set":
            setup_webhook()
        elif command == "info":
            get_webhook_info()
        elif command == "delete":
            delete_webhook()
        else:
            print("Usage: python setup_webhook.py [set|info|delete]")
    else:
        print("Current webhook information:")
        get_webhook_info()
        print("\nTo set up webhook, run: python setup_webhook.py set")