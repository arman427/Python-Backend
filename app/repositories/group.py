from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.groups import GroupORM


class GroupRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, group_id: int) -> GroupORM | None:
        return await self.db.get(GroupORM, group_id)

    async def get_all(self) -> list[GroupORM]:
        result = await self.db.execute(select(GroupORM).order_by(GroupORM.name))
        return list(result.scalars().all())

    async def create(self, name: str, faculty: str) -> GroupORM:
        group = GroupORM(name=name, faculty=faculty)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group
