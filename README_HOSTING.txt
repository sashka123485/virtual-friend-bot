VIRTUAL FRIEND TELEGRAM BOT — FREE HOSTING
==========================================

Этот вариант подготовлен для бесплатного Render Web Service.

Почему Web Service:
Render предоставляет бесплатные Web Service для Python, а Telegram
может отправлять сообщения боту через HTTPS webhook.

ВАЖНО ПРО БЕСПЛАТНЫЙ RENDER
---------------------------
Бесплатный Web Service может автоматически засыпать после периода
неактивности и просыпаться примерно за минуту после нового HTTP-запроса.

Локальные файлы на Free Service не являются постоянными.
Поэтому SQLite-файл dialogues.sqlite3 может потеряться после перезапуска,
redeploy или sleep.

Для тестов и небольшого личного бота это нормально.
Если нужна постоянная память, подключи внешнюю PostgreSQL-базу и
перенеси таблицу messages туда.

ДЕПЛОЙ НА RENDER
----------------

1. Создай GitHub-репозиторий.

2. Загрузите в него все файлы этого проекта.
   НЕ загружай .env с реальными ключами.

3. Открой Render и выбери:
   New -> Web Service.

4. Подключи GitHub-репозиторий.

5. Укажи:
   Build Command:
   pip install -r requirements.txt

   Start Command:
   gunicorn server:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT

   Plan:
   Free

6. После создания сервиса открой:
   Environment.

   Добавь:
   TELEGRAM_BOT_TOKEN = твой токен Telegram
   GEMINI_API_KEY = твой Gemini API Key
   GEMINI_MODEL = gemini-2.5-flash

7. После первого деплоя Render выдаст адрес вида:
   https://название.onrender.com

8. Добавь переменную:
   RENDER_EXTERNAL_URL = https://название.onrender.com

9. WEBHOOK_SECRET:
   Можно создать любую длинную случайную строку.
   Если используешь render.yaml, Render может сгенерировать её автоматически.

10. Нажми Deploy / Redeploy.

11. Открой:
   https://название.onrender.com/health

   Должно появиться:
   {"status":"healthy"}

12. Напиши своему боту /start.

КАК РАБОТАЕТ
------------
Telegram
   ↓
HTTPS webhook
   ↓
Render FastAPI
   ↓
Gemini API
   ↓
ответ
   ↓
Telegram

ЛОКАЛЬНЫЙ ЗАПУСК
----------------
Можно по-прежнему запускать проект на Windows двойным кликом
по start.bat.

Для локального запуска используется polling, а на Render —
webhook.

СЕКРЕТЫ
-------
Никогда не помещай реальные ключи в GitHub.

Используй Environment Variables Render:
TELEGRAM_BOT_TOKEN
GEMINI_API_KEY
WEBHOOK_SECRET

КОМАНДЫ
-------
/start
/help
/clear
/about

СТРУКТУРА
---------
bot.py              Telegram + Gemini
server.py           FastAPI webhook для Render
database.py         SQLite-память
prompt.py           системный промт
requirements.txt    зависимости
render.yaml         конфигурация Render
.env.example        пример локальных настроек
start.bat            запуск Windows
README_HOSTING.txt   инструкция хостинга
