from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.base import BaseResponseSchema


class GradeCreate(BaseModel):

    student_id: int = Field(description="ID записи студента в таблице students")
    grade_value: int = Field(ge=2, le=5, description="Оценка: 2, 3, 4 или 5")
    comment: str | None = Field(default=None, description="Комментарий к оценке")


class GradeResponse(BaseResponseSchema):

    id: int
    lesson_id: int
    student_id: int
    grade_value: int
    comment: str | None = None
    created_at: datetime


class GradeWithStudentName(GradeResponse):

    full_name: str
