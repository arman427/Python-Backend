import asyncio

from fastapi import FastAPI

from app.db.db import init_db

app = FastAPI()

async def main():
    init_db()

if __name__ == "__main__":
    asyncio.run(main())