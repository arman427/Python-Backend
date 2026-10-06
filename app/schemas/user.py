import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enum import Role
from app.schemas.base import BaseResponseSchema


class UserRegister(BaseModel):
    full_name: str = Field(default="Гость", max_length=100, description="ФИО пользователя")
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=6, max_length=128, description="Пароль")
    role: Role = Field(default=Role.STUDENT, description="Роль: TEACHER, STUDENT, ADMIN")


class UserLogin(BaseModel):
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=6, max_length=128, description="Пароль")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserMeResponse(BaseResponseSchema):

    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: Role
    avatar_url: str | None = None
    created_at: datetime


class UserLoginResponse(BaseResponseSchema):

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: Role
    avatar_url: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
