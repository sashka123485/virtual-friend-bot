@echo off
chcp 65001 >nul
title Virtual Friend Telegram Bot

cd /d "%~dp0"

echo ========================================
echo       VIRTUAL FRIEND TELEGRAM BOT
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Создаю виртуальное окружение...
    py -m venv .venv
    if errorlevel 1 (
        echo Не удалось создать Python-окружение.
        pause
        exit /b 1
    )
)

echo [2/3] Устанавливаю зависимости...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Не удалось установить зависимости.
    pause
    exit /b 1
)

if not exist ".env" (
    copy /Y ".env.example" ".env" >nul
    echo.
    echo Создан .env. Заполни в нем TELEGRAM_BOT_TOKEN и GEMINI_API_KEY.
    pause
    exit /b 0
)

echo [3/3] Запускаю локальный polling-режим...
".venv\Scripts\python.exe" bot.py

echo.
echo Бот остановлен.
pause
