from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_qr_service, require_role
from app.models.enum import Role
from app.models.user import UserORM
from app.schemas.attendance import AttendanceResponse
from app.schemas.qr_session import (
    QRGenerateResponse,
    QRStudentConfirm,
    QRStudentMyCode,
    QRTeacherScanRequest,
)
from app.services.qr import QRService

router = APIRouter(prefix="/attendance/qr", tags=["Посещаемость — QR-код"])

get_teacher_user = require_role(Role.TEACHER, Role.ADMIN)
get_student_user = require_role(Role.STUDENT)





@router.post(
    "/lessons/{lesson_id}/qr/generate",
    response_model=QRGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Сгенерировать QR-код для занятия",
    description="Преподаватель генерирует временный QR-код (живёт ~30 сек). "
    "Студенты сканируют его для подтверждения присутствия.",
)
async def generate_teacher_qr(
    lesson_id: int,
    user: Annotated[UserORM, Depends(get_teacher_user)],
    service: Annotated[QRService, Depends(get_qr_service)],
) -> QRGenerateResponse:
    return await service.generate_teacher_qr(
        lesson_id=lesson_id,
        teacher_id=user.id,
    )


@router.post(
    "/student/qr/confirm",
    response_model=AttendanceResponse,
    summary="Студент подтверждает присутствие по QR",
    description="Студент сканирует QR-код, показанный преподавателем, "
    "и отправляет токен для подтверждения присутствия.",
)
async def student_confirm_qr(
    data: QRStudentConfirm,
    user: Annotated[UserORM, Depends(get_student_user)],
    service: Annotated[QRService, Depends(get_qr_service)],
) -> AttendanceResponse:
    return await service.student_confirm_qr(
        qr_token=data.qr_token,
        user_id=user.id,
    )





@router.get(
    "/student/qr/my-code",
    response_model=QRStudentMyCode,
    summary="Получить персональный QR-код студента",
    description="Студент получает свой персональный QR-код для показа преподавателю.",
)
async def get_student_qr(
    user: Annotated[UserORM, Depends(get_student_user)],
    service: Annotated[QRService, Depends(get_qr_service)],
) -> QRStudentMyCode:
    return await service.get_student_personal_qr(user_id=user.id)


@router.post(
    "/teacher/qr/scan-student",
    response_model=AttendanceResponse,
    summary="Учитель сканирует QR-код студента",
    description="Преподаватель сканирует персональный QR-код студента "
    "на занятии для фиксации присутствия.",
)
async def teacher_scan_student_qr(
    data: QRTeacherScanRequest,
    user: Annotated[UserORM, Depends(get_teacher_user)],
    service: Annotated[QRService, Depends(get_qr_service)],
) -> AttendanceResponse:
    return await service.teacher_scan_student_qr(
        qr_token=data.qr_token,
        lesson_id=data.lesson_id,
        teacher_id=user.id,
    )
