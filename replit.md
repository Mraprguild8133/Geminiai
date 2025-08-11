# Telegram Bot with AI Capabilities

## Overview

This is a Telegram bot powered by Google Gemini AI that provides conversational AI, image analysis, and image generation capabilities. The bot can operate in both private chats and group environments, with intelligent mention detection for group interactions. It features a Flask-based webhook architecture for handling Telegram updates and integrates with Google's Gemini AI models for various AI-powered functionalities.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- **August 11, 2025**: Enhanced Telegram group support and reply functionality
  - Added comprehensive group ID tracking and connection support
  - Implemented intelligent reply detection for bot messages in groups
  - Enhanced group conversation context with group name and reply information
  - Added GroupInfo model to track group details (ID, name, type, member count, join date)
  - Improved bot mention detection using dynamic username (@Multibotassitbot)
  - Added group statistics tracking in bot metrics
  - Enhanced message models with reply context (reply_to_message_id, is_reply_to_bot)
  - Bot now provides contextual AI responses based on group information and reply context
  - Fixed username display to show @Multibotassitbot in all commands and messages

## System Architecture

### Backend Architecture
- **Framework**: Flask web application serving as the main entry point
- **Bot Framework**: Python Telegram Bot library (python-telegram-bot) for handling Telegram API interactions
- **Group Support**: Enhanced group management with automatic group tracking and intelligent reply detection
- **Async Handling**: Custom async route decorator for handling asynchronous operations within Flask's synchronous context
- **Webhook Pattern**: Uses webhook-based message handling instead of polling for better scalability
- **Context Management**: Smart conversation context including group information and reply relationships

### AI Integration
- **Primary AI Service**: Google Gemini AI with multiple model variants:
  - `gemini-2.5-flash` for general chat conversations
  - `gemini-2.5-pro` for image analysis and vision tasks
  - `gemini-2.0-flash-preview-image-generation` for image generation
- **Conversation Management**: In-memory conversation history storage with configurable limits
- **Multi-modal Support**: Text, image analysis, and image generation capabilities

### Data Models
- **Message Tracking**: Enhanced message representation with reply context (reply_to_message_id, is_reply_to_bot)
- **Group Information**: GroupInfo model tracks group ID, name, type, member count, and join date
- **Conversation Context**: Maintains conversation history with group information for contextual AI responses
- **Chat Type Support**: Handles private, group, supergroup, and channel interactions with intelligent response logic
- **Statistics Tracking**: Enhanced bot usage statistics including group count and detailed metrics

### Security and Rate Limiting
- **Rate Limiting**: Per-user message rate limiting to prevent abuse
- **Input Validation**: Image size and format validation
- **Configuration Validation**: Runtime validation of required environment variables

### Error Handling and Logging
- **Structured Logging**: Comprehensive logging throughout all components
- **Graceful Degradation**: Error handling with user-friendly messages
- **Health Monitoring**: Built-in health check endpoints and status reporting

## External Dependencies

### Required Services
- **Telegram Bot API**: Requires bot token from @BotFather for Telegram integration
- **Google Gemini AI**: Requires API key for AI conversation, image analysis, and generation capabilities

### Python Libraries
- **Flask**: Web framework for webhook handling
- **python-telegram-bot**: Official Telegram bot framework
- **google-genai**: Google Generative AI client library
- **Pillow (PIL)**: Image processing and validation
- **requests**: HTTP client for external API calls

### Configuration Requirements
- **Environment Variables**: TELEGRAM_BOT_TOKEN and GEMINI_API_KEY are mandatory
- **Optional Configuration**: WEBHOOK_URL, TELEGRAM_BOT_USERNAME for enhanced functionality
- **Runtime Parameters**: Configurable limits for conversation history, message length, and rate limiting