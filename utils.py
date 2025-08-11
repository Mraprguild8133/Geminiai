"""
Utility functions for the Telegram bot.
"""

import logging
import os
import re
from typing import List, Optional
from PIL import Image
import io

logger = logging.getLogger(__name__)

def is_bot_mentioned(message_text: str, bot_username: Optional[str] = None) -> bool:
    """
    Check if the bot is mentioned in a message.
    
    Args:
        message_text: The message text to check
        bot_username: The bot's username (without @)
        
    Returns:
        True if bot is mentioned, False otherwise
    """
    if not message_text:
        return False
    
    # Check for @bot_username mention
    if bot_username:
        mention_pattern = f"@{bot_username.lower()}"
        if mention_pattern in message_text.lower():
            return True
    
    # Check for generic bot mentions
    generic_mentions = ['@bot', 'bot', 'ai', 'assistant']
    message_lower = message_text.lower()
    
    for mention in generic_mentions:
        if mention in message_lower:
            return True
    
    return False

def split_long_message(message: str, max_length: int = 4096) -> List[str]:
    """
    Split a long message into multiple parts.
    
    Args:
        message: The message to split
        max_length: Maximum length per message part
        
    Returns:
        List of message parts
    """
    if len(message) <= max_length:
        return [message]
    
    parts = []
    current_part = ""
    
    # Split by paragraphs first
    paragraphs = message.split('\n\n')
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed limit
        if len(current_part) + len(paragraph) + 2 > max_length:
            if current_part:
                parts.append(current_part.strip())
                current_part = ""
            
            # If single paragraph is too long, split by sentences
            if len(paragraph) > max_length:
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                for sentence in sentences:
                    if len(current_part) + len(sentence) + 1 > max_length:
                        if current_part:
                            parts.append(current_part.strip())
                            current_part = ""
                    
                    if len(sentence) > max_length:
                        # Split by words if sentence is too long
                        words = sentence.split()
                        for word in words:
                            if len(current_part) + len(word) + 1 > max_length:
                                if current_part:
                                    parts.append(current_part.strip())
                                    current_part = word
                            else:
                                current_part += " " + word if current_part else word
                    else:
                        current_part += " " + sentence if current_part else sentence
            else:
                current_part = paragraph
        else:
            current_part += "\n\n" + paragraph if current_part else paragraph
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts

def validate_image(image_data: bytes, max_size: int = 20 * 1024 * 1024) -> bool:
    """
    Validate image data.
    
    Args:
        image_data: Raw image data
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if image is valid, False otherwise
    """
    try:
        # Check file size
        if len(image_data) > max_size:
            logger.warning(f"Image too large: {len(image_data)} bytes")
            return False
        
        # Try to open with PIL to validate format
        image = Image.open(io.BytesIO(image_data))
        
        # Check if it's a valid image format
        valid_formats = ['JPEG', 'PNG', 'WebP', 'GIF', 'BMP']
        if image.format not in valid_formats:
            logger.warning(f"Unsupported image format: {image.format}")
            return False
        
        # Check reasonable dimensions
        if image.width > 10000 or image.height > 10000:
            logger.warning(f"Image dimensions too large: {image.width}x{image.height}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Image validation error: {e}")
        return False

def format_uptime(start_time) -> str:
    """
    Format uptime in a human-readable way.
    
    Args:
        start_time: datetime when the bot started
        
    Returns:
        Formatted uptime string
    """
    from datetime import datetime
    
    uptime = datetime.now() - start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove extra spaces and dots
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = re.sub(r'\.+', '.', sanitized)
    
    # Limit length
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:200-len(ext)] + ext
    
    return sanitized

def extract_command_args(text: str, command: str) -> str:
    """
    Extract arguments from a command message.
    
    Args:
        text: Full message text
        command: Command name (without /)
        
    Returns:
        Arguments string
    """
    pattern = f"^/{command}\\s*(.*)"
    match = re.match(pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return ""

def escape_markdown(text: str) -> str:
    """
    Escape special markdown characters.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text
