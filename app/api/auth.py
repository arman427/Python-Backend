from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_auth_service
from app.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister, service: Annotated[AuthService, Depends(get_auth_service)]
) -> None:
    return await service.register(data)


@router.post("/login", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def login(
    data: UserLogin, service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserResponse:
    return await service.login(data.email, data.password)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    token: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await service.refresh_tokens(token.refresh_token)
