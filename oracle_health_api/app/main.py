import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import create_pool, close_pool
from app.routes.health import router as health_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()
    yield
    await close_pool()


app = FastAPI(
    title="Oracle Health Check API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
