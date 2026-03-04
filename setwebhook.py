import os
import asyncio
from dotenv import load_dotenv
from aiogram.methods.set_webhook import SetWebhook
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = os.getenv("webhook_path")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

async def set_webhook():
    result = await bot(SetWebhook(url=URL))
    print("Webhook set:", result)

asyncio.run(set_webhook())