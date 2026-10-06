import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lessons import LessonORM
from app.models.enum import LessonStatus


class LessonRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, lesson_id: int) -> LessonORM | None:
        return await self.db.get(LessonORM, lesson_id)

    async def get_teacher_lessons(
        self,
        teacher_id: uuid.UUID,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[LessonORM]:

        stmt = (
            select(LessonORM)
            .options(selectinload(LessonORM.group))
            .where(LessonORM.teacher_id == teacher_id)
        )

        if date_from:
            stmt = stmt.where(LessonORM.date_time >= date_from)
        if date_to:
            stmt = stmt.where(LessonORM.date_time <= date_to)

        stmt = stmt.order_by(LessonORM.date_time)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        subject_name: str,
        teacher_id: uuid.UUID,
        group_id: int,
        date_time: datetime,
        classroom: str,
    ) -> LessonORM:
        lesson = LessonORM(
            subject_name=subject_name,
            teacher_id=teacher_id,
            group_id=group_id,
            date_time=date_time,
            classroom=classroom,
            status=LessonStatus.PLANNED,
        )
        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)
        return lesson

    async def update_status(self, lesson_id: int, status: LessonStatus) -> LessonORM | None:
        lesson = await self.get_by_id(lesson_id)
        if lesson:
            lesson.status = status
            await self.db.commit()
            await self.db.refresh(lesson)
        return lesson
