import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.logging_setup import setup_logging
#from app.db.session import async_session   TODO
#from app.middlewares.db import DbSessionMiddleware TODO

TOKEN = settings.bot_token

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    # dp.include_router()    TODO
    # dp.update.outer_middleware(DbSessionMiddleware(session_pool=async_session))    TODO

    # scheduler = build_scheduler(bot)  TODO додасться на етапі 8
    # scheduler.start() TODO

    setup_logging()
    # dp.errors.register(on_error)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())