#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для инициализации Git и загрузки изменений в GitHub
"""
import os
import subprocess
import sys

# Переходим в директорию проекта
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
print(f"Working directory: {project_dir}")

# Проверяем, инициализирован ли Git
if not os.path.exists('.git'):
    print("Инициализируем Git репозиторий...")
    subprocess.run(['git', 'init'], check=True)
    print("✓ Git репозиторий инициализирован")

# Проверяем remote
result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
if 'origin' not in result.stdout:
    print("Добавляем remote origin...")
    subprocess.run([
        'git', 'remote', 'add', 'origin',
        'https://github.com/larik7lolik/telegram-ai-bot.git'
    ], check=True)
    print("✓ Remote origin добавлен")
else:
    print("✓ Remote origin уже настроен")

# Добавляем все файлы (кроме тех, что в .gitignore)
print("\nДобавляем файлы в Git...")
subprocess.run(['git', 'add', 'requirements.txt', 'scheduler.py', 'Dockerfile'], check=True)
subprocess.run(['git', 'add', '.'], check=True)
print("✓ Файлы добавлены")

# Коммитим изменения
print("\nСоздаем коммит...")
subprocess.run([
    'git', 'commit', '-m',
    'Fix: Add schedule module to requirements.txt and update scheduler.py'
], check=True)
print("✓ Коммит создан")

# Пушим в GitHub
print("\nЗагружаем изменения в GitHub...")
try:
    subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
    print("✓ Изменения загружены в GitHub!")
except subprocess.CalledProcessError:
    # Если master не существует, пробуем main
    try:
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        print("✓ Изменения загружены в GitHub (ветка main)!")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Ошибка при push: {e}")
        print("Попробуйте запушить вручную: git push -u origin master (или main)")

print("\n✅ Готово! Теперь можно развернуть проект на Koyeb заново.")
