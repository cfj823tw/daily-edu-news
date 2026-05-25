"""
Configuration management for Daily Education News system
"""

import os
import json
from datetime import datetime
from pathlib import Path

class Config:
    """Configuration class for the news system"""
    
    # Email configuration
    EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', EMAIL_RECIPIENT)
    
    # API configuration
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    # File paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'
    SCRIPTS_DIR = BASE_DIR / 'scripts'
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    
    # News sources configuration
    NEWS_SOURCES = {
        'rss_feeds': [
            {
                'name': 'Nature Education',
                'url': 'https://www.nature.com/natedu/current_issue',
                'category': 'Research'
            },
            {
                'name': 'EdSurge',
                'url': 'https://www.edsurge.com/feed',
                'category': 'EdTech'
            },
            {
                'name': 'The Chronicle of Higher Education',
                'url': 'https://www.chronicle.com/feed.xml',
                'category': 'Higher Education'
            },
        ],
        'news_api_queries': [
            {'q': 'education', 'sortBy': 'publishedAt'},
            {'q': 'teaching learning', 'sortBy': 'publishedAt'},
            {'q': 'online learning', 'sortBy': 'publishedAt'},
            {'q': 'educational technology', 'sortBy': 'publishedAt'},
        ]
    }
    
    # News collection configuration
    NEWS_PER_QUERY = 3
    MAX_TOTAL_NEWS = 10
    MIN_ARTICLE_LENGTH = 50
    
    # Email template configuration
    EMAIL_SUBJECT = f"📚 Daily Education News - {datetime.now().strftime('%Y-%m-%d')}"
    EMAIL_FROM_NAME = "Daily Education News"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_fields = {
            'EMAIL_RECIPIENT': cls.EMAIL_RECIPIENT,
            'EMAIL_PASSWORD': cls.EMAIL_PASSWORD,
        }
        
        missing = [k for k, v in required_fields.items() if not v]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def get_log_file(cls):
        """Get log file path"""
        return cls.LOGS_DIR / f"crawler_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    @classmethod
    def get_archive_file(cls):
        """Get archive file path"""
        return cls.DATA_DIR / 'news_archive.json'
    
    @classmethod
    def load_sources(cls):
        """Load news sources from file or use default"""
        sources_file = cls.DATA_DIR / 'sources.json'
        if sources_file.exists():
            with open(sources_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return cls.NEWS_SOURCES
