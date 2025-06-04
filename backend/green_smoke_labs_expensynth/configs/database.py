import gc
import os
from contextlib import asynccontextmanager
from functools import wraps
from urllib.parse import quote

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = None
SessionLocal = None
BaseModel = declarative_base()


def get_postgres_url(is_async: bool = True):
    username = quote(os.getenv("POSTGRES_USERNAME"))
    password = quote(os.getenv("POSTGRES_PASSWORD"))
    host = quote(os.getenv("POSTGRES_HOST"))
    port = quote(str(os.getenv("POSTGRES_PORT")))
    database = quote(os.getenv("POSTGRES_DATABASE"))
    if is_async:
        if not password or password == "":
            return f"postgresql+asyncpg://{username}@{host}:{port}/{database}"
        return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
    if not password or password == "":
        return f"postgresql://{username}@{host}:{port}/{database}"
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"


def initialize_postgres_engine():
    global engine
    engine = create_async_engine(
        url=get_postgres_url(is_async=True),
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=2,
        pool_recycle=300,
        pool_use_lifo=True,
    )
    return engine


def initialize_postgres_session(postgres_engine):
    global SessionLocal
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=postgres_engine, class_=AsyncSession
    )
    return SessionLocal


async def cleanup_postgres_session():
    global SessionLocal, BaseModel, engine
    if SessionLocal is not None:
        SessionLocal.close_all()
        SessionLocal = None
    if engine is not None:
        await engine.dispose()
        engine = None
    if BaseModel is not None:
        BaseModel = None
    gc.collect()


@asynccontextmanager
async def get_db():
    async with SessionLocal() as session:
        yield session


def use_db_session(func):
    @wraps(func)
    async def wrapper(*args, db=None, **kwargs):
        if db is None:
            async with get_db() as db:
                try:
                    return await func(db=db, *args, **kwargs)
                except Exception as e:
                    await db.rollback()
                    raise e
        else:
            return await func(db=db, *args, **kwargs)

    return wrapper
