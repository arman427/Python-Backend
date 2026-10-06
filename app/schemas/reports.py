from pydantic import BaseModel

from app.schemas.attendance import AttendanceSummary
from app.schemas.grade import GradeWithStudentName


class LessonSummaryResponse(BaseModel):

    lesson_id: int
    subject_name: str
    total_students: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_percent: float
    average_grade: float | None = None
    attendance: list[AttendanceSummary]
    grades: list[GradeWithStudentName]
