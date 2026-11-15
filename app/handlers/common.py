from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.config import settings

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer("Привіт!")


@router.message(F.from_user.id.in_(settings.admin_ids), Command("ping"))
async def command_ping_handler(message: Message):
    await message.answer("pong")


@router.message(F.from_user.id.in_(settings.admin_ids), Command("boom"))
async def command_boom_handler(message: Message):
    raise RuntimeError("Boom!")