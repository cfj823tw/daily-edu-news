"""
Main news crawler script for collecting global education news
"""

import requests
import json
import feedparser
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.get_log_file()),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsCollector:
    """Collect education news from multiple sources"""
    
    def __init__(self):
        self.news_items = []
        self.sources = Config.load_sources()
    
    def collect_all(self):
        """Collect news from all sources"""
        logger.info("Starting news collection...")
        
        # Collect from RSS feeds
        self.collect_from_rss()
        
        # Collect from NewsAPI if key is provided
        if Config.NEWS_API_KEY:
            self.collect_from_newsapi()
        
        # Filter and rank news
        self.filter_and_rank()
        
        logger.info(f"Collected {len(self.news_items)} news items")
        return self.news_items
    
    def collect_from_rss(self):
        """Collect news from RSS feeds"""
        logger.info("Collecting from RSS feeds...")
        
        rss_feeds = self.sources.get('rss_feeds', [])
        
        for feed_config in rss_feeds:
            try:
                logger.info(f"Fetching RSS: {feed_config['name']}")
                feed = feedparser.parse(feed_config['url'])
                
                for entry in feed.entries[:Config.NEWS_PER_QUERY]:
                    article = {
                        'title': entry.get('title', 'No title'),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'source': feed_config['name'],
                        'category': feed_config.get('category', 'General'),
                        'published': entry.get('published', datetime.now().isoformat()),
                        'type': 'rss'
                    }
                    
                    # Clean summary
                    article['summary'] = self.clean_text(article['summary'])
                    
                    if self.validate_article(article):
                        self.news_items.append(article)
                
            except Exception as e:
                logger.warning(f"Error fetching RSS {feed_config['name']}: {e}")
        
        logger.info(f"Collected {len(self.news_items)} items from RSS")
    
    def collect_from_newsapi(self):
        """Collect news from NewsAPI"""
        logger.info("Collecting from NewsAPI...")
        
        base_url = "https://newsapi.org/v2/everything"
        queries = self.sources.get('news_api_queries', [])
        
        for query_config in queries:
            try:
                params = {
                    'q': query_config['q'],
                    'sortBy': query_config.get('sortBy', 'publishedAt'),
                    'pageSize': Config.NEWS_PER_QUERY,
                    'language': 'en',
                    'apiKey': Config.NEWS_API_KEY
                }
                
                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for article in data.get('articles', [])[:Config.NEWS_PER_QUERY]:
                    news_item = {
                        'title': article.get('title', 'No title'),
                        'link': article.get('url', ''),
                        'summary': article.get('description', ''),
                        'content': article.get('content', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'category': 'News',
                        'published': article.get('publishedAt', datetime.now().isoformat()),
                        'image': article.get('urlToImage', ''),
                        'type': 'newsapi'
                    }
                    
                    if self.validate_article(news_item):
                        self.news_items.append(news_item)
                
                logger.info(f"Collected from query '{query_config['q']}'")
                
            except Exception as e:
                logger.warning(f"Error fetching NewsAPI query '{query_config['q']}': {e}")
    
    def validate_article(self, article):
        """Validate article has required fields and minimum length"""
        required_fields = ['title', 'link']
        
        if not all(article.get(field) for field in required_fields):
            return False
        
        text_length = len(article.get('summary', '') + article.get('content', ''))
        if text_length < Config.MIN_ARTICLE_LENGTH:
            return False
        
        return True
    
    def clean_text(self, text):
        """Clean HTML and extra whitespace from text"""
        if not text:
            return ""
        
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        # Truncate to reasonable length
        max_length = 300
        if len(text) > max_length:
            text = text[:max_length] + '...'
        
        return text
    
    def filter_and_rank(self):
        """Filter duplicates and rank by relevance"""
        logger.info("Filtering and ranking news...")
        
        # Remove duplicates by title
        seen_titles = set()
        unique_items = []
        
        for item in self.news_items:
            title_lower = item['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_items.append(item)
        
        # Sort by published date (newest first)
        self.news_items = sorted(
            unique_items,
            key=lambda x: x.get('published', ''),
            reverse=True
        )
        
        # Keep only top MAX_TOTAL_NEWS items
        self.news_items = self.news_items[:Config.MAX_TOTAL_NEWS]
        
        logger.info(f"After filtering: {len(self.news_items)} items")
    
    def save_to_file(self, filename=None):
        """Save collected news to JSON file"""
        if not filename:
            filename = f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = Config.DATA_DIR / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.news_items, f, ensure_ascii=False, indent=2)
            logger.info(f"News saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving news to file: {e}")
            return None

def main():
    """Main entry point"""
    try:
        logger.info("=" * 50)
        logger.info("Daily Education News Crawler Started")
        logger.info("=" * 50)
        
        collector = NewsCollector()
        news_items = collector.collect_all()
        
        # Save to file for email sending
        collector.save_to_file('today_news.json')
        
        logger.info(f"Successfully collected {len(news_items)} news items")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Fatal error in news crawler: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
