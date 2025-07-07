import openai
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class APILimitedClient:
    """OpenAI client wrapper that tracks API requests and halts when limit is reached"""
    
    def __init__(self, api_key: str, increment_callback=None):
        self.client = openai.OpenAI(api_key=api_key)
        self.increment_callback = increment_callback
    
    def chat_completions_create(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Create chat completion with API request tracking"""
        if self.increment_callback:
            limit_reached = self.increment_callback()
            if limit_reached:
                logger.error("API request limit reached. Halting generation.")
                raise Exception("API request limit reached (200 requests). Please try again later.")
        
        try:
            response = self.client.chat.completions.create(**kwargs)
            return response
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise e
    
    def __getattr__(self, name):
        """Delegate all other attributes to the underlying client"""
        return getattr(self.client, name) 