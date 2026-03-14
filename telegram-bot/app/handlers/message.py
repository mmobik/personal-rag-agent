from aiogram import types

async def cmd_message(message: types.Message):
    text = message.text or "(не текст)"
    await message.answer("Вы написали: " + text)

def register_handlers(dp):
    dp.message.register(cmd_message)
