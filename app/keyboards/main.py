from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def main_kb(
        is_admin: bool = False
):
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        KeyboardButton(
            text='Каталог'
        )
    )
    keyboard.row(
        KeyboardButton(
            text='Корзина'
        )
    )
    if is_admin:
        keyboard.row(
            KeyboardButton(
                text='Заказы'
            ),
            KeyboardButton(
                text='Изменить статусы заказа'
            ),
        )
        keyboard.row(
            KeyboardButton(
                text='Добавление товаров'
            ),
            KeyboardButton(
                text='Изменение товаров'
            ),
        )
    return keyboard.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню'
    )
