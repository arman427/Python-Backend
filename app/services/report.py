import uuid

from fastapi import HTTPException

from app.models.enum import AttendanceStatus
from app.repositories.attendance import AttendanceRepository
from app.repositories.grade import GradeRepository
from app.repositories.lesson import LessonRepository
from app.repositories.student import StudentRepository
from app.schemas.attendance import AttendanceSummary
from app.schemas.grade import GradeWithStudentName
from app.schemas.reports import LessonSummaryResponse


class ReportService:
    def __init__(
        self,
        attendance_repo: AttendanceRepository,
        grade_repo: GradeRepository,
        lesson_repo: LessonRepository,
        student_repo: StudentRepository,
    ) -> None:
        self.attendance_repo = attendance_repo
        self.grade_repo = grade_repo
        self.lesson_repo = lesson_repo
        self.student_repo = student_repo

    async def get_lesson_summary(
        self, lesson_id: int, teacher_id: uuid.UUID
    ) -> LessonSummaryResponse:

        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")
        if lesson.teacher_id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь преподавателем этого занятия",
            )

        
        all_students = await self.student_repo.get_by_group_id(lesson.group_id)
        total_students = len(all_students)

        
        attendance_records = await self.attendance_repo.get_by_lesson(lesson_id)
        attendance_map = {a.student_id: a for a in attendance_records}

        present_count = sum(
            1 for a in attendance_records if a.status == AttendanceStatus.PRESENT
        )
        absent_count = sum(
            1 for a in attendance_records if a.status == AttendanceStatus.ABSENT
        )
        late_count = sum(
            1 for a in attendance_records if a.status == AttendanceStatus.LATE
        )

        
        unmarked = total_students - len(attendance_records)
        absent_count += unmarked

        attendance_percent = (
            round((present_count + late_count) / total_students * 100, 1)
            if total_students > 0
            else 0.0
        )

        
        attendance_list = []
        student_map = {s.id: s for s in all_students}
        for student in all_students:
            att = attendance_map.get(student.id)
            attendance_list.append(
                AttendanceSummary(
                    student_id=student.id,
                    full_name=student.user.full_name if student.user else "—",
                    status=att.status if att else AttendanceStatus.ABSENT,
                    method=att.method if att else None,
                    marked_at=att.marked_at if att else None,
                )
            )

        
        grades = await self.grade_repo.get_by_lesson(lesson_id)
        grade_values = [g.grade_value for g in grades]
        average_grade = (
            round(sum(grade_values) / len(grade_values), 2)
            if grade_values
            else None
        )

        grades_list = []
        for g in grades:
            student_name = "—"
            s = student_map.get(g.student_id)
            if s and s.user:
                student_name = s.user.full_name

            grades_list.append(
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

        return LessonSummaryResponse(
            lesson_id=lesson.id,
            subject_name=lesson.subject_name,
            total_students=total_students,
            present_count=present_count,
            absent_count=absent_count,
            late_count=late_count,
            attendance_percent=attendance_percent,
            average_grade=average_grade,
            attendance=attendance_list,
            grades=grades_list,
        )
