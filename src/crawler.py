import feedparser
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import os

class NewsCrawler:
    def __init__(self):
        self.news_sources = self._load_sources()
        self.news_list = []
    
    def _load_sources(self):
        """載入新聞來源配置"""
        try:
            with open('data/sources.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"rss_sources": [], "keywords": []}
    
    def crawl_education_news(self):
        """爬取教育新聞"""
        print("🔍 開始爬取教育新聞...")
        
        # 爬取RSS源
        for source in self.news_sources.get('rss_sources', []):
            self._crawl_rss(source)
        
        # 爬取NewsAPI (如果提供了密鑰)
        news_api_key = os.getenv('NEWS_API_KEY')
        if news_api_key:
            self._crawl_newsapi(news_api_key)
        
        # 排序和篩選
        self._sort_and_filter()
        
        print(f"✅ 成功爬取 {len(self.news_list)} 條新聞")
        return self.news_list[:10]  # 返回前10條
    
    def _crawl_rss(self, source):
        """爬取RSS源"""
        try:
            print(f"  📡 正在爬取 {source['name']}...")
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries[:5]:  # 每個源取5條
                news_item = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'source': source['name'],
                    'category': source.get('category', 'practice'),
                    'published': self._parse_date(entry.get('published', '')),
                    'summary': self._get_summary(entry),
                }
                if news_item['title']:
                    self.news_list.append(news_item)
        except Exception as e:
            print(f"  ⚠️ 爬取 {source['name']} 失敗: {str(e)}")
    
    def _crawl_newsapi(self, api_key):
        """從NewsAPI爬取新聞"""
        try:
            print(f"  📡 正在從NewsAPI爬取新聞...")
            headers = {'Authorization': api_key}
            keywords = ' OR '.join(self.news_sources.get('keywords', ['education']))
            
            url = f"https://newsapi.org/v2/everything?q={keywords}&sortBy=publishedAt&language=en&pageSize=10"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                for article in articles[:5]:
                    news_item = {
                        'title': article.get('title', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'NewsAPI'),
                        'category': 'research',
                        'published': article.get('publishedAt', ''),
                        'summary': article.get('description', ''),
                    }
                    if news_item['title']:
                        self.news_list.append(news_item)
        except Exception as e:
            print(f"  ⚠️ NewsAPI 爬取失敗: {str(e)}")
    
    def _get_summary(self, entry):
        """提取摘要"""
        if hasattr(entry, 'summary'):
            soup = BeautifulSoup(entry.summary, 'html.parser')
            text = soup.get_text()
            return text[:150] if text else "點擊鏈接查看詳情"
        return "點擊鏈接查看詳情"
    
    def _parse_date(self, date_str):
        """解析日期"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now()
    
    def _sort_and_filter(self):
        """排序和去重"""
        # 去重
        seen_urls = set()
        unique_news = []
        for news in self.news_list:
            if news['url'] not in seen_urls:
                seen_urls.add(news['url'])
                unique_news.append(news)
        
        # 按發布時間排序 (最新優先)
        self.news_list = sorted(
            unique_news,
            key=lambda x: x.get('published', datetime.min),
            reverse=True
        )

if __name__ == '__main__':
    crawler = NewsCrawler()
    news = crawler.crawl_education_news()
    for idx, item in enumerate(news, 1):
        print(f"{idx}. {item['title']}")
        print(f"   來源: {item['source']}")
        print(f"   鏈接: {item['url']}\n")
