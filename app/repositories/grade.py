from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.grade import GradeORM
from app.models.students import StudentsORM


class GradeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_lesson(self, lesson_id: int) -> list[GradeORM]:
        result = await self.db.execute(
            select(GradeORM)
            .options(selectinload(GradeORM.student).selectinload(StudentsORM.user))
            .where(GradeORM.lesson_id == lesson_id)
        )
        return list(result.scalars().all())

    async def get_by_lesson_and_student(
        self, lesson_id: int, student_id: int
    ) -> GradeORM | None:
        result = await self.db.execute(
            select(GradeORM).where(
                GradeORM.lesson_id == lesson_id,
                GradeORM.student_id == student_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        lesson_id: int,
        student_id: int,
        grade_value: int,
        comment: str | None = None,
    ) -> GradeORM:
        grade = GradeORM(
            lesson_id=lesson_id,
            student_id=student_id,
            grade_value=grade_value,
            comment=comment,
        )
        self.db.add(grade)
        await self.db.commit()
        await self.db.refresh(grade)
        return grade
