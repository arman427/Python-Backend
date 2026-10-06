from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceORM
from app.models.enum import AttendanceMethod, AttendanceStatus


class AttendanceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_lesson_and_student(
        self, lesson_id: int, student_id: int
    ) -> AttendanceORM | None:
        result = await self.db.execute(
            select(AttendanceORM).where(
                AttendanceORM.lesson_id == lesson_id,
                AttendanceORM.student_id == student_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_lesson(self, lesson_id: int) -> list[AttendanceORM]:
        result = await self.db.execute(
            select(AttendanceORM).where(AttendanceORM.lesson_id == lesson_id)
        )
        return list(result.scalars().all())

    async def get_marked_student_ids(self, lesson_id: int) -> set[int]:

        result = await self.db.execute(
            select(AttendanceORM.student_id).where(
                AttendanceORM.lesson_id == lesson_id
            )
        )
        return set(result.scalars().all())

    async def create(
        self,
        lesson_id: int,
        student_id: int,
        status: AttendanceStatus,
        method: AttendanceMethod,
    ) -> AttendanceORM:
        attendance = AttendanceORM(
            lesson_id=lesson_id,
            student_id=student_id,
            status=status,
            method=method,
        )
        self.db.add(attendance)
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance

    async def update_status(
        self,
        lesson_id: int,
        student_id: int,
        status: AttendanceStatus,
        method: AttendanceMethod,
    ) -> AttendanceORM | None:

        existing = await self.get_by_lesson_and_student(lesson_id, student_id)
        if existing:
            existing.status = status
            existing.method = method
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        return await self.create(lesson_id, student_id, status, method)
