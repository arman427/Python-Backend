from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseResponseSchema


class StudentCreate(BaseModel):
    user_id: UUID = Field(description="ID пользователя из таблицы users")
    group_id: int = Field(description="ID группы")
    student_card_number: str = Field(description="Номер студенческого билета")


class StudentResponse(BaseResponseSchema):
    id: int
    user_id: UUID
    group_id: int
    student_card_number: str


class StudentWithUserInfo(StudentResponse):

    full_name: str
    email: str
    avatar_url: str | None = None
