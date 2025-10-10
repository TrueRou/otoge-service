import contextlib

import httpx
from maimai_py import MaimaiClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from maimai_prober.settings import get_settings

settings = get_settings()

maimai_client = MaimaiClient()
async_engine = create_async_engine(settings.database_url)
httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(None))


@contextlib.asynccontextmanager
async def async_session_ctx():
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session


async def init_db():
    import maimai_prober.models  # noqa: F401

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
