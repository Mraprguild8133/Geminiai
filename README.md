# AI-Powered Telegram Bot

A sophisticated Telegram bot with Google Gemini AI integration, featuring intelligent conversations, image analysis, and AI image generation capabilities. Built with Python and designed for both development and production deployment.

## 🤖 Live Bot

**@Multibotassitbot** - Try it now on Telegram!

## ✨ Features

- **AI Conversations**: Natural conversations powered by Google Gemini 2.5 Flash
- **Image Analysis**: Upload photos for detailed AI analysis using Gemini 2.5 Pro
- **AI Image Generation**: Create custom images from text descriptions
- **Smart Group Support**: Intelligent mention detection for group chats
- **Multi-Modal AI**: Text, image, and generation capabilities in one bot
- **Rate Limiting**: Built-in protection against spam and abuse
- **Health Monitoring**: Comprehensive logging and status endpoints

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- Google Gemini API Key (get from [Google AI Studio](https://aistudio.google.com/))

### Environment Setup

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd telegram-bot-ai
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Set environment variables**:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   export GEMINI_API_KEY="your_gemini_api_key_here"
   export TELEGRAM_BOT_USERNAME="your_bot_username"  # Optional
   ```

### Run the Bot

#### Polling Mode (Recommended for Development)
```bash
python polling_bot.py
```

#### Webhook Mode (Recommended for Production)
```bash
python webhook_bot.py
```

#### Auto-Detection Mode
```bash
python main.py
```

## 🐳 Docker Deployment

### Quick Docker Setup

1. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Run with Docker Compose**:
   ```bash
   # Polling mode
   ./docker-run.sh polling

   # Webhook mode  
   ./docker-run.sh webhook

   # Background mode
   ./docker-run.sh polling --detach
   ```

### Docker Commands

```bash
# Build image
./docker-run.sh build

# View logs
./docker-run.sh logs

# Stop containers
./docker-run.sh stop

# Open shell
./docker-run.sh shell
```

## 🌐 Webhook Setup

### Automatic Setup (After Deployment)

```bash
python deploy_webhook.py
```

### Manual Setup

```bash
# Check webhook status
python webhook_setup.py info

# Set webhook URL
python webhook_setup.py set https://your-domain.com/webhook

# Delete webhook
python webhook_setup.py delete

# Test webhook
python webhook_setup.py test
```

## 📖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and show welcome message |
| `/help` | Display available commands and features |
| `/generate [prompt]` | Generate AI images from text descriptions |
| `/stats` | Show bot usage statistics |

### Features

- **Text Messages**: Send any text for AI conversation
- **Photo Analysis**: Send photos for detailed AI analysis
- **Image Generation**: Use `/generate` command or ask for image creation
- **Group Chats**: Works in groups with mention detection (@botname)

## 🏗️ Architecture

### Core Components

- **Flask Application** (`app.py`): Web server and webhook handler
- **Telegram Bot** (`telegram_bot.py`): Message processing and bot logic
- **Gemini Service** (`gemini_service.py`): AI integration layer
- **Configuration** (`config.py`): Environment and settings management

### AI Models Used

- **Gemini 2.5 Flash**: Fast conversations and general tasks
- **Gemini 2.5 Pro**: Image analysis and complex reasoning
- **Gemini 2.0 Flash Preview**: AI image generation

### Deployment Modes

- **Polling Mode**: Bot actively checks for messages (good for development)
- **Webhook Mode**: Telegram sends messages to your server (production ready)
- **Auto Mode**: Automatically chooses best mode based on environment

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from BotFather |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `TELEGRAM_BOT_USERNAME` | No | Bot username (auto-detected) |
| `WEBHOOK_URL` | No | Webhook URL for production |
| `BOT_MODE` | No | Force mode: 'polling' or 'webhook' |

### Rate Limiting

- **Message Limit**: 10 messages per minute per user
- **Image Analysis**: 5 requests per minute per user
- **Image Generation**: 3 requests per minute per user

## 🔍 Monitoring

### Health Checks

```bash
# Check bot health
curl http://localhost:5000/health

# Get detailed status
curl http://localhost:5000/health?detailed=true
```

### Logs

```bash
# View live logs (Docker)
./docker-run.sh logs

# View logs (Python)
tail -f bot.log
```

## 🛠️ Development

### Project Structure

```
├── app.py                 # Flask application and webhook handler
├── polling_bot.py         # Polling mode runner
├── webhook_bot.py         # Webhook mode runner
├── main.py               # Auto-detection entry point
├── telegram_bot.py       # Bot logic and handlers
├── gemini_service.py     # AI service integration
├── config.py            # Configuration management
├── utils.py             # Utility functions
├── models.py            # Data models
├── auto_webhook.py      # Automatic webhook setup
├── webhook_setup.py     # Manual webhook management
├── deploy_webhook.py    # Deployment helper
├── docker-run.sh        # Docker management script
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Service orchestration
└── pyproject.toml       # Python dependencies
```

### Adding Features

1. **New Commands**: Add handlers in `telegram_bot.py`
2. **AI Features**: Extend `gemini_service.py`
3. **Web Endpoints**: Add routes in `app.py`
4. **Configuration**: Update `config.py`

### Testing

```bash
# Test webhook endpoint
python -c "
import requests
response = requests.post('http://localhost:5000/webhook', json={
    'update_id': 1,
    'message': {
        'message_id': 1,
        'date': 1234567890,
        'chat': {'id': 123, 'type': 'private'},
        'from': {'id': 123, 'is_bot': False, 'first_name': 'Test'},
        'text': '/start'
    }
})
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

## 🚀 Production Deployment

### Replit Deployment

1. Click the **Deploy** button in Replit
2. Get your deployment URL
3. Run webhook setup:
   ```bash
   python deploy_webhook.py
   ```

### VPS/Cloud Deployment

1. **Clone repository** on your server
2. **Set environment variables**
3. **Run with Docker**:
   ```bash
   ./docker-run.sh webhook --detach
   ```
4. **Set up webhook**:
   ```bash
   python deploy_webhook.py
   ```

### SSL/HTTPS Requirements

Webhooks require HTTPS. Use:
- Replit Deployments (automatic HTTPS)
- Nginx with Let's Encrypt
- Cloudflare proxy
- Other reverse proxy solutions

## 🔒 Security

- **Rate limiting** prevents abuse
- **Input validation** for all user data
- **Error handling** prevents crashes
- **Non-root Docker user** for security
- **Environment secrets** for API keys

## 🐛 Troubleshooting

### Common Issues

**Bot not responding**:
```bash
# Check if bot is running
curl http://localhost:5000/health

# Check Telegram webhook
python webhook_setup.py info
```

**Webhook setup failed**:
```bash
# Verify URL is accessible
curl https://your-domain.com/health

# Check webhook manually
python webhook_setup.py set https://your-domain.com/webhook
```

**Image generation not working**:
- Verify `GEMINI_API_KEY` is set correctly
- Check API quotas and billing
- Review logs for specific errors

### Support

- Check the [Webhook Setup Guide](WEBHOOK_SETUP_GUIDE.md)
- Review [Docker Documentation](README-Docker.md)
- Check logs for error details
- Verify all environment variables are set

## 📝 License

This project is open source. Feel free to use, modify, and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Test thoroughly
5. Submit pull request

---

**Built with ❤️ using Python, Google Gemini AI, and Telegram Bot API**