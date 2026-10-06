import uuid

from fastapi import HTTPException

from app.models.enum import AttendanceMethod, AttendanceStatus
from app.repositories.attendance import AttendanceRepository
from app.repositories.lesson import LessonRepository
from app.repositories.student import StudentRepository
from app.schemas.attendance import (
    AttendanceResponse,
    SwipeQueueResponse,
    SwipeResultResponse,
    SwipeStudentCard,
)


class SwipeService:
    def __init__(
        self,
        attendance_repo: AttendanceRepository,
        lesson_repo: LessonRepository,
        student_repo: StudentRepository,
    ) -> None:
        self.attendance_repo = attendance_repo
        self.lesson_repo = lesson_repo
        self.student_repo = student_repo

    async def get_swipe_queue(
        self,
        lesson_id: int,
        teacher_id: uuid.UUID,
    ) -> SwipeQueueResponse:

        lesson = await self.lesson_repo.get_by_id(lesson_id)

        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson.teacher_id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь преподавателем этого занятия",
            )

        
        students = await self.student_repo.get_by_group_id(lesson.group_id)

        
        marked_ids = await self.attendance_repo.get_marked_student_ids(lesson_id)

        
        cards = [
            SwipeStudentCard(
                student_id=s.id,
                full_name=s.user.full_name if s.user else "—",
                avatar_url=s.user.avatar_url if s.user else None,
                student_card_number=s.student_card_number,
            )
            for s in students
            if s.id not in marked_ids
        ]

        return SwipeQueueResponse(students=cards, total_count=len(cards))

    async def process_swipe(
        self,
        lesson_id: int,
        student_id: int,
        status: AttendanceStatus,
        teacher_id: uuid.UUID,
    ) -> SwipeResultResponse:

        lesson = await self.lesson_repo.get_by_id(lesson_id)

        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson.teacher_id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь преподавателем этого занятия",
            )

        if status not in (AttendanceStatus.PRESENT, AttendanceStatus.ABSENT):
            raise HTTPException(
                status_code=422,
                detail="Для свайпа доступны только статусы PRESENT и ABSENT",
            )

        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Студент не найден")
        if student.group_id != lesson.group_id:
            raise HTTPException(
                status_code=400,
                detail="Студент не принадлежит группе этого занятия",
            )

        
        existing = await self.attendance_repo.get_by_lesson_and_student(
            lesson_id, student_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Этот студент уже отмечен на данном занятии",
            )

        
        await self.attendance_repo.create(
            lesson_id=lesson_id,
            student_id=student_id,
            status=status,
            method=AttendanceMethod.SWIPE_MANUAL,
        )

        
        queue = await self.get_swipe_queue(lesson_id, teacher_id)

        next_student = queue.students[0] if queue.students else None

        return SwipeResultResponse(
            next_student=next_student,
            remaining_count=queue.total_count,
        )
