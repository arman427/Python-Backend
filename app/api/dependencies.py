import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.db import get_db
from app.models.enum import Role
from app.models.user import UserORM
from app.repositories.attendance import AttendanceRepository
from app.repositories.grade import GradeRepository
from app.repositories.group import GroupRepository
from app.repositories.lesson import LessonRepository
from app.repositories.qr_session import QRSessionRepository
from app.repositories.student import StudentRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.grade import GradeService
from app.services.qr import QRService
from app.services.report import ReportService
from app.services.swipe import SwipeService
from app.services.teacher import TeacherService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    return AuthService(UserRepository(db))


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
    try:
        user_id = uuid.UUID(sub)
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=401, detail="Невалидный формат ID")

    user = await UserRepository(db).get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


def require_role(*roles: Role):


    async def role_checker(
        current_user: Annotated[UserORM, Depends(get_current_user)],
    ) -> UserORM:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="Недостаточно прав для выполнения данного действия",
            )
        return current_user

    return role_checker


def get_teacher_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeacherService:
    return TeacherService(
        lesson_repo=LessonRepository(db),
        student_repo=StudentRepository(db),
        group_repo=GroupRepository(db),
    )


def get_swipe_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SwipeService:
    return SwipeService(
        attendance_repo=AttendanceRepository(db),
        lesson_repo=LessonRepository(db),
        student_repo=StudentRepository(db),
    )


def get_qr_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QRService:
    return QRService(
        qr_repo=QRSessionRepository(db),
        attendance_repo=AttendanceRepository(db),
        lesson_repo=LessonRepository(db),
        student_repo=StudentRepository(db),
    )


def get_grade_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GradeService:
    return GradeService(
        grade_repo=GradeRepository(db),
        attendance_repo=AttendanceRepository(db),
        lesson_repo=LessonRepository(db),
        student_repo=StudentRepository(db),
    )


def get_report_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReportService:
    return ReportService(
        attendance_repo=AttendanceRepository(db),
        grade_repo=GradeRepository(db),
        lesson_repo=LessonRepository(db),
        student_repo=StudentRepository(db),
    )
