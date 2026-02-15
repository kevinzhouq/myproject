import os
import json
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for AI Sports Daily.
    """
    # Reddit API Credentials
    REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "python:ai-sports-daily:v1.0")
    
    # LLM Settings
    OLLAMA_MODEL = "mistral"
    # Use environment variable for Ollama URL or default
    OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    
    # Output Settings
    MAX_HISTORY_DAYS = 30
    
    # Dynamic Settings (Loaded from JSON)
    RSS_FEEDS = []          # List of dicts: {name, url, category}
    REDDIT_SUBREDDITS = []  # List of dicts: {name, category}
    KEYWORDS = []
    
    _sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sources.json')

    @classmethod
    def load(cls):
        """Load configuration from sources.json"""
        logger.info(f"Loading config from {cls._sources_path}...")
        
        data = {
            "rss": [],
            "reddit_subreddits": [],
            "keywords": []
        }
        
        if os.path.exists(cls._sources_path):
            try:
                with open(cls._sources_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        loaded_data = json.loads(content)
                        data.update(loaded_data)
            except Exception as e:
                logger.error(f"Error loading config file: {e}")

        # Store complete RSS Feeds (filter out invalid ones)
        cls.RSS_FEEDS = []
        for item in data.get('rss', []):
            if isinstance(item, dict) and item.get('url'):
                cls.RSS_FEEDS.append({
                    'name': item.get('name', 'Unknown'),
                    'url': item.get('url'),
                    'category': item.get('category', 'AI前沿')
                })
            elif isinstance(item, str) and item.strip():
                cls.RSS_FEEDS.append({'name': 'Unknown', 'url': item.strip(), 'category': 'AI前沿'})

        # Store complete Subreddits
        cls.REDDIT_SUBREDDITS = []
        for item in data.get('reddit_subreddits', []):
            if isinstance(item, dict) and item.get('name'):
                cls.REDDIT_SUBREDDITS.append({
                    'name': item.get('name'),
                    'category': item.get('category', 'AI前沿')
                })
            elif isinstance(item, str) and item.strip():
                cls.REDDIT_SUBREDDITS.append({'name': item.strip(), 'category': 'AI前沿'})
                
        # Parse Keywords
        cls.KEYWORDS = [k for k in data.get('keywords', []) if isinstance(k, str)]
        
        logger.info(f"Loaded {len(cls.RSS_FEEDS)} RSS feeds, {len(cls.REDDIT_SUBREDDITS)} Subreddits.")

    @classmethod
    def reload(cls):
        """Reload configuration"""
        cls.load()

    @classmethod
    def get_rss_feeds_details(cls):
        """Return full RSS feed details (name, category, url)"""
        # Re-read to ensure we get the full dict objects, as accessing cls.RSS_FEEDS only gives URLs
        if os.path.exists(cls._sources_path):
            try:
                with open(cls._sources_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [item for item in data.get('rss', []) if isinstance(item, dict)]
            except:
                pass
        return []

# Initialize config on module import
Config.load()
