from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enum import QRType
from app.schemas.base import BaseResponseSchema


class QRGenerateResponse(BaseResponseSchema):

    id: int
    lesson_id: int
    qr_token: str
    type: QRType
    expires_at: datetime
    is_used: bool


class QRStudentConfirm(BaseModel):

    qr_token: str = Field(description="Токен из QR-кода учителя")
    latitude: float | None = Field(default=None, ge=-90, le=90, description="Широта (опционально)")
    longitude: float | None = Field(default=None, ge=-180, le=180, description="Долгота (опционально)")


class QRStudentMyCode(BaseModel):

    qr_token: str
    student_id: int
    full_name: str


class QRTeacherScanRequest(BaseModel):

    qr_token: str = Field(description="Токен из персонального QR-кода студента")
    lesson_id: int = Field(description="ID занятия, на котором сканируется")
