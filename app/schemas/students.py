from pydantic import BaseModel

from app.schemas.base import BaseResponseSchema


class StudentCreate(BaseModel):
    name: str
    group_id: int
    student_card_numbe: str


class StudentResponse(BaseResponseSchema, StudentCreate):
    id: int
