import os

class Config:
    # Reddit API Credentials
    REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "python:ai-sports-daily:v1.0 (by /u/YOUR_USERNAME)")

    # RSS Feeds
    RSS_FEEDS = [
        # AI & Tech
        "https://www.jiqizhixin.com/rss",
        "https://36kr.com/feed",
        "https://sspai.com/feed",
        # Sports & Running
        "https://www.runnersworld.com/rss/all.xml", 
    ]

    # Reddit Subreddits to monitor
    REDDIT_SUBREDDITS = [
        "ArtificialIntelligence",
        "MachineLearning",
        "running",
        "AdvancedRunning",
        "MarathonTraining"
    ]
    
    # Keywords for filtering relevant content
    # Only articles containing these keywords (case-insensitive) will be prioritized
    KEYWORDS = [
        "AI", "LLM", "大模型", "Transformer", "Agent",
        "Marathon", "Running", "Training", "Recovery", "Nutrition", "Zone 2",
        "Nike", "Adidas", "Garmin", "Coros", "Suunto"
    ]

    # LLM Settings
    OLLAMA_MODEL = "mistral"
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    
    # Output Settings
    MAX_HISTORY_DAYS = 30
