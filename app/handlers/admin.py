from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.models import Order, Category, Product
from app.keyboards.admin import edit_status_keyboard
from app.keyboards.main import main_kb
from app.utils.utils import check_admin


router = Router()


class CreateNewProduct(StatesGroup):
    catalog = State()
    name = State()
    price = State()
    photo = State()
    description = State()


class UpdateProduct(StatesGroup):
    new_name = State()
    catalog = State()
    name = State()
    price = State()
    photo = State()
    description = State()

class OrderStatus(StatesGroup):
    order_id = State()

@router.message(F.text == 'Заказы')
async def get_orders(
        message: Message,
        session: AsyncSession
):
    is_admin = check_admin(message, session)

    if is_admin:
        stmt_orders = select(Order)
        orders = (await session.execute(stmt_orders)).scalars().all()
        text = ''
        for order in orders:
            text += (f'UUID: {order.uuid}\n'
                     f'TG_ID: {order.user_id}\n'
                     f'Status: {order.status.value}\n'
                     f'Total: {order.total_amount} руб.\n\n')
        await message.answer(text)


@router.message(F.text == 'Изменить статусы заказа')
async def update_orders(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    is_admin = await check_admin(message, session)

    if is_admin:
        await message.answer(
            "Введите UUID заказа, статус которого хотите изменить:"
        )
        await state.set_state(OrderStatus.order_id)


@router.message(OrderStatus.order_id)
async def process_order_id(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    order_uuid = message.text.strip()
    stmt = select(Order).where(
        Order.uuid == order_uuid
    )

    order = (await session.execute(stmt)).scalar_one_or_none()

    if not order:
        await message.answer('Такого заказа нету')
        return

    await message.answer(
        f'{order.uuid}\n{order.total_amount}\n{order.status.value}\n{order.delivery_type}',
        reply_markup=await edit_status_keyboard(order_uuid)
    )

    await state.clear()


@router.callback_query(F.data.startswith('status_'))
async def edit_status(
        callback: CallbackQuery,
        session: AsyncSession
):
    data = callback.data.split('_')
    uuid = data[1]
    status = data[2]

    stmt = update(Order).where(
        Order.uuid == uuid
    ).values(status=status)

    await session.execute(stmt)
    await session.commit()

    await callback.answer(f'Статус заказа изменен на "{status}"')


@router.message(F.text == 'Добавление товаров')
async def create_new_product(
        message: Message,
        session: AsyncSession,
        state: FSMContext,
):
    is_admin = await check_admin(message, session)

    if is_admin:
        await message.answer('Введите название существующего каталога,'
                             ' куда надо добавить:')
        await state.set_state(CreateNewProduct.catalog)


@router.message(CreateNewProduct.catalog)
async def proccess_catalog(
        message: Message,
        state: FSMContext
):
    await state.update_data(catalog=message.text.capitalize())
    await state.set_state(CreateNewProduct.name)
    await message.answer('Введите название продукта:')


@router.message(CreateNewProduct.name)
async def proccess_name(
        message: Message,
        state: FSMContext
):
    await state.update_data(name=message.text)
    await state.set_state(CreateNewProduct.price)
    await message.answer('Введите цену продукта:')


@router.message(CreateNewProduct.price)
async def proccess_price(
        message: Message,
        state: FSMContext
):
    await state.update_data(price=message.text)
    await state.set_state(CreateNewProduct.photo)
    await message.answer('Введите ссылку на фото продукта:')


@router.message(CreateNewProduct.photo)
async def proccess_photo(
        message: Message,
        state: FSMContext
):
    await state.update_data(photo=message.text)
    await state.set_state(CreateNewProduct.description)
    await message.answer('Введите описание продукта:')


@router.message(CreateNewProduct.description)
async def proccess_description(
        message: Message,
        session: AsyncSession,
        state: FSMContext,
):
    await state.update_data(description=message.text)
    data = await state.get_data()

    stmt_category = select(Category).where(
        Category.name == data['catalog']
    )
    category = (await session.execute(stmt_category)).scalar_one_or_none()

    if not category:
        await message.answer('Такого каталога не нашлось')
        return

    new_product = Product(
        name=data['name'],
        price=int(data['price']),
        description=data['description'],
        photo=data['photo'],
        category_id=category.id
    )
    session.add(new_product)
    await session.commit()

    await state.clear()

    await message.answer(
        'Товар успешно добавлен',
        reply_markup=await main_kb(await check_admin(message, session))
    )


@router.message(F.text == 'Изменение товаров')
async def update_product(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    is_admin = await check_admin(message, session)

    if is_admin:
        await message.answer(
            'Введите точное название товара,'
            ' который хотите поменять:'
        )
        await state.set_state(UpdateProduct.name)


@router.message(UpdateProduct.name)
async def admin_update_product(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    await state.update_data(name=message.text.strip())

    stmt = select(Product).options(joinedload(
        Product.category
    )).where(
        Product.name == message.text.strip()
    )
    product = (await session.execute(stmt)).scalar_one_or_none()

    if not product:
        await message.answer('Такого продукта нету')
        return

    await message.answer(
        f'Нынешняя информация:\n'
        f'Название: {product.name}\n'
        f'Описание: {product.description}\n'
        f'Цена: {product.price}\n'
        f'Фото: {product.photo}\n'
        f'Категория: {product.category.name}\n\n'
        f'Скинул информацию о товаре, чтобы лучше было копировать то, что не нужно менять\n\n'
        f'НАПИШИТЕ НОВОЕ НАЗВАНИЕ ИЛИ ОСТАВЬТЕ СТАРОЕ:'
    )
    await state.set_state(UpdateProduct.new_name)


@router.message(UpdateProduct.new_name)
async def proccess_new_name_update(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    await state.update_data(new_name=message.text.strip())

    stmt = select(Category)
    categories = (await session.execute(stmt)).scalars().all()
    text = 'Категории:\n'
    for category in categories:
        text += f'{category.name}\n'


    await message.answer(text + '\n' + 'Введите нужную категорию, написав цифру:\n')
    await state.set_state(UpdateProduct.catalog)


@router.message(UpdateProduct.catalog)
async def admin_proccess_catalog(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    await state.update_data(catalog=message.text.strip())

    stmt = select(Category).where(
        Category.name == message.text.strip()
    )
    category = (await session.execute(stmt)).scalar_one_or_none()

    if not category:
        await message.answer(
            'Такой категории нету'
        )
        return

    await message.answer('Введите описание:')
    await state.set_state(UpdateProduct.description)


@router.message(UpdateProduct.description)
async def admin_proccess_description(
        message: Message,
        state: FSMContext
):
    await state.update_data(description=message.text.strip())
    await message.answer('Введите цену:')
    await state.set_state(UpdateProduct.price)


@router.message(UpdateProduct.price)
async def admin_proccess_price(
        message: Message,
        state: FSMContext
):
    await state.update_data(price=message.text.strip())
    await message.answer('Введите ссылку на фото:')
    await state.set_state(UpdateProduct.photo)


@router.message(UpdateProduct.photo)
async def admin_proccess_photo(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    await state.update_data(photo=message.text.strip())
    data = await state.get_data()

    stmt_cat = select(Category).where(
        Category.name == data['catalog']
    )
    category = (await session.execute(stmt_cat)).scalar_one_or_none()

    stmt_update_prod = update(Product).where(
        Product.name == data['name']
    ).values(
        name=data['new_name'],
        price=int(data['price']),
        description=data['description'],
        photo=data['photo'],
        category_id=category.id
    )
    await session.execute(stmt_update_prod)
    await session.commit()
    await message.answer(
        'Продукт обновлен',
        reply_markup=await main_kb(await check_admin(message, session))
    )
    await state.clear()