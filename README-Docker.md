# Docker Deployment Guide

This guide explains how to run your Telegram bot using Docker for consistent deployment across different environments.

## Quick Start

1. **Set up environment variables:**
   ```bash
   # Copy and edit the environment file
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

2. **Run with Docker Compose (Recommended):**
   ```bash
   # Polling mode (default)
   ./docker-run.sh polling

   # Webhook mode
   ./docker-run.sh webhook

   # Run in background
   ./docker-run.sh polling --detach
   ```

3. **Set up webhook (for webhook mode):**
   ```bash
   # After deploying your app to get a public URL
   python webhook_setup.py set https://your-app-url.com/webhook
   
   # Check webhook status
   python webhook_setup.py info
   
   # Test webhook
   python webhook_setup.py test
   ```

3. **Run with Docker directly:**
   ```bash
   # Build image
   docker build -t telegram-bot-ai .

   # Run polling mode
   docker run --env-file .env telegram-bot-ai

   # Run webhook mode
   docker run --env-file .env -p 5000:5000 telegram-bot-ai python main.py
   ```

## Environment Variables

Create a `.env` file with these variables:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
GEMINI_API_KEY=your_gemini_api_key

# Optional
TELEGRAM_BOT_USERNAME=your_bot_username
WEBHOOK_URL=https://your-domain.com/webhook
```

## Docker Commands

### Using the Helper Script

```bash
# Build image
./docker-run.sh build

# Start in polling mode
./docker-run.sh polling

# Start in webhook mode  
./docker-run.sh webhook

# Run in background
./docker-run.sh polling --detach

# View logs
./docker-run.sh logs

# Stop containers
./docker-run.sh stop

# Open shell in container
./docker-run.sh shell
```

### Manual Docker Commands

```bash
# Build image
docker-compose build

# Start polling mode
docker-compose up telegram-bot

# Start webhook mode
docker-compose --profile webhook up telegram-bot-webhook

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop and remove containers
docker-compose down

# Restart services
docker-compose restart
```

## Deployment Options

### 1. Polling Mode (Recommended for development)
- Bot actively polls Telegram for messages
- Works behind firewalls and NAT
- No public URL required
- Slightly higher latency

```bash
./docker-run.sh polling
```

### 2. Webhook Mode (Recommended for production)
- Telegram sends messages directly to your bot
- Requires public HTTPS URL
- Lower latency and resource usage
- Better for high-traffic bots

```bash
# Set WEBHOOK_URL in .env first
./docker-run.sh webhook
```

## Production Deployment

### On a VPS/Cloud Server

1. **Install Docker and Docker Compose**
2. **Clone your bot repository**
3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your keys
   ```
4. **Run in webhook mode:**
   ```bash
   ./docker-run.sh webhook --detach
   ```
5. **Set up reverse proxy (nginx/traefik) for HTTPS**

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml telegram-bot
```

### Using Kubernetes

```bash
# Create secret for API keys
kubectl create secret generic telegram-bot-secrets \
  --from-literal=telegram-token=your_token \
  --from-literal=gemini-key=your_key

# Deploy using the provided k8s manifests
kubectl apply -f k8s/
```

## Monitoring and Logs

### View Real-time Logs
```bash
./docker-run.sh logs
```

### Health Checks
The container includes built-in health checks:
```bash
# Check container health
docker-compose ps

# Manual health check
curl http://localhost:5000/health
```

### Log Rotation
Logs are automatically rotated by Docker. Configure in docker-compose.yml:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
./docker-run.sh logs

# Check environment variables
docker-compose config

# Rebuild image
./docker-run.sh build --no-cache
```

### Bot Not Responding
```bash
# Check bot status
curl http://localhost:5000/health

# View detailed logs
docker-compose logs -f telegram-bot
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check container health
docker-compose ps
```

## Security Best Practices

1. **Use secrets management** for API keys in production
2. **Run as non-root user** (included in Dockerfile)
3. **Use specific image tags** instead of 'latest'
4. **Regularly update base images** for security patches
5. **Limit container resources** if needed:

```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

## Updates and Maintenance

### Update Bot Code
```bash
# Pull latest changes
git pull

# Rebuild and restart
./docker-run.sh stop
./docker-run.sh build
./docker-run.sh polling
```

### Update Dependencies
```bash
# Rebuild with latest packages
docker-compose build --no-cache
```

This Docker setup provides a robust, scalable way to deploy your Telegram bot with all its AI capabilities intact.