import base64
import requests
import urllib3
from config import Config


class ImageGenerator:
    def __init__(self):
        self.api_key = Config.PROXYAPI_OPENAI_KEY
        self.url = "https://api.proxyapi.ru/openai/v1/images/generations"
        # Можешь вынести в Config, если захочешь менять из .env
        self.model = "gpt-image-1"
        if not Config.SSL_VERIFY:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def generate_image(self, prompt: str, output_path: str = "story_image.png") -> str:
        """
        Генерирует вертикальное изображение через GPT-Image 1 (ProxyAPI).
        Возвращает путь к сохранённому файлу.
        """
        if not self.api_key:
            raise ValueError("PROXYAPI_OPENAI_KEY is not set")

        prompt = (prompt or "").strip()
        if not prompt:
            raise ValueError("Image prompt is empty")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            # Вертикальный формат для сторис
            "size": "1024x1536",
            # Баланс качество/скорость
            "quality": "medium",
            # Удобно сразу PNG
            "output_format": "png",
        }

        resp = requests.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=120,
            verify=Config.SSL_VERIFY,
        )
        if resp.status_code != 200:
            raise Exception(f"GPT-Image error: {resp.status_code} {resp.text}")

        data = resp.json()

        # Для gpt-image-1 ProxyAPI возвращает base64 в поле b64_json
        try:
            image_b64 = data["data"][0]["b64_json"]
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected GPT-Image response: {data}") from e

        img_bytes = base64.b64decode(image_b64)

        with open(output_path, "wb") as f:
            f.write(img_bytes)

        return output_path
