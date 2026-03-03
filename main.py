import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import F
from openai import OpenAI
from aiogram.fsm.storage.memory import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())
load_dotenv()

TOKEN = os.getenv("TOKEN")
LLM_TOKEN = os.getenv("LLM_TOKEN")
HISTORY_MAX_LENGTH = 5000
client = OpenAI(api_key=LLM_TOKEN, base_url="https://api.deepseek.com")

with open("prompt.txt", "r") as f:
    init_message = f.read()

with open("system_prompt.txt", "r") as f:
    system_prompt = f.read()

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(init_message)

@dp.message(Command("newchat"))
async def reset_history(message: Message, state: FSMContext) -> None:
    state.clear()
    await message.answer("История была очищена! Можно начинать общение заново!")

@dp.message(F.text & ~F.text.startswith('/'))
async def llm_caller(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    history = data.get("history", "")
    history += f"Student message: {message.text}\n\n"
    if len(history) > HISTORY_MAX_LENGTH:
        history = history[-5000:]
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": history},
    ],
    stream=False
    )
    answer_text = response.choices[0].message.content
    history += f"Bot message: {answer_text}"
    await state.update_data(history=history)
    await message.answer(answer_text)

async def main() -> None:
    bot = Bot(token=TOKEN, 
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    asyncio.run(main())