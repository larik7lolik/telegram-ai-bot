import sys
import os
from generators.text_gen import TextGenerator
from generators.image_gen import ImageGenerator
from publishers.telegram_pub import TelegramPublisher
from utils.logger import setup_logger
from config import Config

logger = setup_logger()

def run_automation(theme=None):
    """
    Main workflow: 
    1. Pick content from CSV (random or by theme)
    2. Use text from CSV or generate via YandexGPT
    3. Generate image prompt (Qwen via SiliconFlow)
    4. Generate image (FLUX.1 via SiliconFlow)
    5. Publish to Telegram
    """
    logger.info("Starting automated content generation cycle...")
    
    # 1. Initialize generators and publisher
    text_gen = TextGenerator()
    image_gen = ImageGenerator()
    telegram_pub = TelegramPublisher()
    
    try:
        # 2. Get content data from CSV
        if theme:
            logger.info(f"Searching for post with theme: {theme}")
            post_data = text_gen.get_post_by_theme(theme)
            if not post_data:
                logger.warning(f"Theme '{theme}' not found in content plan. Falling back to random.")
                post_data = text_gen.get_random_post_data()
        else:
            post_data = text_gen.get_random_post_data()

        if post_data:
            logger.info(f"Selected post topic: {post_data.get('Тема', 'Unknown')}")
        else:
            logger.warning("No content plan found, using default theme.")

        # 3. Generate Caption (now uses text from CSV if possible) and Image Prompt
        logger.info("Preparing caption and image prompt...")
        caption = text_gen.generate_caption(post_data)
        image_prompt = text_gen.generate_image_prompt(post_data)
        
        # Safely log caption (avoid emoji issues in some consoles)
        try:
            logger.info(f"Final Caption: {caption[:100]}...")
        except:
            logger.info("Final Caption: [Contains characters that cannot be displayed in console]")
        
        logger.info(f"Generated Image Prompt: {image_prompt}")
        
        # 4. Generate Image
        logger.info("Generating image via SiliconFlow (FLUX.1)...")
        image_path = "story_image.png"
        image_gen.generate_image(image_prompt, image_path)
        
        if not os.path.exists(image_path):
            logger.error("Failed to generate image file.")
            return

        # 5. Publish to Telegram
        logger.info("Publishing to Telegram...")
        success = telegram_pub.publish_story(image_path, caption)
        
        if success:
            logger.info("Successfully published content to Telegram!")
        else:
            logger.error("Failed to publish content.")
            
        # Clean up
        if os.path.exists(image_path):
            os.remove(image_path)
            
    except Exception as e:
        logger.error(f"An error occurred during the automation cycle: {e}")

if __name__ == "__main__":
    # Check if a theme was passed as an argument
    requested_theme = sys.argv[1] if len(sys.argv) > 1 else None
    run_automation(requested_theme)
