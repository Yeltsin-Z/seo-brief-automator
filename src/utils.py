import re
import time
import logging
from typing import List, Dict, Any
from urllib.parse import urlparse, urljoin
import requests
from fake_useragent import UserAgent
from config.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Utils:
    """Utility functions for SEO Brief Automator"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Get a random user agent string"""
        try:
            ua = UserAgent()
            return ua.random
        except:
            return Config.USER_AGENT
    
    @staticmethod
    def make_request(url: str, headers: Dict = None, timeout: int = None) -> requests.Response:
        """Make HTTP request with retry logic"""
        if headers is None:
            headers = {
                'User-Agent': Utils.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
        
        if timeout is None:
            timeout = Config.REQUEST_TIMEOUT
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    @staticmethod
    def chunk_text(text: str, max_length: int = 1000) -> List[str]:
        """Split text into chunks of specified length"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        for sentence in text.split('.'):
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + '.'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '.'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract potential keywords from text"""
        # Simple keyword extraction (can be enhanced with NLP libraries)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:max_keywords]]
    
    @staticmethod
    def save_to_file(content: str, filename: str, directory: str = None) -> str:
        """Save content to file"""
        if directory is None:
            directory = Config.OUTPUT_DIR
        
        import os
        os.makedirs(directory, exist_ok=True)
        
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Content saved to: {filepath}")
        return filepath
    
    @staticmethod
    def format_timestamp() -> str:
        """Get formatted timestamp for filenames"""
        return time.strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        return filename 