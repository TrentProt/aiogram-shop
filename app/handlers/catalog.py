from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Product
import app.keyboards.catalog as kb


router = Router()


@router.message(F.text == 'Каталог')
async def h_catalog(message: Message, session: AsyncSession):
    await message.answer(
        'Выберите категорию',
        reply_markup= await kb.inline_category(session)
    )


@router.callback_query(F.data.startswith('category_'))
async def cq_items_category(callback: CallbackQuery, session: AsyncSession):
    category_id = int(callback.data.split('_')[1])
    await callback.answer('')

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            'Продукты в выбранной категории',
            reply_markup=await kb.inline_items_category(category_id, session)
        )

    else:
        await callback.message.edit_text(
            'Продукты в выбранной категории',
            reply_markup=await kb.inline_items_category(category_id, session)
        )


@router.callback_query(F.data.startswith('page_'))
async def cq_pagination(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    category_id = int(data_parts[1])
    page = int(data_parts[2])

    await callback.answer('')
    await callback.message.edit_text(
        'Продукты в выбранной категории',
        reply_markup=await kb.inline_items_category(category_id, session, page)
    )


@router.callback_query(F.data == 'back_to_categories')
async def cq_back_to_categories(callback: CallbackQuery, session: AsyncSession):
    await callback.answer('')
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            'Выберите категорию',
            reply_markup=await kb.inline_category(session)
        )
    else:
        await callback.message.edit_text(
            'Выберите категорию',
            reply_markup=await kb.inline_category(session)
        )


@router.callback_query(F.data == 'current_page')
async def cq_current_page(callback: CallbackQuery):
    await callback.answer('Текущая страница')


@router.callback_query(F.data.startswith('product_'))
async def cq_get_product(callback: CallbackQuery,
                         session: AsyncSession):
    product_id = callback.data.split('_')[1]
    stmt = select(Product).where(
        Product.id == product_id
    )
    product = (await session.execute(stmt)).scalar()

    media = InputMediaPhoto(
        media=str(product.photo),
        caption=f'{product.name}\n{product.description}\nЦена: {product.price}₽'
    )

    await callback.message.edit_media(
        media=media,
        reply_markup=await kb.inside_product(int(product.category_id))
    )
