import asyncio
import logging
from app.bot import bot, dispatcher
from app.handlers import start, message

logging.basicConfig(level=logging.INFO)

async def main():
    print("Запуск бота...")
    start.register_handlers(dispatcher)
    message.register_handlers(dispatcher)

    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
