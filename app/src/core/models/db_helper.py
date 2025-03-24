from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
)
from core.config import settings
import contextlib
from typing import Any, AsyncIterator


class DatabaseHelper:

    def __init__(
        self,
        url,
        echo: bool = False,
        echo_pool: bool = False,
        max_overflow: int = 10,
        pool_size: int = 5,
    ):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            max_overflow=max_overflow,
            echo_pool=echo_pool,
            pool_size=pool_size,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False
        )

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self.engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    async def dispose(self):
        await self.engine.dispose()

    async def get_session_getter(self):
        async with self.session_factory() as session:
            yield session
            await session.close()


db_helper = DatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    max_overflow=settings.db.max_overflow,
    pool_size=settings.db.pool_size,
)


async def get_db_session():
    async with db_helper.session_factory() as session:
        yield session
