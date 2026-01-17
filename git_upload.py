# -*- coding: utf-8 -*-
import os
import subprocess
import sys

# Определяем путь к проекту
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("=" * 50)
print("Загрузка проекта в GitHub")
print("=" * 50)
print(f"Рабочая директория: {os.getcwd()}")
print()

# Проверяем Git
try:
    result = subprocess.run(['git', '--version'], capture_output=True, text=True, encoding='utf-8')
    print(f"✓ Git установлен: {result.stdout.strip()}")
except FileNotFoundError:
    print("✗ ОШИБКА: Git не установлен!")
    sys.exit(1)

# Инициализируем репозиторий, если нужно
if not os.path.exists('.git'):
    print("\nИнициализируем Git репозиторий...")
    subprocess.run(['git', 'init'], check=True, encoding='utf-8')
    print("✓ Git репозиторий инициализирован")

# Проверяем remote
result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True, encoding='utf-8')
if 'origin' not in result.stdout:
    print("\nДобавляем remote origin...")
    subprocess.run([
        'git', 'remote', 'add', 'origin',
        'https://github.com/larik7lolik/telegram-ai-bot.git'
    ], check=True, encoding='utf-8')
    print("✓ Remote origin добавлен")
else:
    print("\n✓ Remote origin уже настроен")

# Добавляем файлы
print("\nДобавляем файлы в Git...")
subprocess.run(['git', 'add', 'requirements.txt'], check=True, encoding='utf-8')
subprocess.run(['git', 'add', 'scheduler.py'], check=True, encoding='utf-8')
subprocess.run(['git', 'add', 'Dockerfile'], check=True, encoding='utf-8')
subprocess.run(['git', 'add', '.'], check=True, encoding='utf-8')
print("✓ Файлы добавлены")

# Коммитим
print("\nСоздаем коммит...")
try:
    subprocess.run([
        'git', 'commit', '-m',
        'Fix: Add schedule module to requirements.txt and update scheduler.py'
    ], check=True, encoding='utf-8')
    print("✓ Коммит создан")
except subprocess.CalledProcessError as e:
    if "nothing to commit" in str(e.stdout) if hasattr(e, 'stdout') else "":
        print("⚠ Нет изменений для коммита (возможно, уже закоммичено)")
    else:
        print(f"⚠ Ошибка при коммите: {e}")

# Пушим
print("\nЗагружаем в GitHub...")
try:
    subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True, encoding='utf-8')
    print("✓ Изменения загружены в GitHub (ветка master)!")
except subprocess.CalledProcessError:
    try:
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True, encoding='utf-8')
        print("✓ Изменения загружены в GitHub (ветка main)!")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Ошибка при push: {e}")
        print("\nПопробуйте выполнить вручную:")
        print("  git push -u origin master")
        print("  или")
        print("  git push -u origin main")

print("\n" + "=" * 50)
print("Готово! Теперь можно развернуть проект на Koyeb заново.")
print("=" * 50)
