from datetime import datetime

from pydantic import BaseModel

from app.models.enum import AttendanceMethod, AttendanceStatus
from app.schemas.base import BaseResponseSchema


class AttendanceCreate(BaseModel):
    student_id: int
    group_id: int
    status: AttendanceStatus
    method: AttendanceMethod


class AttendanceResponse(BaseResponseSchema, BaseModel):
    id: int
    marked_at: datetime
