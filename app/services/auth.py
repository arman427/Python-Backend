import uuid

from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.repositories.User import UserRepository
from app.schemas.user import TokenResponse, UserRegister, UserResponse


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, data: UserRegister) -> None:
        user = await self.user_repo.get_by_email(data.email)

        if user:
            raise HTTPException(
                status_code=409, detail="Пользователь с таким email уже существует"
            )

        hash_pass = get_password_hash(data.password)

        user = await self.user_repo.create(data.email, hash_pass, data.name)

    async def login(self, email: str, password: str) -> UserResponse:
        user = await self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Неверный email или пароль",
            )

        access_token = create_access_token(user_id=user.id)
        refresh_token = create_refresh_token(user_id=user.id)

        await self.user_repo.update_refresh_token(user.id, refresh_token)

        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            token=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            ),
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

        user = await self.user_repo.get_by_id(user_id=user_id)

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
