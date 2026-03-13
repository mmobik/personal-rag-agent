from aiogram import types
from aiogram.filters import Command

async def cmd_start(message: types.Message):
    await message.answer("Привет, я цифровой ассистент")

def register_handlers(dp):
    dp.message.register(cmd_start, Command(commands=["start","help"]))
