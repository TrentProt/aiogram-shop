from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User
import app.keyboards.main as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    stmt = select(User).where(
        User.telegram_id == message.from_user.id
    )
    result = (await session.execute(stmt)).scalar_one_or_none()

    if not result:
        new_user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )
        session.add(new_user)
        await session.commit()

    await message.answer(
        f'Привет, {message.from_user.first_name}!\nЭто тестовый бот!',
        reply_markup=kb.main
    )