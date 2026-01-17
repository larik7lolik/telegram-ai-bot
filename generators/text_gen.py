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

        # HTTP session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

        # Load content plan from CSV
        self.content_plan = self._load_content_plan()

    # ---------- Загрузка контент-плана из CSV ----------

    def _load_content_plan(self):
        plan = []
        file_path = Config.CONTENT_PLAN_PATH

        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), Config.CONTENT_PLAN_PATH)

        if os.path.exists(file_path):
            try:
                # Пробуем UTF-8, если не получается — cp1251
                try:
                    with open(file_path, mode="r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(file_path, mode="r", encoding="cp1251") as f:
                        content = f.read()

                # Перебираем возможные разделители
                for delimiter in [None, ";", "\t", ","]:
                    plan = []
                    f = io.StringIO(content.strip())

                    if delimiter:
                        reader = csv.reader(f, delimiter=delimiter)
                    else:
                        try:
                            dialect = csv.Sniffer().sniff(content[:2000])
                            f.seek(0)
                            reader = csv.reader(f, dialect)
                        except Exception:
                            f.seek(0)
                            reader = csv.reader(f)

                    headers = next(reader, None)

                    for row in reader:
                        if not row:
                            continue

                        # Ожидаемый формат: минимум 7 колонок
                        if len(row) >= 7:
                            plan.append(
                                {
                                    "Тема": row[3].strip(),
                                    "Идея_картинки": row[5].strip(),
                                    "Текст_поста": row[6].strip(),
                                }
                            )
                        # Случай: всё в одной колонке, разделённой пробелами/табами
                        elif len(row) == 1:
                            line = row[0]
                            parts = re.split(r" {2,}|\t", line)
                            if len(parts) >= 7:
                                plan.append(
                                    {
                                        "Тема": parts[3].strip(),
                                        "Идея_картинки": parts[5].strip(),
                                        "Текст_поста": parts[6].strip(),
                                    }
                                )

                    if plan:
                        break
            except Exception as e:
                print(f"Error loading CSV: {e}")

        return plan

    # ---------- Вспомогательные методы ----------

    def _generate_yandex(self, system_text: str, user_text: str) -> str:
        if not self.yandex_api_key or not self.yandex_folder_id:
            raise ValueError("YANDEX_API_KEY or YANDEX_FOLDER_ID is not set")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.yandex_api_key}",
        }

        payload = {
            "modelUri": f"gpt://{self.yandex_folder_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "1000",
            },
            "messages": [
                {"role": "system", "text": system_text},
                {"role": "user", "text": user_text},
            ],
        }

        response = self.session.post(
            self.yandex_url, headers=headers, json=payload, timeout=60
        )
        if response.status_code != 200:
            raise Exception(f"YandexGPT error: {response.text}")

        return response.json()["result"]["alternatives"][0]["message"]["text"]

    # ---------- Работа с контент-планом ----------

    def get_random_post_data(self):
        if not self.content_plan:
            return None
        return random.choice(self.content_plan)

    def get_post_by_theme(self, theme: str):
        if not self.content_plan or not theme:
            return None

        theme_lower = theme.lower()
        for post in self.content_plan:
            if theme_lower in post.get("Тема", "").lower():
                return post
        return None

    # ---------- Генерация текста поста ----------

    def generate_caption(self, post_data: dict | None) -> str:
        """
        Использует текст из CSV. Если его нет — генерирует через YandexGPT.
        """
        if post_data and post_data.get("Текст_поста"):
            return post_data.get("Текст_поста").strip().strip('"')

        # Fallback на YandexGPT, если в CSV пусто
        system_text = Config.MARKETING_PERSONA
        user_text = (
            "Напиши экспертный, понятный, мотивирующий пост для Telegram про AI-маркетинг. "
            "До 100 слов, без воды, с конкретной пользой для владельца онлайн-школы."
        )

        try:
            return self._generate_yandex(system_text, user_text).strip().strip('"')
        except Exception:
            # Последний запасной вариант, если YandexGPT недоступен
            return (
                "Автоматизирую воронки и контент, чтобы вы могли спокойно масштабировать "
                "онлайн-школу и сосредоточиться на продукте. 🚀"
            )

    # ---------- Генерация промпта для картинки ----------

    def generate_image_prompt(self, post_data: dict | None) -> str:
        """
        Генерирует промт для картинки (ориентируемся на твой стиль, но без Qwen).
        """
        theme = post_data.get("Тема", "").lower() if post_data else ""

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

        # Базовая идея из контент-плана
        idea = (
            post_data.get("Идея_картинки", "Professional marketing workspace")
            if post_data
            else "Professional marketing workspace"
        )

        # Формируем английский промпт вручную, без внешних моделей
        base_prompt = (
            f"A vertical 9:16 image of {idea}. "
            f"Premium, minimalist, cinematic aesthetic, high contrast lighting, "
            f"professional photography, 8k, highly detailed."
        )

        return base_prompt
