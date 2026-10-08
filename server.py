import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from telegram import Update

from bot import build_application

logger = logging.getLogger("virtual_friend.web")

telegram_app = build_application()
webhook_secret = os.getenv("WEBHOOK_SECRET", "").strip()
external_url = os.getenv("RENDER_EXTERNAL_URL", "").strip().rstrip("/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_app.initialize()
    await telegram_app.start()

    if not external_url:
        logger.warning(
            "RENDER_EXTERNAL_URL не задан. Webhook автоматически не установлен."
        )
    else:
        webhook_url = f"{external_url}/telegram/webhook"
        await telegram_app.bot.set_webhook(
            url=webhook_url,
            secret_token=webhook_secret or None,
            drop_pending_updates=True,
        )
        logger.info("Telegram webhook установлен: %s", webhook_url)

    yield

    await telegram_app.stop()
    await telegram_app.shutdown()


app = FastAPI(title="Virtual Friend Telegram Bot")


@app.get("/")
async def root():
    return {"status": "ok", "service": "virtual-friend-telegram-bot"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if webhook_secret:
        incoming = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if incoming != webhook_secret:
            raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
