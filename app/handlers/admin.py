from aiogram import Router, F
from aiogram.types import Message

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User, Role, Order
from app.utils.utils import check_admin

router = Router()

@router.message(F.text == 'Заказы')
async def get_orders(
        message: Message,
        session: AsyncSession
):
    is_admin = check_admin(message, session)

    if is_admin:
        stmt_orders = select(Order)
        orders = (await session.execute(stmt_orders)).scalars().all()
        text = ''
        for order in orders:
            text += (f'UUID: {order.uuid}\n'
                     f'TG_ID: {order.user_id}\n'
                     f'Status: {order.status.value}\n'
                     f'Total: {order.total_amount} руб.\n\n')
        await message.answer(text)

    else:
        await message.answer('У вас нету прав')