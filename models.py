"""
Data models for the Telegram bot.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class MessageType(Enum):
    """Types of messages supported by the bot."""
    TEXT = "text"
    PHOTO = "photo"
    COMMAND = "command"
    GENERATED_IMAGE = "generated_image"

class ChatType(Enum):
    """Types of chats supported by the bot."""
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"

@dataclass
class GroupInfo:
    """Information about a Telegram group."""
    group_id: int
    group_name: str
    group_type: str  # "group" or "supergroup"
    member_count: Optional[int] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    joined_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass  
class Message:
    """Represents a message in the conversation."""
    user_id: int
    chat_id: int
    message_id: int
    text: str
    message_type: MessageType
    timestamp: datetime = field(default_factory=datetime.now)
    username: Optional[str] = None
    file_path: Optional[str] = None
    reply_to_message_id: Optional[int] = None
    is_reply_to_bot: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'user_id': self.user_id,
            'chat_id': self.chat_id,
            'message_id': self.message_id,
            'text': self.text,
            'message_type': self.message_type.value,
            'timestamp': self.timestamp.isoformat(),
            'username': self.username,
            'file_path': self.file_path,
            'reply_to_message_id': self.reply_to_message_id,
            'is_reply_to_bot': self.is_reply_to_bot
        }

@dataclass
class Conversation:
    """Represents a conversation history for a chat."""
    chat_id: int
    chat_type: ChatType
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    group_info: Optional[GroupInfo] = None
    
    def add_message(self, message: Message, max_history: int = 20):
        """Add a message to the conversation history."""
        self.messages.append(message)
        self.last_updated = datetime.now()
        
        # Keep only the last max_history messages
        if len(self.messages) > max_history:
            self.messages = self.messages[-max_history:]
    
    def get_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get conversation context for AI processing."""
        context = []
        recent_messages = self.messages[-max_messages:] if self.messages else []
        
        for msg in recent_messages:
            if msg.message_type in [MessageType.TEXT, MessageType.COMMAND]:
                role = "user" if msg.text.startswith('/') == False else "user"
                context.append({
                    "role": role,
                    "content": msg.text
                })
        
        return context
    
    def clear(self):
        """Clear conversation history."""
        self.messages.clear()
        self.last_updated = datetime.now()

@dataclass
class BotStats:
    """Bot statistics and metrics."""
    total_messages: int = 0
    total_images_analyzed: int = 0
    total_images_generated: int = 0
    total_groups: int = 0
    total_conversations: int = 0
    uptime_start: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        uptime = datetime.now() - self.uptime_start
        return {
            'total_messages': self.total_messages,
            'total_images_analyzed': self.total_images_analyzed,
            'total_images_generated': self.total_images_generated,
            'total_groups': self.total_groups,
            'total_conversations': self.total_conversations,
            'uptime_hours': uptime.total_seconds() / 3600
        }
