import logging import sqlite3 import asyncio from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup from telegram.ext import ( Application, CommandHandler, CallbackQueryHandler, ContextTypes, ApplicationBuilder )

from fastapi import FastAPI, Request import uvicorn

--- Logging ---

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO )

--- Config ---

BOT_TOKEN = "7950712207:AAHMIek-JXLy6fLrQMBHk-2hzFXdY1d0HG8" WEBHOOK_URL = "https://refer-to-earn-bot.onrender.com/webhook"  # Replace with actual Render URL CHECK_CHANNEL_ID = -1001441974665 CHANNEL_LINK = "https://t.me/dailyearn11" BONUS_AMOUNT = 1 REFERRAL_REWARD = 5 WITHDRAW_THRESHOLD = 50 DB_NAME = 'bot_data.db'

--- FastAPI App ---

app = FastAPI() application = None

--- Database Functions ---

def init_db(): with sqlite3.connect(DB_NAME) as conn: cursor = conn.cursor() cursor.execute(''' CREATE TABLE IF NOT EXISTS users ( user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, last_bonus TEXT, ref_by INTEGER ) ''') conn.commit()

def get_user_data(user_id: int): with sqlite3.connect(DB_NAME) as conn: conn.row_factory = sqlite3.Row cursor = conn.cursor() cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) user_row = cursor.fetchone()

if user_row:
        user_data = dict(user_row)
        if user_data['last_bonus']:
            user_data['last_bonus'] = datetime.fromisoformat(user_data['last_bonus'])
        else:
            user_data['last_bonus'] = None

        cursor.execute('SELECT COUNT(*) FROM users WHERE ref_by = ?', (user_id,))
        user_data['referral_count'] = cursor.fetchone()[0]
        return user_data
    return None

def create_user(user_id: int, ref_by: int = None): with sqlite3.connect(DB_NAME) as conn: cursor = conn.cursor() cursor.execute('INSERT INTO users (user_id, balance, last_bonus, ref_by) VALUES (?, ?, ?, ?)', (user_id, 0, None, ref_by)) conn.commit()

def update_user_balance(user_id: int, new_balance: float): with sqlite3.connect(DB_NAME) as conn: cursor = conn.cursor() cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id)) conn.commit()

def update_user_last_bonus(user_id: int, last_bonus_time: datetime): with sqlite3.connect(DB_NAME) as conn: cursor = conn.cursor() cursor.execute('UPDATE users SET last_bonus = ? WHERE user_id = ?', (last_bonus_time.isoformat(), user_id)) conn.commit()

--- Startup ---

@app.on_event("startup") async def startup(): global application init_db() application = ( ApplicationBuilder() .token(BOT_TOKEN) .build() ) application.add_handler(CommandHandler("start", start)) application.add_handler(CallbackQueryHandler(handle_buttons))

await application.initialize()
await application.bot.set_webhook(url=WEBHOOK_URL)
logging.info("Webhook set and bot initialized.")

--- Webhook Endpoint ---

@app.post("/webhook") async def process_webhook(req: Request): update = Update.de_json(await req.json(), application.bot) await application.update_queue.put(update) return {"status": "ok"}

--- Root Test ---

@app.get("/") async def root(): return {"message": "🤖 Bot is alive!"}

--- Main (for local test only) ---

if name == "main": uvicorn.run("bot:app", host="0.0.0.0", port=10000, reload=True)

