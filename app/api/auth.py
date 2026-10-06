from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError

from app.api.dependencies import get_auth_service, get_current_user
from app.models.user import UserORM
from app.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserLoginResponse,
    UserMeResponse,
    UserRegister,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация"])


async def parse_login(request: Request) -> UserLogin:

    try:
        if "application/json" in request.headers.get("content-type", ""):
            return UserLogin.model_validate(await request.json())
        form = await request.form()
        return UserLogin(
            email=form.get("username") or form.get("email"),
            password=form.get("password"),
        )
    except (ValidationError, ValueError, TypeError):
        raise HTTPException(
            status_code=422, detail="Укажите корректные email и password"
        )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    description="Создаёт пользователя. Для готового студенческого профиля используйте тестовые данные seed.",
)
async def register(
    data: UserRegister, service: Annotated[AuthService, Depends(get_auth_service)]
) -> dict:
    await service.register(data)
    return {"detail": "Пользователь успешно зарегистрирован"}


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="Авторизация",
    description="Принимает JSON email/password или OAuth2 form username/password. Возвращает JWT.",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/UserLogin"}
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "required": ["username", "password"],
                        "properties": {
                            "username": {
                                "type": "string",
                                "format": "email",
                                "example": "teacher@example.com",
                            },
                            "password": {"type": "string", "example": "Teacher123!"},
                        },
                    }
                },
            },
        }
    },
)
async def login(
    data: Annotated[UserLogin, Depends(parse_login)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserLoginResponse:
    return await service.login(data.email, data.password)


@router.post("/refresh", response_model=TokenResponse, summary="Обновить JWT")
async def refresh_token(
    token: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await service.refresh_tokens(token.refresh_token)


@router.get("/me", response_model=UserMeResponse, summary="Текущий профиль")
async def get_me(user: Annotated[UserORM, Depends(get_current_user)]) -> UserMeResponse:
    return UserMeResponse.model_validate(user)
