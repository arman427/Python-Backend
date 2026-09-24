from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
