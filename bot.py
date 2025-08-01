import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from fastapi import FastAPI, Request
from telegram.ext import ApplicationBuilder
from datetime import datetime, timedelta
import sqlite3
import asyncio
import uvicorn

# --- Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Config ---
BOT_TOKEN = "7950712207:AAHMIek-JXLy6fLrQMBHk-2hzFXdY1d0HG8"
WEBHOOK_URL = "https://your-app-name.onrender.com/webhook"  # Change this!
CHECK_CHANNEL_ID = -1001441974665
CHANNEL_LINK = "https://t.me/dailyearn11"
BONUS_AMOUNT = 1
REFERRAL_REWARD = 5
WITHDRAW_THRESHOLD = 50
DB_NAME = 'bot_data.db'

# --- FastAPI App ---
app = FastAPI()
application = None  # Global Application object

# ---- Your database & bot logic functions go here ----
# (paste everything from your previous message including: init_db, get_user_data, etc.)

# ⬇️ Keep all handlers (start, handle_buttons, etc.) as you already wrote them.

@app.on_event("startup")
async def startup():
    global application
    init_db()
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_buttons))

    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logging.info("Webhook set and bot initialized.")

@app.post("/webhook")
async def process_webhook(req: Request):
    update = Update.de_json(await req.json(), application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}
