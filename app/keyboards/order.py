from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

choose_deltype = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Курьером', callback_data='delivery_courier'
            )
        ],
        [
            InlineKeyboardButton(
                text='Самовывоз', callback_data='delivery_pickup'
            )
        ],
        [
            InlineKeyboardButton(
                text='Экспресс', callback_data='delivery_express'
            )
        ]
    ]
)