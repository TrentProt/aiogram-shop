from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.core.models import Base

class DBFunction:
    def __init__(
            self,
            url: str,
            echo: bool = True,
            echo_pool: bool = False,
            pool_size: int = 50,
            max_overflow: int = 10
    ):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    async def create_database(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        session = self.session_factory()
        yield session
        await session.close()


db_helper = DBFunction(url=str(settings.db.url), echo=bool(settings.db.echo))