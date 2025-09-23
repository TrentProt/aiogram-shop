import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Enum, String, Integer, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Role(enum.Enum):
    admin = 'admin'
    user = 'user'


class Status(enum.Enum):
    completed = 'completed'
    in_process = 'in_process'
    created = 'created'
    stopped = 'stopped'
    paid_for = 'paid_for'


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(40), default=None)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)

    cart: Mapped[list['Cart']] = relationship(back_populates='users')
    orders: Mapped[list['Order']] = relationship(back_populates='user')

class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30))

    products: Mapped[list['Product']] = relationship(back_populates='category')

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    price: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(100))
    photo: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('categories.id', ondelete='CASCADE'),
        index=True
    )

    category: Mapped['Category'] = relationship(back_populates='products')
    cart: Mapped[list['Cart']] = relationship(back_populates='products')
    order_items: Mapped[list['OrderItem']] = relationship(back_populates='product')


class Cart(Base):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.telegram_id', ondelete='CASCADE'),
        index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('products.id', ondelete='CASCADE'),
        index=True
    )
    qty: Mapped[int] = mapped_column(Integer, default=1)

    users: Mapped[list['User']] = relationship(back_populates='cart')
    products: Mapped[list['Product']] = relationship(back_populates='cart')


class Order(Base):
    __tablename__ = 'orders'

    uuid: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.telegram_id', ondelete='CASCADE'),
        index=True
    )
    customer_name: Mapped[str] = mapped_column(String(30))
    customer_phone: Mapped[str] = mapped_column(String(30))
    customer_address: Mapped[str] = mapped_column(String(100))
    delivery_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.created)
    total_amount: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user: Mapped['User'] = relationship(back_populates='orders')
    order_items: Mapped[list['OrderItem']] = relationship(back_populates='order')


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('orders.uuid', ondelete='CASCADE'),
        index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('products.id', ondelete='CASCADE'),
        index=True
    )
    qty: Mapped[int] = mapped_column(Integer)

    order: Mapped['Order'] = relationship(back_populates='order_items')
    product: Mapped['Product'] = relationship(back_populates='order_items')
