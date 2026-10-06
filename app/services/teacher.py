import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from app.models.enum import LessonStatus
from app.repositories.lesson import LessonRepository
from app.repositories.group import GroupRepository
from app.repositories.student import StudentRepository
from app.schemas.lessons import LessonCreate, LessonResponse, LessonWithGroupName
from app.schemas.students import StudentWithUserInfo


class TeacherService:
    def __init__(
        self,
        lesson_repo: LessonRepository,
        student_repo: StudentRepository,
        group_repo: GroupRepository,
    ) -> None:
        self.lesson_repo = lesson_repo
        self.student_repo = student_repo
        self.group_repo = group_repo

    async def get_lessons(
        self,
        teacher_id: uuid.UUID,
        period: str = "week",
    ) -> list[LessonWithGroupName]:

        now = datetime.now(timezone.utc)

        if period == "today":
            date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
            date_to = date_from + timedelta(days=1)
        else:  
            
            start_of_week = now - timedelta(days=now.weekday())
            date_from = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
            date_to = date_from + timedelta(days=7)

        lessons = await self.lesson_repo.get_teacher_lessons(
            teacher_id=teacher_id,
            date_from=date_from,
            date_to=date_to,
        )

        return [
            LessonWithGroupName(
                id=lesson.id,
                subject_name=lesson.subject_name,
                teacher_id=lesson.teacher_id,
                group_id=lesson.group_id,
                date_time=lesson.date_time,
                classroom=lesson.classroom,
                status=lesson.status,
                group_name=lesson.group.name if lesson.group else "—",
            )
            for lesson in lessons
        ]

    async def get_lesson_students(
        self,
        lesson_id: int,
        teacher_id: uuid.UUID,
    ) -> list[StudentWithUserInfo]:

        lesson = await self.lesson_repo.get_by_id(lesson_id)

        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson.teacher_id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь преподавателем этого занятия",
            )

        students = await self.student_repo.get_by_group_id(lesson.group_id)

        return [
            StudentWithUserInfo(
                id=s.id,
                user_id=s.user_id,
                group_id=s.group_id,
                student_card_number=s.student_card_number,
                full_name=s.user.full_name if s.user else "—",
                email=s.user.email if s.user else "—",
                avatar_url=s.user.avatar_url if s.user else None,
            )
            for s in students
        ]

    async def create_lesson(
        self,
        teacher_id: uuid.UUID,
        data: LessonCreate,
    ) -> LessonResponse:
        if not await self.group_repo.get_by_id(data.group_id):
            raise HTTPException(status_code=404, detail="Группа не найдена")
        lesson = await self.lesson_repo.create(
            subject_name=data.subject_name,
            teacher_id=teacher_id,
            group_id=data.group_id,
            date_time=data.date_time,
            classroom=data.classroom,
        )
        return LessonResponse(
            id=lesson.id,
            subject_name=lesson.subject_name,
            teacher_id=lesson.teacher_id,
            group_id=lesson.group_id,
            date_time=lesson.date_time,
            classroom=lesson.classroom,
            status=lesson.status,
        )

    async def update_lesson_status(
        self,
        lesson_id: int,
        teacher_id: uuid.UUID,
        status: LessonStatus,
    ) -> LessonResponse:
        lesson = await self.lesson_repo.get_by_id(lesson_id)

        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson.teacher_id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь преподавателем этого занятия",
            )

        updated = await self.lesson_repo.update_status(lesson_id, status)
        return LessonResponse(
            id=updated.id,
            subject_name=updated.subject_name,
            teacher_id=updated.teacher_id,
            group_id=updated.group_id,
            date_time=updated.date_time,
            classroom=updated.classroom,
            status=updated.status,
        )
