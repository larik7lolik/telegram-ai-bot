import requests
import os
import time
import base64
from config import Config
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class ImageGenerator:
    def __init__(self):
        self.api_key = Config.SILICON_FLOW_API_KEY
        self.url = "https://api.siliconflow.cn/v1/images/generations"
        self.model = Config.SILICON_FLOW_IMAGE_MODEL
        
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

    def generate_image(self, prompt, output_path="generated_story.png"):
        """
        Generates a vertical image using SiliconFlow (FLUX.1).
        """
        if not self.api_key:
            raise ValueError("SILICON_FLOW_API_KEY is not set")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # SiliconFlow FLUX.1 parameters
        payload = {
            "model": self.model,
            "prompt": prompt,
            "image_size": "768x1344", # Vertical 9:16 approx for FLUX
            "batch_size": 1,
            "num_inference_steps": 20,
            "guidance_scale": 7.5
        }

        # 1. Start generation
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.post(self.url, headers=headers, json=payload, timeout=90)
                if response.status_code != 200:
                    raise Exception(f"SiliconFlow Art error: {response.text}")
                
                result = response.json()
                image_url = result["data"][0]["url"]
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error in SiliconFlow (Attempt {attempt + 1}), retrying... {e}")
                    time.sleep(5)
                    continue
                raise e

        # 2. Download the image
        img_response = self.session.get(image_url, timeout=60)
        if img_response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(img_response.content)
        else:
            raise Exception(f"Failed to download image from {image_url}")
        
        return output_path
