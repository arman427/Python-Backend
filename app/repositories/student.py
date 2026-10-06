import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.students import StudentsORM


class StudentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, student_id: int) -> StudentsORM | None:
        result = await self.db.execute(
            select(StudentsORM)
            .options(selectinload(StudentsORM.user))
            .where(StudentsORM.id == student_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> StudentsORM | None:
        result = await self.db.execute(
            select(StudentsORM)
            .options(selectinload(StudentsORM.user))
            .where(StudentsORM.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_group_id(self, group_id: int) -> list[StudentsORM]:
        result = await self.db.execute(
            select(StudentsORM)
            .options(selectinload(StudentsORM.user))
            .where(StudentsORM.group_id == group_id)
            .order_by(StudentsORM.id)
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: uuid.UUID,
        group_id: int,
        student_card_number: str,
    ) -> StudentsORM:
        student = StudentsORM(
            user_id=user_id,
            group_id=group_id,
            student_card_number=student_card_number,
        )
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student
