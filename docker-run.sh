#!/bin/bash

# Docker run script for Telegram Bot with AI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file template...${NC}"
    cat > .env << EOF
# Required Environment Variables
TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
TELEGRAM_BOT_USERNAME=your_bot_username
WEBHOOK_URL=https://your-domain.com/webhook
EOF
    echo -e "${RED}Please edit .env file with your actual API keys before running the bot.${NC}"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "Modes:"
    echo "  polling    Run bot in polling mode (default)"
    echo "  webhook    Run bot in webhook mode"
    echo "  build      Build Docker image only"
    echo "  stop       Stop running containers"
    echo "  logs       Show container logs"
    echo "  shell      Open shell in running container"
    echo ""
    echo "Options:"
    echo "  --build    Force rebuild image"
    echo "  --detach   Run in background"
    echo "  --help     Show this help"
}

# Parse arguments
MODE="polling"
BUILD_FLAG=""
DETACH_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        polling|webhook|build|stop|logs|shell)
            MODE="$1"
            shift
            ;;
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --detach|-d)
            DETACH_FLAG="-d"
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
case $MODE in
    polling)
        echo -e "${GREEN}Starting Telegram Bot in polling mode...${NC}"
        docker-compose $BUILD_FLAG up $DETACH_FLAG telegram-bot
        ;;
    webhook)
        echo -e "${GREEN}Starting Telegram Bot in webhook mode...${NC}"
        docker-compose --profile webhook $BUILD_FLAG up $DETACH_FLAG telegram-bot-webhook
        ;;
    build)
        echo -e "${GREEN}Building Docker image...${NC}"
        docker-compose build
        ;;
    stop)
        echo -e "${YELLOW}Stopping all containers...${NC}"
        docker-compose down
        ;;
    logs)
        echo -e "${GREEN}Showing container logs...${NC}"
        docker-compose logs -f
        ;;
    shell)
        echo -e "${GREEN}Opening shell in running container...${NC}"
        docker-compose exec telegram-bot /bin/bash
        ;;
    *)
        echo -e "${RED}Invalid mode: $MODE${NC}"
        show_usage
        exit 1
        ;;
esac