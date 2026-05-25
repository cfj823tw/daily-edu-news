"""
Email template generation for daily news report
"""

from datetime import datetime
from jinja2 import Template

class EmailTemplate:
    """Generate HTML email template for news report"""
    
    TEMPLATE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }
        
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 3px solid #4CAF50;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #4CAF50;
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .header p {
            color: #999;
            font-size: 14px;
        }
        
        .news-list {
            list-style: none;
            margin: 20px 0;
        }
        
        .news-item {
            margin-bottom: 25px;
            padding-bottom: 25px;
            border-bottom: 1px solid #eee;
        }
        
        .news-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        
        .news-number {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            font-weight: bold;
            margin-right: 10px;
            font-size: 14px;
        }
        
        .news-title {
            display: inline-block;
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        
        .news-title a {
            color: #4CAF50;
            text-decoration: none;
        }
        
        .news-title a:hover {
            text-decoration: underline;
        }
        
        .news-meta {
            font-size: 12px;
            color: #999;
            margin: 8px 0;
        }
        
        .news-category {
            display: inline-block;
            background-color: #e8f5e9;
            color: #2e7d32;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 10px;
        }
        
        .news-source {
            display: inline-block;
            background-color: #e3f2fd;
            color: #1565c0;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
        }
        
        .news-summary {
            color: #666;
            font-size: 14px;
            line-height: 1.6;
            margin: 10px 0;
        }
        
        .read-more {
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .read-more:hover {
            background-color: #45a049;
        }
        
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #999;
            font-size: 12px;
        }
        
        .footer p {
            margin-bottom: 10px;
        }
        
        .divider {
            height: 1px;
            background-color: #eee;
            margin: 30px 0;
        }
        
        .stats {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
            font-size: 12px;
            color: #666;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Daily Education News</h1>
            <p>{{ date }}</p>
        </div>
        
        <div class="stats">
            <p>Today's Top {{ count }} Education News from Global Sources</p>
        </div>
        
        {% if news_items %}
        <ul class="news-list">
            {% for item in news_items %}
            <li class="news-item">
                <span class="news-number">{{ loop.index }}</span>
                <div class="news-title">
                    <a href="{{ item.link }}" target="_blank">{{ item.title }}</a>
                </div>
                
                <div class="news-meta">
                    <span class="news-category">{{ item.category }}</span>
                    <span class="news-source">{{ item.source }}</span>
                    {% if item.published %}
                    <span>{{ format_date(item.published) }}</span>
                    {% endif %}
                </div>
                
                {% if item.summary %}
                <p class="news-summary">{{ item.summary }}</p>
                {% endif %}
                
                <a href="{{ item.link }}" target="_blank" class="read-more">Read Full Article →</a>
            </li>
            {% endfor %}
        </ul>
        {% else %}
        <p style="text-align: center; color: #999; padding: 30px 0;">
            No news items available today. Please check back tomorrow.
        </p>
        {% endif %}
        
        <div class="footer">
            <div class="divider"></div>
            <p>📧 This is an automated email from <strong>Daily Education News</strong></p>
            <p>Sent: {{ now }} (UTC)</p>
            <p>
                <a href="#" style="color: #4CAF50; text-decoration: none;">Unsubscribe</a> | 
                <a href="#" style="color: #4CAF50; text-decoration: none;">Manage Preferences</a>
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    @staticmethod
    def format_date(date_str):
        """Format date string to readable format"""
        try:
            # Try parsing various date formats
            from dateutil import parser
            dt = parser.parse(date_str)
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return date_str
    
    @staticmethod
    def generate(news_items):
        """Generate HTML email from news items"""
        
        template = Template(EmailTemplate.TEMPLATE_HTML)
        
        html_content = template.render(
            news_items=news_items,
            count=len(news_items),
            date=datetime.now().strftime('%A, %B %d, %Y'),
            now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            format_date=EmailTemplate.format_date
        )
        
        return html_content
