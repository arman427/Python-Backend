import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserORM


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> UserORM | None:
        user = await self.db.execute(select(UserORM).where(UserORM.email == email))

        return user.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> UserORM | None:
        user = await self.db.get(UserORM, user_id)

        return user

    async def create(
        self, email: str, hashed_password: str, name: str | None = None
    ) -> UserORM:
        user_data = {"email": email, "hashed_password": hashed_password}
        if name is not None:
            user_data["name"] = name

        user = UserORM(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_refresh_token(
        self, user_id: uuid.UUID, refresh_token: str | None
    ) -> None:

        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(refresh_token=refresh_token)
        )

        await self.db.execute(stmt)
        await self.db.commit()
