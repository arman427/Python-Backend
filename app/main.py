from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as user_router
from app.db.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
