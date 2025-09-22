import enum

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.models import Cart, Order, OrderItem
import app.keyboards.main as kb_main
import app.keyboards.order as kb
from app.utils.utils import check_admin

router = Router()


DELIVERYTYPE = {
    'courier': 'Курьером',
    'pickup': 'Самовывоз',
    'express': 'Экспресс'
}


class CreateOrder(StatesGroup):
    name = State()
    number = State()
    delivery_type = State()
    address = State()


@router.callback_query(F.data == 'create_order')
async def name_add(
        callback: CallbackQuery,
        state: FSMContext
):
    await callback.answer('')
    await state.set_state(CreateOrder.name)
    await callback.message.answer('Введите свое имя:')


@router.message(CreateOrder.name)
async def process_name(
        message: Message,
        state: FSMContext
):
    await state.update_data(name=message.text)
    await state.set_state(CreateOrder.number)
    await message.answer("Введите ваш номер телефона:")


@router.message(CreateOrder.number)
async def process_number(
        message: Message,
        state: FSMContext
):
    if not message.text.replace('+', '').replace(' ', '').isdigit():
        await message.answer('Введите номер телефона')
        return

    await state.update_data(number=message.text)
    await state.set_state(CreateOrder.address)
    await message.answer(
        'Выберите способ доставки:',
        reply_markup=kb.choose_deltype
    )


@router.callback_query(F.data.startswith('delivery_'))
async def process_devtype(
        callback: CallbackQuery,
        state: FSMContext
):
    await callback.answer('')
    delivery_type = callback.data.replace('delivery_', '')
    await state.update_data(delivery_type=DELIVERYTYPE[delivery_type])
    await callback.message.answer("Введите адрес:")

@router.message(CreateOrder.address)
async def process_address(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    await state.update_data(address=message.text)
    data = await state.get_data()

    stmt = select(Cart).options(
        selectinload(
            Cart.products
        )
    ).where(
        Cart.user_id == message.from_user.id
    )
    cart_items = (await session.execute(stmt)).scalars().all()

    if not cart_items:
        await message.answer('Ваша корзина пуста!')
        await state.clear()
        return

    total_amount = 0
    order_items = []

    for item in cart_items:
        item_total = item.qty * item.products.price
        total_amount += item_total
        order_item = OrderItem(
            product_id=item.product_id,
            qty=item.qty,
        )
        order_items.append(order_item)

    new_order = Order(
        user_id=message.from_user.id,
        customer_name=data['name'],
        customer_phone=data['number'],
        customer_address=data['address'],
        delivery_type=data['delivery_type'],
        status='created',
        total_amount=total_amount
    )
    session.add(new_order)
    await session.flush()

    for order_item in order_items:
        order_item.order_id = new_order.uuid
        session.add(order_item)

    await session.execute(delete(Cart).where(Cart.user_id == message.from_user.id))

    await session.commit()

    is_admin = await check_admin(message, session)

    await message.answer(
        'Заказ создан',
        reply_markup=await kb_main.main_kb(is_admin)
    )
