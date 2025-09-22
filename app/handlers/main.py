from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

import app.keyboards.main as kb
from app.utils.utils import check_admin

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    is_admin = await check_admin(message, session)

    await message.answer(
        f'Привет, {message.from_user.first_name}!\nЭто тестовый бот!',
        reply_markup=await kb.main_kb(is_admin)
    )