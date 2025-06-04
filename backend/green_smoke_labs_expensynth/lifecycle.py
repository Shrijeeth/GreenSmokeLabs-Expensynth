from fastapi import FastAPI

from green_smoke_labs_expensynth.configs.database import (
    cleanup_postgres_session,
    initialize_postgres_engine,
    initialize_postgres_session,
)


async def startup(wapp: FastAPI):
    print("Starting the app...")
    engine = initialize_postgres_engine()
    initialize_postgres_session(engine)


async def shutdown(wapp: FastAPI):
    print("Shutting down the app...")
    await cleanup_postgres_session()
