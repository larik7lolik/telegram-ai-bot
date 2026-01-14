import schedule
import time
import subprocess
import sys
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from utils.logger import setup_logger

logger = setup_logger()

# Простой HTTP-сервер для health checks от Koyeb
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Отключаем логирование HTTP-запросов
        pass

def start_health_server(port=8000):
    """Запускает HTTP-сервер для health checks в отдельном потоке"""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server started on port {port}")
    server.serve_forever()

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
    
    # Запускаем health check сервер в отдельном потоке
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    logger.info("Health check server thread started")
    
    # Первый запуск при старте (необязательно, но полезно для проверки)
    # job() 
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Проверяем каждую минуту
