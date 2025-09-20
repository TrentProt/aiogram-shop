from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton)

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Каталог')],
        [KeyboardButton(text='Корзина')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт'
)