import requests
import csv
import random
import os
import re
import io
from config import Config
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class TextGenerator:
    def __init__(self):
        # Yandex Settings
        self.yandex_api_key = Config.YANDEX_API_KEY
        self.yandex_folder_id = Config.YANDEX_FOLDER_ID
        self.yandex_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        
        # SiliconFlow (Qwen) Settings
        self.sf_api_key = Config.SILICON_FLOW_API_KEY
        self.sf_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.sf_model = Config.SILICON_FLOW_TEXT_MODEL
        
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        self.content_plan = self._load_content_plan()

    def _load_content_plan(self):
        plan = []
        file_path = Config.CONTENT_PLAN_PATH
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), Config.CONTENT_PLAN_PATH)

        if os.path.exists(file_path):
            try:
                try:
                    with open(file_path, mode='r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(file_path, mode='r', encoding='cp1251') as f:
                        content = f.read()

                for delimiter in [None, ';', '\t', ',']:
                    plan = []
                    f = io.StringIO(content.strip())
                    if delimiter:
                        reader = csv.reader(f, delimiter=delimiter)
                    else:
                        try:
                            dialect = csv.Sniffer().sniff(content[:2000])
                            f.seek(0)
                            reader = csv.reader(f, dialect)
                        except:
                            f.seek(0)
                            reader = csv.reader(f)
                    
                    headers = next(reader, None)
                    for row in reader:
                        if not row: continue
                        if len(row) >= 7:
                            plan.append({
                                'Тема': row[3].strip(),
                                'Идея_картинки': row[5].strip(),
                                'Текст_поста': row[6].strip()
                            })
                        elif len(row) == 1:
                            line = row[0]
                            parts = re.split(r' {2,}|\t', line)
                            if len(parts) >= 7:
                                plan.append({
                                    'Тема': parts[3].strip(),
                                    'Идея_картинки': parts[5].strip(),
                                    'Текст_поста': parts[6].strip()
                                })
                    
                    if plan: break
            except Exception as e:
                print(f"Error loading CSV: {e}")
        return plan

    def _generate_yandex(self, system_text, user_text):
        if not self.yandex_api_key or not self.yandex_folder_id:
            raise ValueError("YANDEX_API_KEY or YANDEX_FOLDER_ID is not set")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.yandex_api_key}"
        }

        payload = {
            "modelUri": f"gpt://{self.yandex_folder_id}/yandexgpt-lite",
            "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": "1000"},
            "messages": [
                {"role": "system", "text": system_text},
                {"role": "user", "text": user_text}
            ]
        }

        response = self.session.post(self.yandex_url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            raise Exception(f"YandexGPT error: {response.text}")
        
        return response.json()["result"]["alternatives"][0]["message"]["text"]

    def _generate_qwen(self, system_text, user_text):
        if not self.sf_api_key:
            raise ValueError("SILICON_FLOW_API_KEY is not set")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.sf_api_key}"
        }

        payload = {
            "model": self.sf_model,
            "messages": [
                {"role": "system", "content": system_text},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        response = self.session.post(self.sf_url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            raise Exception(f"SiliconFlow (Qwen) error: {response.text}")
        
        return response.json()["choices"][0]["message"]["content"]

    def get_random_post_data(self):
        if not self.content_plan:
            return None
        return random.choice(self.content_plan)

    def get_post_by_theme(self, theme):
        if not self.content_plan:
            return None
        for post in self.content_plan:
            if theme.lower() in post.get('Тема', '').lower():
                return post
        return None

    def generate_caption(self, post_data):
        """
        Использует текст из CSV. Если его нет — генерирует через Yandex.
        """
        if post_data and post_data.get('Текст_поста'):
            return post_data.get('Текст_поста').strip().strip('"')
        
        # Fallback на YandexGPT, если в CSV пусто
        system_text = Config.MARKETING_PERSONA
        user_text = "Напиши экспертный пост для Telegram про AI-маркетинг. До 100 слов."
        try:
            return self._generate_yandex(system_text, user_text).strip().strip('"')
        except Exception as e:
            return "Автоматизирую воронки, чтобы вы могли спокойно масштабировать свой проект. 🚀"

    def generate_image_prompt(self, post_data):
        """
        Генерирует промт для картинки через Qwen (SiliconFlow).
        """
        theme = post_data.get('Тема', '').lower() if post_data else ""
        
        # Специальный эталонный промт для темы "Знакомство"
        if "знакомство" in theme:
            return (
                "Photorealistic, 8k resolution. A professional young woman with brown hair, "
                "wearing a stylish beige blazer, sitting at a grey desk in a modern bright office. "
                "She is working on a laptop displaying a colorful sales funnel chart. "
                "Above the laptop, a magical floating open book with a graduation cap. "
                "Ethereal glowing light trails and network nodes connecting the laptop and the book. "
                "Cinematic lighting, soft bokeh background, premium marketing vibe, highly detailed."
            )

        system_text = (
            "You are a world-class AI digital artist. Style: 'Vibe Coder' - premium, minimalist, sophisticated. "
            "Create English prompts for FLUX.1. Focus on cinematic lighting, professional photography, 8k."
        )
        
        idea = post_data.get('Идея_картинки', "Professional marketing workspace") if post_data else "Professional marketing workspace"
        
        user_text = (
            f"Create a premium image prompt for FLUX.1 based on: '{idea}'. "
            f"Style: Cinematic, professional photography, high contrast. "
            f"Vertical 9:16 layout. English only, under 400 characters."
        )
        
        try:
            # Используем Qwen для создания промта
            prompt = self._generate_qwen(system_text, user_text).strip().strip('"')
            return f"{prompt}, photorealistic, cinematic lighting, 8k, highly detailed, premium aesthetic"
        except Exception as e:
            # Fallback на Yandex, если SiliconFlow недоступен
            try:
                prompt = self._generate_yandex(system_text, user_text).strip().strip('"')
                return f"{prompt}, photorealistic, cinematic lighting, 8k"
            except:
                return "Professional aesthetic workspace, cinematic lighting, 8k, premium marketing vibe"
