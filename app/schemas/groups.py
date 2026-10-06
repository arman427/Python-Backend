from pydantic import BaseModel, Field

from app.schemas.base import BaseResponseSchema


class GroupCreate(BaseModel):
    name: str = Field(description="Название группы, например 'ВСПК-201'")
    faculty: str = Field(description="Факультет / отделение")


class GroupResponse(BaseResponseSchema):
    id: int
    name: str
    faculty: str
