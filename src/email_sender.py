import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailSender:
    def __init__(self):
        # 使用 .strip() 確保變數前後沒有隱藏的空格或換行符號
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com').strip()
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        # 🟢 修正 1：將 SENDER_EMAIL 改為與 YAML 一致的 EMAIL_ADDRESS
        self.sender_email = os.getenv('EMAIL_ADDRESS', '').strip()
        self.sender_password = os.getenv('EMAIL_PASSWORD', '').strip()
        self.recipient_email = os.getenv('EMAIL_RECIPIENT', '').strip()
    
    def send_news_digest(self, news_list):
        """
        發送新聞日報
        :param news_list: 新聞列表 [{'title': '', 'url': '', 'source': '', 'category': ''}]
        """
        try:
            html_content = self._generate_html(news_list)
            
            message = MIMEMultipart('alternative')
            message['Subject'] = f"📚 教育新知日報 - {datetime.now().strftime('%Y年%m月%d日')}"
            message['From'] = self.sender_email
            message['To'] = self.recipient_email
            
            text_part = MIMEText("請使用支持HTML的郵件客戶端查看此郵件", 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            message.attach(text_part)
            message.attach(html_part)
            
            print(f"📡 正在連線至郵件伺服器 {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                # 🟢 修正 2：加入完整的 Gmail TLS 安全加密連線握手步驟
                server.ehlo()          # 第一次握手
                server.starttls()      # 啟動加密
                server.ehlo()          # 🟢 加密後的第二次握手（Gmail 規定，缺少會噴 334 錯誤）
                
                print(f"🔑 正在嘗試登入帳號: {self.sender_email}...")
                server.login(self.sender_email, self.sender_password)
                print("🔓 郵件伺服器登入成功！正在發送郵件...")
                
                server.send_message(message)
            
            print(f"✅ 郵件已成功發送至 {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ 郵件發送失敗: {str(e)}")
            return False
    
    def _generate_html(self, news_list):
        """生成HTML郵件內容"""
        today = datetime.now().strftime('%Y年%m月%d日')
        
        news_html = ""
        for idx, news in enumerate(news_list[:10], 1):  # 只取前10條
            category_emoji = {
                'research': '🔬',
                'edtech': '💡',
                'higher_ed': '🎓',
                'policy': '📋',
                'practice': '🛠️'
            }.get(news.get('category', '').lower(), '📌') # 轉小寫比對更安全
            
            news_html += f"""
            <tr>
                <td style="padding: 15px; border-bottom: 1px solid #eee;">
                    <p style="margin: 0 0 10px 0; color: #666; font-size: 12px;">
                        {idx}. {category_emoji} {news.get('source', '未知來源')}
                    </p>
                    <h3 style="margin: 5px 0 10px 0; color: #333; font-size: 15px;">
                        <a href="{news.get('url', '#')}" style="color: #0066cc; text-decoration: none;">
                            {news.get('title', '無標題')}
                        </a>
                    </h3>
                    <p style="margin: 0; color: #666; font-size: 13px; line-height: 1.6;">
                        {news.get('summary', '點擊鏈接查看詳情')}
                    </p>
                </td>
            </tr>
            """
        
        html_template = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .header p {{ margin: 10px 0 0 0; font-size: 14px; opacity: 0.9; }}
                table {{ width: 100%; border-collapse: collapse; background-color: white; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #999; background-color: #f0f0f0; border-radius: 0 0 8px 8px; }}
                a {{ color: #0066cc; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📚 全球教育新知日報</h1>
                    <p>{today}</p>
                </div>
                <table>
                    {news_html}
                </table>
                <div class="footer">
                    <p>本日報由 Daily Education News 自動生成</p>
                    <p>如有問題，請聯繫系統管理員</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
