import requests
import time
from config import Config
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class TelegramPublisher:
    def __init__(self):
        # Clean token from whitespace and potential 'bot' prefix
        token = Config.TELEGRAM_BOT_TOKEN
        if token:
            token = token.strip()
            if token.lower().startswith("bot"):
                token = token[3:]
        self.bot_token = token
        self.chat_id = Config.TELEGRAM_CHAT_ID.strip() if Config.TELEGRAM_CHAT_ID else None
        
        # Set up a session with automatic retries for common server errors
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

    def publish_story(self, image_path, caption):
        """
        Publishes a standard photo post to a Telegram channel with retries and timeout.
        """
        if not self.bot_token:
            print("Error: TELEGRAM_BOT_TOKEN is not set.")
            return False
            
        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
        
        # Manual retries for connection issues (like 10054 Connection Reset)
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                with open(image_path, 'rb') as image_file:
                    files = {
                        'photo': image_file
                    }
                    data = {
                        'chat_id': str(self.chat_id),
                        'caption': caption,
                        'parse_mode': 'HTML'
                    }
                    
                    # Increased timeout to 90s for potentially slow uploads/network
                    response = self.session.post(url, data=data, files=files, timeout=90)
                    result = response.json()
                    
                    if not result.get("ok"):
                        print(f"Failed to send post (Attempt {attempt + 1}): {result}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        return False
                    
                    print(f"Post published successfully: {result.get('result', {}).get('message_id')}")
                    return True
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"Network error (10054 or Timeout) on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Telegram might be unstable or your network is blocking the connection.")
            except Exception as e:
                print(f"Unexpected error publishing to Telegram: {e}")
                return False
                
        return False
