import asyncio
import logging
from bot import bot, dispatcher
from handlers import start

logging.basicConfig(level=logging.INFO)

async def main():
    print("Запуск бота...")
    start.register_handlers(dispatcher)

    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
