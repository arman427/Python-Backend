from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.repositories.User import UserRepository
from app.services.auth import AuthService


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    return AuthService(UserRepository(db))
