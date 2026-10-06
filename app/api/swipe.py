from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_swipe_service, require_role
from app.models.enum import Role
from app.models.user import UserORM
from app.schemas.attendance import SwipeQueueResponse, SwipeRequest, SwipeResultResponse
from app.services.swipe import SwipeService

router = APIRouter(prefix="/attendance/swipe", tags=["Посещаемость — Свайп"])

get_teacher_user = require_role(Role.TEACHER, Role.ADMIN)


@router.get(
    "/lessons/{lesson_id}/swipe-queue",
    response_model=SwipeQueueResponse,
    summary="Очередь карточек для свайпа",
    description="Получить очередь неотмеченных студентов (ФИО, фото, ID) "
    "для последовательного свайпа.",
)
async def get_swipe_queue(
    lesson_id: int,
    user: Annotated[UserORM, Depends(get_teacher_user)],
    service: Annotated[SwipeService, Depends(get_swipe_service)],
) -> SwipeQueueResponse:
    return await service.get_swipe_queue(
        lesson_id=lesson_id,
        teacher_id=user.id,
    )


@router.post(
    "/lessons/{lesson_id}/swipe",
    response_model=SwipeResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Отправить результат свайпа",
    description="Отметить студента как PRESENT или ABSENT. "
    "Возвращает следующего студента и количество оставшихся.",
)
async def process_swipe(
    lesson_id: int,
    data: SwipeRequest,
    user: Annotated[UserORM, Depends(get_teacher_user)],
    service: Annotated[SwipeService, Depends(get_swipe_service)],
) -> SwipeResultResponse:
    return await service.process_swipe(
        lesson_id=lesson_id,
        student_id=data.student_id,
        status=data.status,
        teacher_id=user.id,
    )
