from pydantic import BaseModel

from app.schemas.base import BaseResponseSchema


class GroupCreate(BaseModel):
    name: str
    faculty: str


class GroupResponse(BaseResponseSchema, GroupCreate):
    id: int
