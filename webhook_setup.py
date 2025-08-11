#!/usr/bin/env python3
"""
Advanced webhook setup script for Telegram bot.
"""

import os
import sys
import requests
import asyncio
from urllib.parse import urlparse
import json

def get_replit_url():
    """Get the Replit public URL."""
    # Try different methods to get the public URL
    repl_id = os.getenv('REPL_ID')
    repl_slug = os.getenv('REPL_SLUG') 
    repl_owner = os.getenv('REPL_OWNER')
    
    if repl_slug and repl_owner:
        # New Replit format
        return f"https://{repl_slug}.{repl_owner}.repl.co"
    elif repl_id:
        # Alternative format
        return f"https://{repl_id}.replit.app"
    else:
        return None

def check_url_accessibility(url):
    """Check if the URL is accessible from outside."""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def set_telegram_webhook(bot_token, webhook_url):
    """Set the webhook with Telegram."""
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
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
            print(f"✅ Webhook set successfully!")
            print(f"📍 URL: {webhook_url}")
            return True
        else:
            print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def get_webhook_info(bot_token):
    """Get current webhook information."""
    api_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(api_url, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            webhook_info = result['result']
            print("📋 Current Webhook Information:")
            print(f"URL: {webhook_info.get('url', 'Not set')}")
            print(f"Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
            print(f"Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"Max connections: {webhook_info.get('max_connections', 'Not set')}")
            print(f"Allowed updates: {', '.join(webhook_info.get('allowed_updates', []))}")
            
            if webhook_info.get('last_error_date'):
                print(f"⚠️ Last error: {webhook_info.get('last_error_message', 'Unknown')}")
                print(f"Last error date: {webhook_info.get('last_error_date')}")
            
            return webhook_info
        else:
            print(f"Failed to get webhook info: {result}")
            return None
            
    except Exception as e:
        print(f"Error getting webhook info: {e}")
        return None

def delete_webhook(bot_token):
    """Delete the current webhook."""
    api_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    
    try:
        response = requests.post(api_url, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook deleted successfully!")
            return True
        else:
            print(f"❌ Failed to delete webhook: {result}")
            return False
            
    except Exception as e:
        print(f"Error deleting webhook: {e}")
        return False

def test_webhook_endpoint(webhook_url):
    """Test if the webhook endpoint is working."""
    try:
        # Test with a mock update
        test_data = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "date": 1234567890,
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 123456, "is_bot": False, "first_name": "Test"},
                "text": "/test"
            }
        }
        
        response = requests.post(
            webhook_url,
            json=test_data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'ok':
                print("✅ Webhook endpoint is working!")
                return True
            else:
                print(f"⚠️ Webhook responded but with error: {result}")
                return False
        else:
            print(f"❌ Webhook endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def main():
    """Main function."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        sys.exit(1)
    
    command = sys.argv[1] if len(sys.argv) > 1 else 'info'
    
    if command == 'info':
        print("🔍 Getting current webhook information...")
        get_webhook_info(bot_token)
        
    elif command == 'delete':
        print("🗑️ Deleting webhook...")
        delete_webhook(bot_token)
        
    elif command == 'set':
        # Try to get webhook URL from command line or environment
        webhook_url = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not webhook_url:
            # Try to auto-detect Replit URL
            base_url = get_replit_url()
            if base_url:
                webhook_url = f"{base_url}/webhook"
                print(f"🔍 Auto-detected Replit URL: {base_url}")
            else:
                print("❌ Could not auto-detect URL. Please provide webhook URL:")
                print("Usage: python webhook_setup.py set https://your-domain.com/webhook")
                sys.exit(1)
        
        print(f"🌐 Testing URL accessibility: {webhook_url.replace('/webhook', '')}")
        
        # Test if URL is accessible
        base_url = webhook_url.replace('/webhook', '')
        if not check_url_accessibility(base_url):
            print("⚠️ Warning: URL may not be accessible from outside")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(1)
        
        # Test webhook endpoint
        print("🧪 Testing webhook endpoint...")
        if test_webhook_endpoint(webhook_url):
            print("✅ Webhook endpoint test passed!")
        else:
            print("⚠️ Webhook endpoint test failed - webhook may not work properly")
            response = input("Continue setting webhook anyway? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(1)
        
        # Set the webhook
        print("📡 Setting webhook with Telegram...")
        if set_telegram_webhook(bot_token, webhook_url):
            print("\n🎉 Webhook setup complete!")
            print("Your bot should now receive messages via webhook.")
            print("Send a message to your bot to test it.")
        else:
            print("\n❌ Webhook setup failed.")
            
    elif command == 'test':
        # Test current webhook
        webhook_info = get_webhook_info(bot_token)
        if webhook_info and webhook_info.get('url'):
            webhook_url = webhook_info['url']
            print(f"🧪 Testing webhook: {webhook_url}")
            test_webhook_endpoint(webhook_url)
        else:
            print("❌ No webhook URL configured")
            
    else:
        print("Usage: python webhook_setup.py [info|set|delete|test] [webhook_url]")
        print("")
        print("Commands:")
        print("  info    - Show current webhook information")
        print("  set     - Set webhook URL (auto-detects Replit URL if not provided)")
        print("  delete  - Delete current webhook")
        print("  test    - Test current webhook endpoint")
        print("")
        print("Examples:")
        print("  python webhook_setup.py info")
        print("  python webhook_setup.py set")
        print("  python webhook_setup.py set https://mybot.example.com/webhook")

if __name__ == "__main__":
    main()