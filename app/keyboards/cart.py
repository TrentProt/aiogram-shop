from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def choose_qty(product_id: int):
    keyboard = InlineKeyboardBuilder()
    for i in range(1,10):
        keyboard.add(
            InlineKeyboardButton(
                text=str(i),
                callback_data=f'write_qty_{i}_product_{product_id}'
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text='CLEAR',
            callback_data=f'add_to_cart_{product_id}'
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text='0',
            callback_data=f'write_qty_0_product_{product_id}'
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text='ГОТОВО',
            callback_data=f'add_qty_in_cart_product_{product_id}'
        )
    )
    return keyboard.adjust(3).as_markup()