"""
Email sending module for daily news report
"""

import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from config import Config
from email_template import EmailTemplate

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

class EmailSender:
    """Send email with daily news report"""
    
    def __init__(self):
        self.sender_email = Config.SENDER_EMAIL
        self.sender_password = Config.EMAIL_PASSWORD
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
    
    def load_news(self, news_file='today_news.json'):
        """Load news from JSON file"""
        filepath = Config.DATA_DIR / news_file
        
        if not filepath.exists():
            logger.warning(f"News file not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                news_items = json.load(f)
            logger.info(f"Loaded {len(news_items)} news items from {filepath}")
            return news_items
        except Exception as e:
            logger.error(f"Error loading news file: {e}")
            return []
    
    def send(self, recipient_email, news_items):
        """Send email with news report"""
        
        if not news_items:
            logger.warning("No news items to send")
            return False
        
        try:
            # Generate HTML content
            html_content = EmailTemplate.generate(news_items)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = Config.EMAIL_SUBJECT
            msg['From'] = f"{Config.EMAIL_FROM_NAME} <{self.sender_email}>"
            msg['To'] = recipient_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            logger.info(f"Connecting to {self.smtp_server}:{self.smtp_port}...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                logger.info("SMTP connection established and TLS enabled")
                
                server.login(self.sender_email, self.sender_password)
                logger.info(f"Logged in as {self.sender_email}")
                
                server.send_message(msg)
                logger.info(f"Email sent successfully to {recipient_email}")
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {e}")
            logger.error("Check your email and password/app password")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return False
    
    def send_report(self):
        """Send daily report to configured recipient"""
        
        try:
            # Validate configuration
            if not Config.EMAIL_RECIPIENT:
                raise ValueError("EMAIL_RECIPIENT not configured")
            
            logger.info("=" * 50)
            logger.info("Email Sender Started")
            logger.info("=" * 50)
            
            # Load news
            news_items = self.load_news()
            
            if not news_items:
                logger.warning("No news items to send")
                return False
            
            # Send email
            success = self.send(Config.EMAIL_RECIPIENT, news_items)
            
            if success:
                logger.info(f"Report sent to {Config.EMAIL_RECIPIENT}")
            else:
                logger.error("Failed to send report")
            
            logger.info("=" * 50)
            return success
            
        except Exception as e:
            logger.error(f"Fatal error in email sender: {e}", exc_info=True)
            return False

def main():
    """Main entry point"""
    sender = EmailSender()
    sender.send_report()

if __name__ == '__main__':
    main()
