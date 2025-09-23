from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.models import User, Role


async def check_admin(
        message: Message,
        session: AsyncSession
):
    stmt = select(User).where(
        User.telegram_id == message.from_user.id
    )
    result = (await session.execute(stmt)).scalar_one_or_none()

    is_admin = False

    if not result:
        print(f'{settings.admins.tg_ids} iii')
        if message.from_user.id in settings.admins.tg_ids:
            new_user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                role=Role.admin
            )
            is_admin = True
        else:
            new_user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
            )
        session.add(new_user)
        await session.commit()
    else:
        is_admin = (result.role == Role.admin)
    return is_admin