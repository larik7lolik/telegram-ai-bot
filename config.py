from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    PROXYAPI_OPENAI_KEY = os.getenv("PROXYAPI_OPENAI_KEY")
    # API Keys & Auth
    # YandexGPT Settings
    YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
    YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
    
    # Yandex Art (Image Generation)
    # Available from Russia, no VPN needed. Uses same auth as YandexGPT.
    #YANDEX_ART_MODEL_URI = f"art://{os.getenv('YANDEX_FOLDER_ID')}/yandex-art/latest"
    

    # Telegram Settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Content Settings
    CONTENT_THEME = os.getenv("CONTENT_THEME", "Маркетолог-вайбкодер, онлайн-школы, AI-автоматизация")
    CONTENT_PLAN_PATH = os.getenv("CONTENT_PLAN_PATH", "Контент план.csv")
    
    # Marketing Persona
    MARKETING_PERSONA = (
        "Ты — классный маркетолог-вайбкодер. Ты создаёшь сайты и воронки продаж под онлайн-школы и экспертов "
        "с помощью AI (Cursor), где ИИ остаётся внутренним инструментом, а клиент покупает результат: "
        "больше заявок и автоматизацию рутины. У тебя уже есть серьёзные технические кейсы: аналитика, "
        "PDF-отчёты, ассистенты, Telegram-сбор и суммаризация, воронка для репетитора французского. "
        "Твой стиль: спокойный, экспертный, ориентированный на результат, без лишнего хайпа вокруг ИИ."
    )
    
    # Image Generation Settings (9:16)
    IMAGE_WIDTH = 1024
    IMAGE_HEIGHT = 1024 
    # Requests SSL verification (set SSL_VERIFY=0 to disable)
    SSL_VERIFY = os.getenv("SSL_VERIFY", "1").strip().lower() in ("1", "true", "yes")