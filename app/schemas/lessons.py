from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enum import LessonStatus
from app.schemas.base import BaseResponseSchema


class LessonCreate(BaseModel):
    subject_name: str = Field(description="Название предмета")
    group_id: int = Field(description="ID группы")
    date_time: datetime = Field(description="Дата и время занятия")
    classroom: str = Field(description="Аудитория")


class LessonResponse(BaseResponseSchema):
    id: int
    subject_name: str
    teacher_id: UUID
    group_id: int
    date_time: datetime
    classroom: str
    status: LessonStatus


class LessonWithGroupName(LessonResponse):

    group_name: str


class LessonStatusUpdate(BaseModel):

    status: LessonStatus
