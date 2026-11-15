import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.logging_setup import setup_logging, on_error
#from app.db.session import async_session   TODO
#from app.middlewares.db import DbSessionMiddleware TODO

from app.handlers.common import router as common_router

async def main() -> None:
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(common_router)
    #dp.update.outer_middleware(DbSessionMiddleware(session_pool=async_session))    TODO

    #scheduler = build_scheduler(bot)  TODO додасться на етапі 8
    #scheduler.start() TODO

    setup_logging()
    dp.errors.register(on_error)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())