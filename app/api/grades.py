from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_grade_service, require_role
from app.models.enum import Role
from app.models.user import UserORM
from app.schemas.grade import GradeCreate, GradeResponse, GradeWithStudentName
from app.services.grade import GradeService

router = APIRouter(prefix="/grades", tags=["Оценки"])
teacher_only = require_role(Role.TEACHER, Role.ADMIN)


@router.post(
    "/lessons/{lesson_id}/grades",
    response_model=GradeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Выставить оценку",
    description="Оценка 2–5 доступна только присутствующему или опоздавшему студенту.",
)
async def create_grade(
    lesson_id: int,
    data: GradeCreate,
    user: Annotated[UserORM, Depends(teacher_only)],
    service: Annotated[GradeService, Depends(get_grade_service)],
) -> GradeResponse:
    return await service.create_grade(lesson_id, data, user.id)


@router.get(
    "/lessons/{lesson_id}/grades",
    response_model=list[GradeWithStudentName],
    summary="Оценки за занятие",
)
async def get_grades(
    lesson_id: int,
    user: Annotated[UserORM, Depends(teacher_only)],
    service: Annotated[GradeService, Depends(get_grade_service)],
) -> list[GradeWithStudentName]:
    return await service.get_lesson_grades(lesson_id, user.id)
