from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GradeCreate(BaseModel):
    lesson_id: int
    student_id: int
    grade_value: int
    comment: str | None = None


class GradeResponse(GradeCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
