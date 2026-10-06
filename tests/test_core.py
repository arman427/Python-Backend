import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.core.security import get_password_hash, verify_password
from app.main import app
from app.models.enum import AttendanceStatus
from app.schemas.grade import GradeCreate
from app.services.grade import GradeService


def test_password_is_hashed_and_verifiable():
    hashed = get_password_hash("SafePassword123!")
    assert hashed != "SafePassword123!"
    assert verify_password("SafePassword123!", hashed)
    assert not verify_password("wrong-password", hashed)


def test_required_openapi_routes_and_oauth2_are_present():
    schema = app.openapi()
    required = {
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/api/v1/teacher/lessons",
        "/api/v1/attendance/swipe/lessons/{lesson_id}/swipe-queue",
        "/api/v1/attendance/qr/lessons/{lesson_id}/qr/generate",
        "/api/v1/grades/lessons/{lesson_id}/grades",
        "/api/v1/reports/lessons/{lesson_id}/summary",
    }
    assert required <= set(schema["paths"])
    oauth = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]
    assert oauth["flows"]["password"]["tokenUrl"] == "/api/v1/auth/login"


@pytest.mark.asyncio
async def test_absent_student_cannot_be_graded():
    teacher_id = uuid.uuid4()
    lesson = SimpleNamespace(id=1, teacher_id=teacher_id, group_id=1)
    student = SimpleNamespace(id=1, group_id=1)
    attendance = SimpleNamespace(status=AttendanceStatus.ABSENT)
    service = GradeService(
        grade_repo=AsyncMock(),
        attendance_repo=AsyncMock(),
        lesson_repo=AsyncMock(),
        student_repo=AsyncMock(),
    )
    service.lesson_repo.get_by_id.return_value = lesson
    service.student_repo.get_by_id.return_value = student
    service.attendance_repo.get_by_lesson_and_student.return_value = attendance

    with pytest.raises(HTTPException) as error:
        await service.create_grade(1, GradeCreate(student_id=1, grade_value=5), teacher_id)
    assert error.value.status_code == 400
    assert "отсутствующему" in error.value.detail
