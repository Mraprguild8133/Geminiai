# Webhook Setup Guide

Your Telegram bot now has complete webhook support with automatic setup capabilities. Here's how to use it:

## Current Status

✅ **Polling Mode**: Currently running and working perfectly  
✅ **Webhook Mode**: Ready for deployment with automatic setup  
✅ **All Features**: AI conversations, image analysis, image generation  

## Quick Webhook Deployment

### Option 1: Deploy on Replit (Recommended)

1. **Click the Deploy button** in your Replit interface
2. **Get your deployment URL** (will be something like `https://your-app.replit.app`)
3. **Run the webhook setup script**:
   ```bash
   python deploy_webhook.py
   ```
4. **Enter your deployment URL** when prompted
5. **Done!** Your bot will automatically switch to webhook mode

### Option 2: Automatic Setup (After Deployment)

If you deploy your app, the webhook will try to set itself up automatically:

```bash
# Start webhook mode (after deployment)
python webhook_bot.py
```

The system will:
- Detect your public URL automatically
- Test the endpoint accessibility  
- Configure the webhook with Telegram
- Start receiving messages via webhook

## Manual Webhook Setup

If you prefer manual control:

```bash
# Check current webhook status
python webhook_setup.py info

# Set webhook manually
python webhook_setup.py set https://your-domain.com/webhook

# Delete webhook (switch back to polling)
python webhook_setup.py delete

# Test webhook endpoint
python webhook_setup.py test
```

## Switching Between Modes

### Currently Running: Polling Mode
Your bot is actively working in polling mode at @Multibotassitbot

### To Switch to Webhook Mode:
1. Deploy your app to get a public URL
2. Run `python deploy_webhook.py`
3. Enter your deployment URL
4. Your bot will instantly switch to webhook mode

### To Switch Back to Polling:
```bash
python webhook_setup.py delete
python polling_bot.py
```

## Docker Deployment

### Polling Mode (Current):
```bash
./docker-run.sh polling
```

### Webhook Mode:
```bash
./docker-run.sh webhook
```

After deployment, set the webhook:
```bash
python deploy_webhook.py
```

## Features Working in Both Modes

- ✅ AI-powered conversations with Google Gemini
- ✅ Image analysis and description
- ✅ AI image generation  
- ✅ Group chat support with mention detection
- ✅ Rate limiting and security
- ✅ Health monitoring
- ✅ Error handling and logging

## Webhook Advantages

- **Lower latency**: Messages arrive instantly
- **Better performance**: No constant polling
- **Scalable**: Handles high message volumes efficiently
- **Resource efficient**: Uses fewer server resources

## Troubleshooting

### Webhook Setup Failed
```bash
# Check if your app is accessible
curl https://your-app-url.com/health

# Try manual setup
python webhook_setup.py set https://your-app-url.com/webhook
```

### Bot Not Responding in Webhook Mode
```bash
# Check webhook status
python webhook_setup.py info

# Test webhook endpoint
python webhook_setup.py test

# Switch back to polling if needed
python webhook_setup.py delete
```

### URL Not Accessible
- Make sure your app is deployed and running
- Check that port 5000 is accessible
- Verify HTTPS is working (required for webhooks)

## Next Steps

1. **Deploy your app** to get a public URL
2. **Run `python deploy_webhook.py`** to set up webhook
3. **Test your bot** by sending messages
4. **Monitor performance** using the health endpoint

Your bot will work exactly the same in webhook mode as it does now in polling mode, but with better performance and scalability!