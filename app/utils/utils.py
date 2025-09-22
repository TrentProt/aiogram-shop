from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User, Role


async def check_admin(
        message: Message,
        session: AsyncSession
):
    stmt = select(User).where(
        User.telegram_id == message.from_user.id
    )
    result = (await session.execute(stmt)).scalar_one_or_none()

    if not result:
        is_admin = False
        return is_admin

    is_admin = (result.role == Role.admin)
    return is_admin