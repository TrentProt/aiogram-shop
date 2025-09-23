from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.models import Status


async def edit_status_keyboard(order_uuid: str):
    keyboard = InlineKeyboardBuilder()

    statuses = [
        ('Создан', Status.created.value),
        ('Оплачен', Status.paid_for.value),
        ('Завершен', Status.completed.value),
        ('В процессе', Status.in_process.value),
        ('Остановлен', Status.stopped.value)
    ]

    for text, status in statuses:
        keyboard.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"status_{order_uuid}_{status}"
            )
        )
    return keyboard.adjust(2).as_markup()
