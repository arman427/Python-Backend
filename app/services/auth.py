import uuid

from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.enum import Role
from app.repositories.user import UserRepository
from app.schemas.user import (
    TokenResponse,
    UserLoginResponse,
    UserMeResponse,
    UserRegister,
)


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, data: UserRegister) -> None:
        if data.role == Role.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Регистрация администратора через публичный API запрещена",
            )
        user = await self.user_repo.get_by_email(data.email)

        if user:
            raise HTTPException(
                status_code=409, detail="Пользователь с таким email уже существует"
            )

        hash_pass = get_password_hash(data.password)

        await self.user_repo.create(
            email=data.email,
            hashed_password=hash_pass,
            full_name=data.full_name,
            role=data.role,
        )

    async def login(self, email: str, password: str) -> UserLoginResponse:
        user = await self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Неверный email или пароль",
            )

        access_token = create_access_token(user_id=user.id)
        refresh_token = create_refresh_token(user_id=user.id)

        await self.user_repo.update_refresh_token(user.id, refresh_token)

        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            avatar_url=user.avatar_url,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(token=refresh_token)

        if payload is None:
            raise HTTPException(status_code=401, detail="Невалидный или истекший токен")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Неверный тип токена")

        sub = payload.get("sub")
        try:
            user_id = uuid.UUID(sub)
        except (ValueError, TypeError, AttributeError):
            raise HTTPException(status_code=401, detail="Невалидный формат ID")

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден")

        if user.refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Недействительный токен")

        new_access_token = create_access_token(user_id=user.id)
        new_refresh_token = create_refresh_token(user_id=user.id)

        await self.user_repo.update_refresh_token(user.id, new_refresh_token)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )
