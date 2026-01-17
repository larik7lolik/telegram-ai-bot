@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ====================================
echo Загрузка проекта в GitHub
echo ====================================
echo.

echo Проверяем Git...
git --version
if errorlevel 1 (
    echo ОШИБКА: Git не установлен!
    pause
    exit /b 1
)

echo.
echo Инициализируем репозиторий (если нужно)...
if not exist .git (
    git init
)

echo.
echo Проверяем remote...
git remote -v | findstr origin >nul
if errorlevel 1 (
    echo Добавляем remote origin...
    git remote add origin https://github.com/larik7lolik/telegram-ai-bot.git
) else (
    echo Remote origin уже настроен
)

echo.
echo Добавляем файлы...
git add requirements.txt
git add scheduler.py
git add Dockerfile
git add .

echo.
echo Создаем коммит...
git commit -m "Fix: Add schedule module to requirements.txt and update scheduler.py"

echo.
echo Загружаем в GitHub...
git push -u origin master
if errorlevel 1 (
    echo Пробуем ветку main...
    git push -u origin main
)

echo.
echo ====================================
echo Готово! Теперь можно развернуть на Koyeb
echo ====================================
pause
