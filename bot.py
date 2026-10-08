import logging
import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
from google import genai
from google.genai import types

from database import init_db, get_history, add_message, clear_history
from prompt import SYSTEM_PROMPT

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Не указан TELEGRAM_BOT_TOKEN.")
if not GEMINI_API_KEY:
    raise RuntimeError("Не указан GEMINI_API_KEY.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "bot.log", encoding="utf-8")
    ],
)
logger = logging.getLogger("virtual_friend")

client = genai.Client(api_key=GEMINI_API_KEY)


def build_contents(history):
    return [
        types.Content(
            role=role,
            parts=[types.Part.from_text(text=text)]
        )
        for role, text in history
    ]


async def ask_gemini(user_id: int, user_text: str) -> str:
    history = get_history(user_id)[-40:]
    contents = build_contents(history)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_text)]
        )
    )

    response = await asyncio.to_thread(
        client.models.generate_content,
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.8,
            max_output_tokens=2048,
        ),
    )

    answer = (response.text or "").strip()
    if not answer:
        raise RuntimeError("Gemini вернул пустой ответ.")

    add_message(user_id, "user", user_text)
    add_message(user_id, "model", answer)
    return answer


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋 Я твой виртуальный друг и ИИ-помощник.\n\n"
        "Можешь просто написать мне что угодно: поговорить, попросить совет, "
        "разобраться с программированием или просто поболтать.\n\n"
        "Команды:\n"
        "/help — возможности\n"
        "/clear — очистить историю\n"
        "/about — информация о боте"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Что я умею:\n\n"
        "• общаться как виртуальный друг;\n"
        "• помогать с программированием и сайтами;\n"
        "• обсуждать игры и Minecraft;\n"
        "• помогать с техническими проблемами;\n"
        "• поддерживать, когда тебе грустно или тревожно;\n"
        "• помнить текущий диалог.\n\n"
        "/clear — начать диалог заново."
    )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_history(update.effective_user.id)
    await update.message.reply_text(
        "🧹 Готово! Историю твоего диалога очистил 🙂"
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💙 Виртуальный друг\n\n"
        "ИИ-бот на Python + Telegram + Gemini.\n"
        "У каждого Telegram-пользователя отдельная история."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id
    user_text = (update.message.text or "").strip()
    if not user_text:
        return

    try:
        await update.message.chat.send_action(ChatAction.TYPING)
        answer = await ask_gemini(user_id, user_text)
        await update.message.reply_text(answer)
    except Exception:
        logger.exception("Ошибка обработки сообщения пользователя %s", user_id)
        await update.message.reply_text(
            "Ой, у меня сейчас небольшая техническая проблема 😅\n"
            "Попробуй отправить сообщение ещё раз через несколько секунд."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Ошибка Telegram: %s", context.error)


def build_application() -> Application:
    init_db()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)
    return application


def main():
    application = build_application()
    logger.info("Локальный режим polling: запуск...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
