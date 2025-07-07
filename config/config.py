import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for SEO Brief Automator"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Scraping Settings
    SERP_RESULTS_COUNT = 10
    REQUEST_TIMEOUT = 30
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    # UGC Platforms
    UGC_PLATFORMS = [
        'reddit.com',
        'quora.com',
        'stackoverflow.com',
        'forums.com',
        'community.com'
    ]
    
    # Content Analysis Settings
    MAX_TOKENS_PER_REQUEST = 4000
    SUMMARY_LENGTH = 200
    KEY_POINTS_COUNT = 5
    
    # Output Settings
    OUTPUT_DIR = 'output'
    BRIEF_TEMPLATE_PATH = 'templates/brief_template.html'
    
    # Flask Settings
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Selenium Settings
    SELENIUM_HEADLESS = True
    SELENIUM_TIMEOUT = 20
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required in environment variables")
        
        # Create output directory if it doesn't exist
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        
        return True 