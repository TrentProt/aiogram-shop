import re

from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.keyboards.cart as kb
import app.keyboards.catalog as kb_cat

from app.core.models import Product, Cart

router = Router()


@router.callback_query(F.data.startswith('add_to_cart_'))
async def cq_add_to_cart(callback: CallbackQuery):
    await callback.answer('')

    product_id = callback.data.split('cart_')[1]
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=callback.message.photo[-1].file_id,
            caption='Выберите количество товара'
        ),
        reply_markup=await kb.choose_qty(int(product_id))
    )


@router.callback_query(F.data.startswith('write_qty_'))
async def cq_add_qty(callback: CallbackQuery,
                     session: AsyncSession):
    await callback.answer('')

    data = callback.data.split('_')
    qty, product_id = data[2], data[4]
    stmt = select(Product).where(
        Product.id == product_id
    )
    product = (await session.execute(stmt)).scalar()

    if 'Добавить' in callback.message.caption:
        old = callback.message.caption
        old_qty = re.search(r'\((\d+)\)', old).group(1)
        concat = old_qty + qty
        new_qty = int(concat.replace('in', ''))

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=callback.message.photo[-1].file_id,
                caption=f'Добавить в корзину ({new_qty}) шт.\n\n'
                        f'Стоимость: {product.price * new_qty}'
            ),
            reply_markup=await kb.choose_qty(int(product_id))
        )

    else:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=callback.message.photo[-1].file_id,
                caption=f'Добавить в корзину ({qty}) шт.\n\n'
                        f'Стоимость: {product.price * int(qty)}'
            ),
            reply_markup=await kb.choose_qty(int(product_id))
        )


@router.callback_query(F.data.startswith('add_qty_in_cart_product_'))
async def cq_add_qty_pr_in_cart(callback: CallbackQuery,
                                session: AsyncSession):
    await callback.answer('Товар добавлен в корзину!')

    user_id = callback.from_user.id

    caption_w_qty = callback.message.caption
    qty = int(re.search(r'\((\d+)\)', caption_w_qty).group(1))

    product_id = int(callback.data.split('product_')[1])

    await callback.message.delete()

    new_cart = Cart(
        user_id=user_id,
        product_id=product_id,
        qty=qty
    )
    session.add(new_cart)
    await session.commit()

    await callback.message.answer(
        'Выберите категорию',
        reply_markup=await kb_cat.inline_category(session)
    )


@router.message(F.text == 'Корзина')
async def get_cart(message: Message,
                   session: AsyncSession):
    stmt = select(Product, Cart.qty).join(
        Cart, Cart.product_id == Product.id
    ).where(
        Cart.user_id == message.from_user.id
    )
    result = await session.execute(stmt)
    cart_items = result.all()

    if not cart_items:
        await message.answer('Ваша корзина пуста')
        return

    await message.answer(
        'Ваша корзина',
        reply_markup=await kb.check_cart(cart_items)
    )

