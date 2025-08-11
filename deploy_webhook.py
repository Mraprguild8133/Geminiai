#!/usr/bin/env python3
"""
Simple webhook deployment script that works with Replit deployments.
"""

import os
import sys
import asyncio
import logging
import requests
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def deploy_webhook():
    """Deploy webhook using Replit's deployment URL."""
    
    # Get the deployment URL
    deployment_url = input("Enter your deployment URL (e.g., https://your-app.replit.app): ").strip()
    
    if not deployment_url:
        print("❌ No URL provided")
        return False
    
    if not deployment_url.startswith('http'):
        deployment_url = f"https://{deployment_url}"
    
    # Test the health endpoint
    print(f"🧪 Testing {deployment_url}/health...")
    
    try:
        response = requests.get(f"{deployment_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed!")
        else:
            print(f"⚠️ Health check returned {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("The app might not be accessible yet. Continue anyway? (y/N): ", end="")
        if input().lower() != 'y':
            return False
    
    # Set the webhook
    webhook_url = f"{deployment_url}/webhook"
    print(f"📡 Setting webhook to: {webhook_url}")
    
    bot_token = Config.TELEGRAM_BOT_TOKEN
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
            print("✅ Webhook set successfully!")
            print(f"📍 Your bot is now live at: {webhook_url}")
            print("🤖 Send a message to your bot to test it!")
            
            # Save the webhook URL
            with open('.env.webhook', 'w') as f:
                f.write(f"WEBHOOK_URL={webhook_url}\n")
                f.write(f"DEPLOYMENT_URL={deployment_url}\n")
            
            return True
        else:
            print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Webhook Deployment Setup")
    print("=" * 30)
    print()
    print("This script will help you set up your webhook after deployment.")
    print("Make sure you have already deployed your app and have the public URL.")
    print()
    
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        sys.exit(1)
    
    asyncio.run(deploy_webhook())

if __name__ == "__main__":
    main()