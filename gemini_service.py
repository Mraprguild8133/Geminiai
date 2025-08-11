"""
Google Gemini AI service for chat, image analysis, and image generation.
"""

import logging
import os
import tempfile
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
import requests
from PIL import Image
import io

logger = logging.getLogger(__name__)

class GeminiService:
    """Service class for interacting with Google Gemini AI."""
    
    def __init__(self, api_key: str):
        """Initialize Gemini service with API key."""
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        
        # Model configurations
        self.chat_model = "gemini-2.5-flash"
        self.vision_model = "gemini-2.5-pro"
        self.image_gen_model = "gemini-2.0-flash-preview-image-generation"
        
        logger.info("Gemini service initialized successfully")
    
    def generate_response(self, message: str, conversation_context: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate AI response to user message with conversation context.
        
        Args:
            message: User's message
            conversation_context: Previous conversation messages
            
        Returns:
            AI generated response
        """
        try:
            # Build the conversation context
            prompt_parts = []
            
            # Add system instruction
            system_instruction = (
                "You are a helpful AI assistant in a Telegram bot. "
                "Provide concise, helpful responses. Be friendly and conversational. "
                "If asked about your capabilities, mention that you can analyze images "
                "and generate images using the /image command."
            )
            
            # Add conversation history if available
            if conversation_context:
                for ctx in conversation_context[-10:]:  # Last 10 messages for context
                    prompt_parts.append(f"{ctx['role']}: {ctx['content']}")
            
            # Add current message
            prompt_parts.append(f"user: {message}")
            
            full_prompt = "\n".join(prompt_parts)
            
            response = self.client.models.generate_content(
                model=self.chat_model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=1000,
                    temperature=0.7
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "I'm sorry, I couldn't generate a response right now."
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm experiencing some technical difficulties. Please try again later."
    
    def analyze_image(self, image_data: bytes, prompt: Optional[str] = None) -> str:
        """
        Analyze an image using Gemini Vision.
        
        Args:
            image_data: Raw image data
            prompt: Optional custom prompt for analysis
            
        Returns:
            Analysis result
        """
        try:
            if not prompt:
                prompt = (
                    "Analyze this image in detail. Describe what you see, "
                    "including objects, people, scenery, text, and any notable features. "
                    "Be descriptive but concise."
                )
            
            response = self.client.models.generate_content(
                model=self.vision_model,
                contents=[
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type="image/jpeg"
                    ),
                    prompt
                ]
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "I couldn't analyze this image. Please try with a different image."
                
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return "I'm having trouble analyzing this image right now. Please try again later."
    
    def generate_image(self, prompt: str) -> Optional[bytes]:
        """
        Generate an image using Gemini.
        
        Args:
            prompt: Text description for image generation
            
        Returns:
            Generated image data as bytes, or None if failed
        """
        try:
            # Enhance the prompt for better results
            enhanced_prompt = f"Create a high-quality, detailed image: {prompt}"
            
            response = self.client.models.generate_content(
                model=self.image_gen_model,
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            if not response.candidates:
                logger.warning("No image generated in response")
                return None
            
            content = response.candidates[0].content
            if not content or not content.parts:
                logger.warning("No content parts in response")
                return None
            
            # Look for image data in response parts
            for part in content.parts:
                if part.inline_data and part.inline_data.data:
                    logger.info("Successfully generated image")
                    return part.inline_data.data
            
            logger.warning("No image data found in response")
            return None
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
    
    def prepare_image_for_analysis(self, image_data: bytes) -> bytes:
        """
        Prepare image data for analysis (resize if needed, convert format).
        
        Args:
            image_data: Raw image data
            
        Returns:
            Processed image data
        """
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (max 2048x2048 for better API performance)
            max_size = 2048
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save as JPEG
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=90)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error preparing image: {e}")
            return image_data  # Return original if processing fails
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the Gemini service.
        
        Returns:
            Health check results
        """
        try:
            # Test basic text generation
            test_response = self.client.models.generate_content(
                model=self.chat_model,
                contents="Say 'OK' if you can respond"
            )
            
            text_working = bool(test_response.text and 'OK' in test_response.text.upper())
            
            return {
                'status': 'healthy' if text_working else 'degraded',
                'text_generation': text_working,
                'api_key_valid': bool(self.api_key),
                'models': {
                    'chat': self.chat_model,
                    'vision': self.vision_model,
                    'image_generation': self.image_gen_model
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'text_generation': False,
                'api_key_valid': bool(self.api_key)
            }
