#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawler import NewsCrawler
from src.email_sender import EmailSender
import os

def main():
    """主程序 - 爬取新聞並發送郵件"""
    
    print("=" * 50)
    print("📚 Daily Education News - 日報生成器")
    print("=" * 50)
    
    # 檢查必需的環境變數
    if not os.getenv('EMAIL_RECIPIENT') or not os.getenv('EMAIL_PASSWORD'):
        print("❌ 錯誤: 缺少必需的環境變數 (EMAIL_RECIPIENT 或 EMAIL_PASSWORD)")
        print("   請在 GitHub Secrets 中配置這些變數")
        return False
    
    try:
        # 爬取新聞
        print("\n[1/2] 正在爬取教育新聞...")
        crawler = NewsCrawler()
        news_list = crawler.crawl_education_news()
        
        if not news_list:
            print("❌ 未能爬取任何新聞")
            return False
        
        # 發送郵件
        print("\n[2/2] 正在發送郵件...")
        sender = EmailSender()
        success = sender.send_news_digest(news_list)
        
        if success:
            print("\n✅ 日報生成並發送成功！")
            print(f"   📧 收件人: {os.getenv('EMAIL_RECIPIENT')}")
            print(f"   📰 新聞數: {len(news_list)}")
            return True
        else:
            print("\n❌ 郵件發送失敗")
            return False
            
    except Exception as e:
        print(f"\n❌ 發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    print("\n" + "=" * 50)
    sys.exit(0 if success else 1)
