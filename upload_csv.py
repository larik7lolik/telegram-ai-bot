# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import io

# Настраиваем кодировку вывода для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Находим директорию проекта
desktop = r'C:\Users\user\Desktop'
dirs = [x for x in os.listdir(desktop) if os.path.isdir(os.path.join(desktop, x))]
proj_dir = next((os.path.join(desktop, x) for x in dirs if os.path.exists(os.path.join(desktop, x, 'scheduler.py'))), None)

if not proj_dir:
    print("Проект не найден!")
    sys.exit(1)

os.chdir(proj_dir)
print(f"Рабочая директория: {os.getcwd()}")
print()

# Проверяем статус
print("Проверяем статус Git...")
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
print()

# Добавляем файл
print("Добавляем файл 'Контент план.csv'...")
result = subprocess.run(['git', 'add', 'Контент план.csv'], capture_output=True, text=True, encoding='utf-8')
if result.returncode != 0:
    print(f"Ошибка при добавлении: {result.stderr}")
    sys.exit(1)
print("[OK] Файл добавлен")
print()

# Коммитим
print("Создаем коммит...")
result = subprocess.run(['git', 'commit', '-m', 'Update content plan with new posts (Week 5-6)'], 
                       capture_output=True, text=True, encoding='utf-8')
if result.returncode != 0:
    if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
        print("⚠ Нет изменений для коммита (возможно, уже закоммичено)")
    else:
        print(f"Ошибка при коммите: {result.stderr}")
        sys.exit(1)
else:
    print("[OK] Коммит создан")
print()

# Пушим
print("Загружаем в GitHub...")
result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True, encoding='utf-8')
if result.returncode != 0:
    # Пробуем master
    result = subprocess.run(['git', 'push', 'origin', 'master'], capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"Ошибка при push: {result.stderr}")
        sys.exit(1)
    else:
        print("[OK] Изменения загружены в GitHub (ветка master)!")
else:
    print("[OK] Изменения загружены в GitHub (ветка main)!")

print()
print("[OK] Готово! Файл загружен в GitHub.")
