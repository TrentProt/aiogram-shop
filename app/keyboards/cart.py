from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.models import Product


async def choose_qty(product_id: int, is_edit: bool = False):
    keyboard = InlineKeyboardBuilder()
    for i in range(1,10):
        keyboard.add(
            InlineKeyboardButton(
                text=str(i),
                callback_data=f'update_qty_{i}_product_{product_id}' if is_edit
                else f'write_qty_{i}_product_{product_id}'
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
            callback_data=f'update_qty_0_{product_id}' if is_edit
            else f'write_qty_0_product_{product_id}'
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text='ГОТОВО',
            callback_data=f'replace_qty_in_cart_product_{product_id}' if is_edit
            else f'add_qty_in_cart_product_{product_id}'
        )
    )
    return keyboard.adjust(3).as_markup()


async def check_cart(cart_items: [Product, int]):
    keyboard = InlineKeyboardBuilder()

    total_value = 0

    for product, qty in cart_items:
        keyboard.row(
            InlineKeyboardButton(
                text=f'{product.name}',
                callback_data=f'product'
            ),
            InlineKeyboardButton(
                text=f'Кол-во: {qty}',
                callback_data=f'product'
            ),
            InlineKeyboardButton(
                text=f'Цена: {product.price * qty}',
                callback_data=f'product'
            )
        )
        keyboard.row(
            InlineKeyboardButton(
                text=f'Удалить товар',
                callback_data=f'delete_product_{product.id}'
            ),
            InlineKeyboardButton(
                text=f'Изменить кол-во',
                callback_data=f'edit_product_{product.id}'
            )
        )
        total_value += product.price * qty
    keyboard.row(
        InlineKeyboardButton(
            text=f'Всего: {total_value}',
            callback_data=f'product'
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=f'Оформить заказ',
            callback_data=f'create_order'
        )
    )

    return keyboard.as_markup()
