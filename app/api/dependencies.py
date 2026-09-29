import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.db import get_db
from app.models.user import UserORM
from app.repositories.User import UserRepository
from app.services.auth import AuthService


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    return AuthService(UserRepository(db))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserORM:
    payload = decode_token(token=token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Неверный тип токена")

    sub = payload.get("sub")
    user_id = uuid.UUID(sub)

    user = await UserRepository(db).get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user
