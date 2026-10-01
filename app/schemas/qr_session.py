from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enum import QRType


class QRGenerateRequest(BaseModel):
    lesson_id: int
    type: QRType


class QRResponse(BaseModel):
    id: int
    lesson_id: int
    qr_token: str
    type: QRType
    expires_at: datetime
    is_used: bool

    model_config = ConfigDict(from_attributes=True)
