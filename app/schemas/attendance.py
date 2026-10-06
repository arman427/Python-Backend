from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enum import AttendanceMethod, AttendanceStatus
from app.schemas.base import BaseResponseSchema


class SwipeRequest(BaseModel):

    student_id: int = Field(description="ID записи студента в таблице students")
    status: AttendanceStatus = Field(description="PRESENT или ABSENT")


class SwipeStudentCard(BaseModel):

    student_id: int
    full_name: str
    avatar_url: str | None = None
    student_card_number: str


class SwipeQueueResponse(BaseModel):

    students: list[SwipeStudentCard]
    total_count: int


class SwipeResultResponse(BaseModel):

    next_student: SwipeStudentCard | None = None
    remaining_count: int


class AttendanceResponse(BaseResponseSchema):

    id: int
    lesson_id: int
    student_id: int
    status: AttendanceStatus
    method: AttendanceMethod
    marked_at: datetime


class AttendanceSummary(BaseModel):

    student_id: int
    full_name: str
    status: AttendanceStatus
    method: AttendanceMethod | None = None
    marked_at: datetime | None = None
