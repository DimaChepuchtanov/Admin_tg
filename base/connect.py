from setting import setting
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


connect_str = f'postgresql+asyncpg://{setting.PG_USER}:{setting.PG_PASSWORD}@{setting.PG_HOST}:{setting.PG_PORT}/{setting.PG_DB}'

engine = create_async_engine(connect_str)
async_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def db_conn():
    async with async_maker() as con:
        yield con
