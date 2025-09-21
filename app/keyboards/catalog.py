import math

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Category, Product


async def inline_category(session: AsyncSession):
    keyboard = InlineKeyboardBuilder()
    stmt = select(Category)
    categories = (await session.execute(stmt)).scalars().all()

    for category in categories:
        keyboard.add(
            InlineKeyboardButton(
                text=category.name,
                callback_data=f"category_{category.id}"
            )
        )

    return keyboard.adjust(2).as_markup()


async def inline_items_category(
        category_id: int,
        session: AsyncSession,
        page: int = 0,
        items_per_page: int = 2):
    keyboard = InlineKeyboardBuilder()

    total_stmt = select(Product).where(
        Product.category_id == category_id
    )
    total_products = (await session.execute(total_stmt)).scalars().all()
    total_pages = math.ceil(len(total_products) / items_per_page)

    stmt = select(Product).where(
        Product.category_id == category_id
    ).offset(page * items_per_page).limit(items_per_page)
    products = (await session.execute(stmt)).scalars().all()

    for product in products:
        keyboard.add(
            InlineKeyboardButton(
                text=product.name,
                callback_data=f"product_{product.id}"
            )
        )

    pagination_buttons = []

    if page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="<- Назад",
                callback_data=f"page_{category_id}_{page - 1}"
            )
        )

    pagination_buttons.append(
        InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data="current_page"
        )
    )

    if page < total_pages - 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Вперед ->",
                callback_data=f"page_{category_id}_{page + 1}"
            )
        )

    keyboard.adjust(2)

    keyboard.row(*pagination_buttons)

    keyboard.row(
        InlineKeyboardButton(
            text="<-- Назад к категориям",
            callback_data="back_to_categories"
        )
    )

    return keyboard.as_markup()


async def inside_product(category_id: int,
                         product_id: int):
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(
            text='Добавить в корзину',
            callback_data=f'add_to_cart_{product_id}'
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text='<-- Назад к списку',
            callback_data=f'category_{category_id}'
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text='<-- Назад к категориям',
            callback_data='back_to_categories'
        )
    )

    return keyboard.as_markup()
