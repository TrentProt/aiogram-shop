from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class DBMiddleware(BaseMiddleware):
    def __init__(self, db_helper):
        self.db_helper = db_helper

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        print('До обработчика')

        async with self.db_helper.get_session() as session:
            data['session'] = session
            result = await handler(event, data)

        print('После обработчика')
        return result
