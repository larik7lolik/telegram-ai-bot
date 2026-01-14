import schedule
import time
import subprocess
import sys
import os
from utils.logger import setup_logger

logger = setup_logger()

def job():
    logger.info("--- STARTING SCHEDULED POST ---")
    try:
        # Запускаем основной скрипт бота
        # Мы вызываем его как отдельный процесс, чтобы он каждый раз инициализировался заново
        result = subprocess.run([sys.executable, "main.py"], check=True)
        logger.info("--- SCHEDULED POST FINISHED SUCCESSFULLY ---")
    except Exception as e:
        logger.error(f"Error during scheduled job: {e}")

# НАСТРОЙКА РАСПИСАНИЯ
# Вы можете настроить время (по UTC или вашему локальному)
schedule.every().day.at("11:00").do(job)  # Утренний пост
schedule.every().day.at("21:00").do(job)  # Вечерний пост

if __name__ == "__main__":
    logger.info("Scheduler started. Waiting for scheduled times...")
    # Первый запуск при старте (необязательно, но полезно для проверки)
    # job() 
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Проверяем каждую минуту
