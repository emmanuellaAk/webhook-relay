import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

TEST_DB_URL = "postgresql+asyncpg://relay:relay@localhost:5433/relay_test"
os.environ["DATABASE_URL"] = TEST_DB_URL

from app.main import app       # noqa: E402
from app.models import Base    # noqa: E402
from app import db             # noqa: E402


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    db.engine = engine
    db.SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()
