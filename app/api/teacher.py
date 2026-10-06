from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_teacher_service, require_role
from app.models.enum import Role
from app.models.user import UserORM
from app.schemas.lessons import (
    LessonCreate,
    LessonResponse,
    LessonStatusUpdate,
    LessonWithGroupName,
)
from app.schemas.students import StudentWithUserInfo
from app.services.teacher import TeacherService

router = APIRouter(prefix="/teacher", tags=["Преподаватель"])

get_teacher_user = require_role(Role.TEACHER, Role.ADMIN)


@router.get(
    "/lessons",
    response_model=list[LessonWithGroupName],
    summary="Список занятий преподавателя",
    description="Получить список занятий на сегодня или текущую неделю. "
    "Параметр period: 'today' или 'week' (по умолчанию 'week').",
)
async def get_lessons(
    user: Annotated[UserORM, Depends(get_teacher_user)],
    service: Annotated[TeacherService, Depends(get_teacher_service)],
    period: str = Query(default="week", pattern="^(today|week)$"),
) -> list[LessonWithGroupName]:
    return await service.get_lessons(teacher_id=user.id, period=period)


@router.get(
    "/lessons/{lesson_id}/students",
    response_model=list[StudentWithUserInfo],
    summary="Список студентов группы для пары",
    description="Получить список студентов группы, привязанной к указанному занятию.",
)
async def get_lesson_students(
    lesson_id: int,
    user: Annotated[UserORM, Depends(get_teacher_user)],
    service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> list[StudentWithUserInfo]:
    return await service.get_lesson_students(
        lesson_id=lesson_id,
        teacher_id=user.id,
    )


@router.post(
    "/lessons",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать занятие",
    description="Создать новое занятие (пару). teacher_id берётся из токена автоматически.",
)
async def create_lesson(
    data: LessonCreate,
    user: Annotated[UserORM, Depends(get_teacher_user)],
    service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> LessonResponse:
    return await service.create_lesson(teacher_id=user.id, data=data)


@router.patch(
    "/lessons/{lesson_id}/status",
    response_model=LessonResponse,
    summary="Обновить статус занятия",
    description="Изменить статус занятия: PLANNED → ACTIVE → FINISHED.",
)
async def update_lesson_status(
    lesson_id: int,
    data: LessonStatusUpdate,
    user: Annotated[UserORM, Depends(get_teacher_user)],
    service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> LessonResponse:
    return await service.update_lesson_status(
        lesson_id=lesson_id,
        teacher_id=user.id,
        status=data.status,
    )
