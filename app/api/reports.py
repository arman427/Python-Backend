import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_report_service, require_role
from app.models.enum import Role
from app.models.user import UserORM
from app.schemas.reports import LessonSummaryResponse
from app.services.report import ReportService

router = APIRouter(prefix="/reports", tags=["Отчёты"])
teacher_only = require_role(Role.TEACHER, Role.ADMIN)


@router.get(
    "/lessons/{lesson_id}/summary",
    response_model=LessonSummaryResponse,
    summary="Итоговая статистика занятия",
    description="Процент посетивших, средний балл и детализация по студентам.",
)
async def lesson_summary(
    lesson_id: int,
    user: Annotated[UserORM, Depends(teacher_only)],
    service: Annotated[ReportService, Depends(get_report_service)],
) -> LessonSummaryResponse:
    return await service.get_lesson_summary(lesson_id, user.id)


@router.get(
    "/export/excel",
    summary="Экспорт ведомости в CSV",
    description="CSV в UTF-8 с BOM открывается в Excel. Передайте lesson_id.",
    responses={200: {"content": {"text/csv": {}}}},
)
async def export_excel(
    lesson_id: int,
    user: Annotated[UserORM, Depends(teacher_only)],
    service: Annotated[ReportService, Depends(get_report_service)],
) -> StreamingResponse:
    report = await service.get_lesson_summary(lesson_id, user.id)
    grades = {item.student_id: item.grade_value for item in report.grades}
    stream = io.StringIO()
    writer = csv.writer(stream, delimiter=";")
    writer.writerow(["Студент", "Статус", "Способ отметки", "Оценка"])
    for item in report.attendance:
        writer.writerow([
            item.full_name,
            item.status.value,
            item.method.value if item.method else "—",
            grades.get(item.student_id, ""),
        ])
    payload = "\ufeff" + stream.getvalue()
    headers = {"Content-Disposition": f'attachment; filename="lesson_{lesson_id}.csv"'}
    return StreamingResponse(iter([payload]), media_type="text/csv; charset=utf-8", headers=headers)
