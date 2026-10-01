from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enum import LessonStatus
from app.schemas.base import BaseResponseSchema


class LessonCreate(BaseModel):
    subject_name: str
    teacher_id: UUID
    group_id: int
    date_time: datetime
    classroom: str


class LessonResponse(LessonCreate, BaseResponseSchema):
    id: int
    status: LessonStatus
