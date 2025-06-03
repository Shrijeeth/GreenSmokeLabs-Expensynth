from fastapi import APIRouter

from green_smoke_labs_expensynth.api.routes import (
    health_check,
)

api_router = APIRouter()
api_router.include_router(health_check.router, tags=["health_check"])
