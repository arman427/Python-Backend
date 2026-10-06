import uuid

from fastapi import HTTPException

from app.models.enum import AttendanceStatus
from app.repositories.attendance import AttendanceRepository
from app.repositories.grade import GradeRepository
from app.repositories.lesson import LessonRepository
from app.repositories.student import StudentRepository
from app.schemas.grade import GradeCreate, GradeResponse, GradeWithStudentName


class GradeService:
    def __init__(
        self,
        grade_repo: GradeRepository,
        attendance_repo: AttendanceRepository,
        lesson_repo: LessonRepository,
        student_repo: StudentRepository,
    ) -> None:
        self.grade_repo = grade_repo
        self.attendance_repo = attendance_repo
        self.lesson_repo = lesson_repo
        self.student_repo = student_repo

    async def create_grade(
        self,
        lesson_id: int,
        data: GradeCreate,
        teacher_id: uuid.UUID,
    ) -> GradeResponse:




        lesson = await self.lesson_repo.get_by_id(lesson_id)

        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson.teacher_id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь преподавателем этого занятия",
            )

        
        student = await self.student_repo.get_by_id(data.student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Студент не найден")
        if student.group_id != lesson.group_id:
            raise HTTPException(
                status_code=400,
                detail="Студент не принадлежит группе этого занятия",
            )

        
        attendance = await self.attendance_repo.get_by_lesson_and_student(
            lesson_id, data.student_id
        )

        if not attendance or attendance.status not in (
            AttendanceStatus.PRESENT,
            AttendanceStatus.LATE,
        ):
            raise HTTPException(
                status_code=400,
                detail="Невозможно выставить оценку отсутствующему студенту",
            )

        
        existing = await self.grade_repo.get_by_lesson_and_student(
            lesson_id, data.student_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Оценка уже выставлена этому студенту за данное занятие",
            )

        grade = await self.grade_repo.create(
            lesson_id=lesson_id,
            student_id=data.student_id,
            grade_value=data.grade_value,
            comment=data.comment,
        )

        return GradeResponse(
            id=grade.id,
            lesson_id=grade.lesson_id,
            student_id=grade.student_id,
            grade_value=grade.grade_value,
            comment=grade.comment,
            created_at=grade.created_at,
        )

    async def get_lesson_grades(
        self,
        lesson_id: int,
        teacher_id: uuid.UUID,
    ) -> list[GradeWithStudentName]:

        lesson = await self.lesson_repo.get_by_id(lesson_id)

        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson.teacher_id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь преподавателем этого занятия",
            )

        grades = await self.grade_repo.get_by_lesson(lesson_id)

        result = []
        for g in grades:
            
            student_name = "—"
            if g.student and g.student.user:
                student_name = g.student.user.full_name
            elif g.student:
                
                s = await self.student_repo.get_by_id(g.student_id)
                student_name = s.user.full_name if s and s.user else "—"

            result.append(
                GradeWithStudentName(
                    id=g.id,
                    lesson_id=g.lesson_id,
                    student_id=g.student_id,
                    grade_value=g.grade_value,
                    comment=g.comment,
                    created_at=g.created_at,
                    full_name=student_name,
                )
            )

        return result
