import asyncio
import logging
from aiogram import Bot, Dispatcher

from app.core.config import settings
from app.core.db import db_helper
from app.core.middleware import DBMiddleware
from app.handlers.catalog import router as catalog_router
from app.handlers.main import router as main_router
from app.handlers.cart import router as cart_router
from app.handlers.order import router as order_router

bot = Bot(token=settings.api.key)
dp = Dispatcher()

db_middleware = DBMiddleware(db_helper)
dp.update.middleware(db_middleware)


async def main():
    await db_helper.create_database()
    dp.include_router(catalog_router)
    dp.include_router(main_router)
    dp.include_router(cart_router)
    dp.include_router(order_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
