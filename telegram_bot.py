"""
Telegram bot implementation with AI capabilities.
"""

import logging
import os
import tempfile
from typing import Dict, Optional
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

from telegram import Update, Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes
)
from telegram.constants import ParseMode

from gemini_service import GeminiService
from models import Message, Conversation, ChatType, MessageType, BotStats, GroupInfo
from config import Config
from utils import is_bot_mentioned, split_long_message, validate_image

logger = logging.getLogger(__name__)

class TelegramBot:
    """Main Telegram bot class with AI capabilities."""
    
    def __init__(self, token: str, gemini_service: GeminiService):
        """Initialize the Telegram bot."""
        self.token = token
        self.gemini_service = gemini_service
        self.conversations: Dict[int, Conversation] = {}
        self.groups: Dict[int, GroupInfo] = {}  # Track group information
        self.stats = BotStats()
        self.rate_limits: Dict[int, list] = defaultdict(list)
        self.bot_username = None  # Will be set when bot starts
        
        # Initialize bot application
        self.application = Application.builder().token(token).build()
        self._setup_handlers()
        
        logger.info("Telegram bot initialized successfully")
    
    def _setup_handlers(self):
        """Set up message and command handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("health", self.health_command))
        self.application.add_handler(CommandHandler("image", self.image_command))
        
        # Additional command handlers
        self.application.add_handler(CommandHandler("groupid", self.groupid_command))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo_message))
        
        logger.info("Bot handlers set up successfully")
    
    async def get_bot_username(self):
        """Get and cache the bot's username."""
        if not self.bot_username:
            try:
                bot_info = await self.application.bot.get_me()
                self.bot_username = bot_info.username
                logger.info(f"Bot username detected: @{self.bot_username}")
            except Exception as e:
                logger.error(f"Failed to get bot username: {e}")
                self.bot_username = "Unknown"
        return self.bot_username
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user is rate limited."""
        now = datetime.now()
        window_start = now - timedelta(seconds=Config.RATE_LIMIT_WINDOW)
        
        # Clean old entries
        self.rate_limits[user_id] = [
            timestamp for timestamp in self.rate_limits[user_id]
            if timestamp > window_start
        ]
        
        # Check if under limit
        if len(self.rate_limits[user_id]) >= Config.RATE_LIMIT_MESSAGES:
            return False
        
        # Add current request
        self.rate_limits[user_id].append(now)
        return True
    
    def _get_or_create_conversation(self, chat_id: int, chat_type: str, chat_title: str = None, member_count: int = None) -> Conversation:
        """Get or create conversation for a chat."""
        if chat_id not in self.conversations:
            chat_type_enum = ChatType.PRIVATE
            if chat_type == "group":
                chat_type_enum = ChatType.GROUP
            elif chat_type == "supergroup":
                chat_type_enum = ChatType.SUPERGROUP
            elif chat_type == "channel":
                chat_type_enum = ChatType.CHANNEL
            
            # Create group info if it's a group chat
            group_info = None
            if chat_type in ["group", "supergroup"] and chat_title:
                group_info = GroupInfo(
                    group_id=chat_id,
                    group_name=chat_title,
                    group_type=chat_type,
                    member_count=member_count
                )
                self.groups[chat_id] = group_info
                self.stats.total_groups += 1
                logger.info(f"Bot joined group: {chat_title} (ID: {chat_id}, Type: {chat_type})")
            
            self.conversations[chat_id] = Conversation(
                chat_id=chat_id,
                chat_type=chat_type_enum,
                group_info=group_info
            )
            self.stats.total_conversations += 1
        
        return self.conversations[chat_id]
    
    def _should_respond_in_group(self, message_text: str, chat_type: str, is_reply: bool = False, is_reply_to_bot: bool = False) -> bool:
        """Determine if bot should respond in group chat."""
        if chat_type == "private":
            return True
        
        # Respond if:
        # 1. Bot is mentioned by username
        # 2. Message is a reply to bot's message
        # 3. Message is a direct reply to any bot message
        bot_mentioned = is_bot_mentioned(message_text, self.bot_username) if self.bot_username else False
        
        return bot_mentioned or is_reply_to_bot or is_reply
    
    def _check_reply_to_bot(self, update: Update) -> bool:
        """Check if message is a reply to the bot."""
        if not update.message.reply_to_message:
            return False
        
        # Check if reply is to bot's message
        return update.message.reply_to_message.from_user.is_bot and update.message.reply_to_message.from_user.id == self.application.bot.id
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        try:
            # Get bot username
            bot_username = await self.get_bot_username()
            user_name = update.effective_user.first_name or "there"
            
            welcome_message = (
                f"🤖 **Welcome to Gemini AI Assistant, {user_name}!**\n\n"
                f"I'm @{bot_username}, your AI-powered Telegram bot with advanced capabilities:\n\n"
                "💬 **Smart Conversations** - Chat with me naturally\n"
                "📸 **Photo Analysis** - Send me images for AI analysis\n"
                "🎨 **Image Generation** - Use `/image <description>` to create AI art\n"
                f"👥 **Group Support** - Add me to groups (mention @{bot_username} or reply to respond)\n\n"
                "🚀 **Get Started:**\n"
                "• Just start typing to chat with me\n"
                "• Send a photo for analysis\n"
                "• Try `/image sunset over mountains`\n"
                "• Use `/help` for all commands\n\n"
                "Ready to assist you! 🌟"
            )
            
            await update.message.reply_text(
                welcome_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Track conversation with group info
            conversation = self._get_or_create_conversation(
                update.effective_chat.id,
                update.effective_chat.type,
                getattr(update.effective_chat, 'title', None),
                getattr(update.effective_chat, 'member_count', None)
            )
            
            # Check for reply context
            reply_to_message_id = None
            is_reply_to_bot = False
            if update.message.reply_to_message:
                reply_to_message_id = update.message.reply_to_message.message_id
                is_reply_to_bot = self._check_reply_to_bot(update)
            
            message = Message(
                user_id=update.effective_user.id,
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
                text="/start",
                message_type=MessageType.COMMAND,
                username=update.effective_user.username,
                reply_to_message_id=reply_to_message_id,
                is_reply_to_bot=is_reply_to_bot
            )
            conversation.add_message(message, Config.MAX_CONVERSATION_HISTORY)
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text("Sorry, I encountered an error. Please try again.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        try:
            bot_username = await self.get_bot_username()
            help_message = (
                "🤖 **Gemini AI Assistant - Help**\n\n"
                "**Available Commands:**\n"
                "• `/start` - Welcome message and introduction\n"
                "• `/help` - Show this help message\n"
                "• `/image <description>` - Generate AI image\n"
                "• `/clear` - Clear conversation history\n"
                "• `/health` - Check bot status\n"
                "• `/groupinfo` - Show group information (groups only)\n\n"
                "**Features:**\n"
                "• **Text Chat** - Just type any message to chat with AI\n"
                "• **Photo Analysis** - Send any image for detailed analysis\n"
                "• **Image Generation** - Describe what you want to see\n"
                f"• **Group Chat** - Mention me (@{bot_username}) or reply to my messages\n\n"
                "**Examples:**\n"
                "• `Tell me a joke`\n"
                "• `Explain quantum physics simply`\n"
                "• `/image cat wearing a space suit`\n"
                "• Send a photo with caption `What's in this image?`\n\n"
                "**Tips:**\n"
                "• I remember our conversation context\n"
                "• You can ask follow-up questions\n"
                "• Images work best in good lighting\n"
                "• Be specific with image generation prompts\n\n"
                "Need more help? Just ask me anything! 🌟"
            )
            
            await update.message.reply_text(
                help_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text("Sorry, I couldn't display the help message.")
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command."""
        try:
            conversation = self._get_or_create_conversation(
                update.effective_chat.id,
                update.effective_chat.type
            )
            conversation.clear()
            
            await update.message.reply_text(
                "🧹 Conversation history cleared! Starting fresh.",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in clear command: {e}")
            await update.message.reply_text("Sorry, I couldn't clear the conversation.")
    
    async def health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /health command."""
        try:
            # Get Gemini service health
            gemini_health = self.gemini_service.health_check()
            bot_stats = self.stats.to_dict()
            config_info = Config.get_bot_info()
            
            status_emoji = "✅" if gemini_health['status'] == 'healthy' else "⚠️"
            
            health_message = (
                f"🏥 **Bot Health Status** {status_emoji}\n\n"
                f"**Bot Status:** {gemini_health['status'].title()}\n"
                f"**AI Text Generation:** {'✅' if gemini_health.get('text_generation') else '❌'}\n"
                f"**API Keys:** {'✅' if config_info['has_gemini_key'] else '❌'}\n\n"
                f"**Statistics:**\n"
                f"• Messages Processed: {bot_stats['total_messages']}\n"
                f"• Images Analyzed: {bot_stats['total_images_analyzed']}\n"
                f"• Images Generated: {bot_stats['total_images_generated']}\n"
                f"• Active Conversations: {bot_stats['total_conversations']}\n"
                f"• Uptime: {bot_stats['uptime_hours']:.1f} hours\n\n"
                f"**Configuration:**\n"
                f"• Max History: {config_info['max_history']} messages\n"
                f"• Bot Username: {config_info.get('bot_username', 'Not Set')}\n\n"
                f"**AI Models:**\n"
                f"• Chat: {gemini_health.get('models', {}).get('chat', 'N/A')}\n"
                f"• Vision: {gemini_health.get('models', {}).get('vision', 'N/A')}\n"
                f"• Image Gen: {gemini_health.get('models', {}).get('image_generation', 'N/A')}"
            )
            
            await update.message.reply_text(
                health_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in health command: {e}")
            await update.message.reply_text("❌ Health check failed. Please contact administrator.")
    
    async def groupid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /groupid command to show current chat/group ID."""
        try:
            chat = update.effective_chat
            user = update.effective_user
            
            if chat.type == "private":
                message = (
                    f"💬 **Private Chat Information**\n\n"
                    f"🆔 **Your User ID:** `{user.id}`\n"
                    f"👤 **Name:** {user.first_name or 'Unknown'}\n"
                    f"📧 **Username:** @{user.username or 'None'}\n"
                    f"🔗 **Chat ID:** `{chat.id}`"
                )
            else:
                group_type = chat.type.title()
                message = (
                    f"🏢 **Group Information**\n\n"
                    f"🆔 **Group ID:** `{chat.id}`\n"
                    f"📝 **Group Name:** {chat.title or 'Unknown'}\n"
                    f"📊 **Type:** {group_type}\n"
                    f"👥 **Member Count:** {getattr(chat, 'member_count', 'Unknown')}\n\n"
                    f"💡 **Copy the Group ID above to use it in your applications!**"
                )
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in groupid command: {e}")
            await update.message.reply_text("Sorry, I couldn't retrieve the group ID information.")
    
    async def image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /image command for AI image generation."""
        try:
            # Check rate limiting
            if not self._check_rate_limit(update.effective_user.id):
                await update.message.reply_text(
                    "⏰ You're sending messages too quickly. Please wait a moment and try again."
                )
                return
            
            # Get the prompt from command arguments
            prompt = " ".join(context.args) if context.args else None
            
            if not prompt:
                await update.message.reply_text(
                    "🎨 **Image Generation**\n\n"
                    "Please provide a description for the image you want to generate.\n\n"
                    "**Example:** `/image sunset over mountains with purple sky`\n"
                    "**Example:** `/image cute robot playing guitar`\n"
                    "**Example:** `/image abstract art with flowing colors`"
                )
                return
            
            # Send "generating" message
            generating_msg = await update.message.reply_text(
                "🎨 Generating your image... This may take a moment.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Generate image
            image_data = self.gemini_service.generate_image(prompt)
            
            if image_data:
                # Send the generated image
                await update.message.reply_photo(
                    photo=image_data,
                    caption=f"🎨 **Generated Image**\n📝 Prompt: {prompt}",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Delete generating message
                await generating_msg.delete()
                
                self.stats.total_images_generated += 1
                
                # Track in conversation
                conversation = self._get_or_create_conversation(
                    update.effective_chat.id,
                    update.effective_chat.type
                )
                
                message = Message(
                    user_id=update.effective_user.id,
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id,
                    text=f"/image {prompt}",
                    message_type=MessageType.GENERATED_IMAGE,
                    username=update.effective_user.username
                )
                conversation.add_message(message, Config.MAX_CONVERSATION_HISTORY)
                
            else:
                await generating_msg.edit_text(
                    "❌ **Image Generation Failed**\n\n"
                    "I couldn't generate an image right now. This could be due to:\n"
                    "• Temporary service issues\n"
                    "• Content policy restrictions\n"
                    "• Network problems\n\n"
                    "Please try again with a different prompt."
                )
            
        except Exception as e:
            logger.error(f"Error in image command: {e}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error while generating the image. Please try again."
            )
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        try:
            # Check for reply context
            is_reply_to_bot = self._check_reply_to_bot(update)
            
            # Check if we should respond (for group chats)
            if not self._should_respond_in_group(
                update.message.text,
                update.effective_chat.type,
                bool(update.message.reply_to_message),
                is_reply_to_bot
            ):
                return
            
            # Check rate limiting
            if not self._check_rate_limit(update.effective_user.id):
                await update.message.reply_text(
                    "⏰ You're sending messages too quickly. Please wait a moment and try again."
                )
                return
            
            # Get conversation with group info
            conversation = self._get_or_create_conversation(
                update.effective_chat.id,
                update.effective_chat.type,
                getattr(update.effective_chat, 'title', None),
                getattr(update.effective_chat, 'member_count', None)
            )
            
            # Track reply information
            reply_to_message_id = None
            if update.message.reply_to_message:
                reply_to_message_id = update.message.reply_to_message.message_id
            
            # Add user message to conversation
            user_message = Message(
                user_id=update.effective_user.id,
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
                text=update.message.text,
                message_type=MessageType.TEXT,
                username=update.effective_user.username,
                reply_to_message_id=reply_to_message_id,
                is_reply_to_bot=is_reply_to_bot
            )
            conversation.add_message(user_message, Config.MAX_CONVERSATION_HISTORY)
            
            # Show typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Prepare context with group and reply information
            context_prefix = ""
            if conversation.group_info:
                context_prefix = f"[Group: {conversation.group_info.group_name}] "
            
            if is_reply_to_bot and update.message.reply_to_message:
                context_prefix += f"[Reply to: {update.message.reply_to_message.text[:50]}...] "
            
            # Generate AI response
            context_history = conversation.get_context()
            full_message = context_prefix + update.message.text if context_prefix else update.message.text
            
            ai_response = self.gemini_service.generate_response(
                full_message,
                context_history
            )
            
            # Send response (split if too long)
            response_messages = split_long_message(ai_response, Config.MAX_MESSAGE_LENGTH)
            
            for response_text in response_messages:
                sent_message = await update.message.reply_text(response_text)
                
                # Add AI response to conversation
                ai_message = Message(
                    user_id=0,  # Bot user ID
                    chat_id=update.effective_chat.id,
                    message_id=sent_message.message_id,
                    text=response_text,
                    message_type=MessageType.TEXT,
                    username="AI Assistant"
                )
                conversation.add_message(ai_message, Config.MAX_CONVERSATION_HISTORY)
            
            self.stats.total_messages += 1
            
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text(
                "❌ I'm sorry, I encountered an error processing your message. Please try again."
            )
    
    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages for AI analysis."""
        try:
            # Check for reply context
            is_reply_to_bot = self._check_reply_to_bot(update)
            
            # Check if we should respond (for group chats)
            if not self._should_respond_in_group(
                update.message.caption or "",
                update.effective_chat.type,
                bool(update.message.reply_to_message),
                is_reply_to_bot
            ):
                return
            
            # Check rate limiting
            if not self._check_rate_limit(update.effective_user.id):
                await update.message.reply_text(
                    "⏰ You're sending messages too quickly. Please wait a moment and try again."
                )
                return
            
            # Send analyzing message
            analyzing_msg = await update.message.reply_text(
                "📸 Analyzing your image... Please wait.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Get the largest photo size
            photo = update.message.photo[-1]
            
            # Download photo
            photo_file = await photo.get_file()
            photo_data = await photo_file.download_as_bytearray()
            
            # Validate image
            if not validate_image(bytes(photo_data), Config.MAX_IMAGE_SIZE):
                await analyzing_msg.edit_text(
                    "❌ **Image Processing Error**\n\n"
                    "The image is too large or in an unsupported format. "
                    "Please send a smaller image (max 20MB) in JPG, PNG, or WebP format."
                )
                return
            
            # Prepare image for analysis
            processed_image = self.gemini_service.prepare_image_for_analysis(bytes(photo_data))
            
            # Use custom prompt if provided in caption
            custom_prompt = update.message.caption if update.message.caption else None
            
            # Analyze image
            analysis_result = self.gemini_service.analyze_image(processed_image, custom_prompt)
            
            # Send analysis result (escape markdown to avoid parsing errors)
            from utils import escape_markdown
            escaped_result = escape_markdown(analysis_result)
            await analyzing_msg.edit_text(
                f"📸 **Image Analysis**\n\n{escaped_result}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            self.stats.total_images_analyzed += 1
            
            # Track in conversation with group info
            conversation = self._get_or_create_conversation(
                update.effective_chat.id,
                update.effective_chat.type,
                getattr(update.effective_chat, 'title', None),
                getattr(update.effective_chat, 'member_count', None)
            )
            
            # Track reply information
            reply_to_message_id = None
            if update.message.reply_to_message:
                reply_to_message_id = update.message.reply_to_message.message_id
            
            message = Message(
                user_id=update.effective_user.id,
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
                text=f"[Photo] {update.message.caption or 'Image analysis'}",
                message_type=MessageType.PHOTO,
                username=update.effective_user.username,
                reply_to_message_id=reply_to_message_id,
                is_reply_to_bot=is_reply_to_bot
            )
            conversation.add_message(message, Config.MAX_CONVERSATION_HISTORY)
            
        except Exception as e:
            logger.error(f"Error handling photo message: {e}")
            await update.message.reply_text(
                "❌ I'm sorry, I couldn't analyze this image. Please try again with a different image."
            )
    
    def get_webhook_info(self) -> Dict:
        """Get webhook information for setup."""
        return {
            'token': self.token,
            'application': self.application
        }
