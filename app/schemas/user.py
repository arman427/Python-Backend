import uuid

from pydantic import BaseModel, EmailStr, Field

from app.schemas.base import BaseResponseSchema


class UserRegister(BaseModel):
    full_name: str = Field(default="Гость", max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseResponseSchema):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    token: TokenResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str
