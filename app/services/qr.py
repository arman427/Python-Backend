import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from app.models.enum import AttendanceMethod, AttendanceStatus, QRType
from app.core.security import create_token, decode_token
from app.repositories.attendance import AttendanceRepository
from app.repositories.lesson import LessonRepository
from app.repositories.qr_session import QRSessionRepository
from app.repositories.student import StudentRepository
from app.schemas.attendance import AttendanceResponse
from app.schemas.qr_session import QRGenerateResponse, QRStudentMyCode



TEACHER_QR_TTL_SECONDS = 30


STUDENT_QR_TTL_MINUTES = 120


class QRService:
    def __init__(
        self,
        qr_repo: QRSessionRepository,
        attendance_repo: AttendanceRepository,
        lesson_repo: LessonRepository,
        student_repo: StudentRepository,
    ) -> None:
        self.qr_repo = qr_repo
        self.attendance_repo = attendance_repo
        self.lesson_repo = lesson_repo
        self.student_repo = student_repo

    

    async def generate_teacher_qr(
        self,
        lesson_id: int,
        teacher_id: uuid.UUID,
    ) -> QRGenerateResponse:

        lesson = await self.lesson_repo.get_by_id(lesson_id)

        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson.teacher_id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь преподавателем этого занятия",
            )

        
        qr_token = f"qr_{lesson_id}_{secrets.token_urlsafe(32)}"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=TEACHER_QR_TTL_SECONDS)

        qr_session = await self.qr_repo.create(
            lesson_id=lesson_id,
            qr_token=qr_token,
            qr_type=QRType.TEACHER_DYNAMIC,
            expires_at=expires_at,
        )

        return QRGenerateResponse(
            id=qr_session.id,
            lesson_id=qr_session.lesson_id,
            qr_token=qr_session.qr_token,
            type=qr_session.type,
            expires_at=qr_session.expires_at,
            is_used=qr_session.is_used,
        )

    async def student_confirm_qr(
        self,
        qr_token: str,
        user_id: uuid.UUID,
    ) -> AttendanceResponse:

        
        student = await self.student_repo.get_by_user_id(user_id)
        if not student:
            raise HTTPException(
                status_code=404, detail="Профиль студента не найден"
            )

        
        qr_session = await self.qr_repo.get_by_token(qr_token)
        if not qr_session or qr_session.type != QRType.TEACHER_DYNAMIC or qr_session.is_used:
            raise HTTPException(status_code=400, detail="Недействительный QR-код")

        
        now = datetime.now(timezone.utc)
        
        expires_at = qr_session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            raise HTTPException(
                status_code=400, detail="QR-код истёк, попросите преподавателя обновить"
            )

        
        lesson = await self.lesson_repo.get_by_id(qr_session.lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")

        if student.group_id != lesson.group_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не принадлежите к группе этого занятия",
            )

        
        existing = await self.attendance_repo.get_by_lesson_and_student(
            qr_session.lesson_id, student.id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Вы уже отмечены на данном занятии",
            )

        
        attendance = await self.attendance_repo.create(
            lesson_id=qr_session.lesson_id,
            student_id=student.id,
            status=AttendanceStatus.PRESENT,
            method=AttendanceMethod.QR_STUDENT_SCANNED,
        )

        return AttendanceResponse(
            id=attendance.id,
            lesson_id=attendance.lesson_id,
            student_id=attendance.student_id,
            status=attendance.status,
            method=attendance.method,
            marked_at=attendance.marked_at,
        )

    

    async def get_student_personal_qr(
        self, user_id: uuid.UUID
    ) -> QRStudentMyCode:

        student = await self.student_repo.get_by_user_id(user_id)
        if not student:
            raise HTTPException(
                status_code=404, detail="Профиль студента не найден"
            )

        qr_token = create_token(
            {"sub": str(student.id), "type": "student_qr"},
            timedelta(minutes=STUDENT_QR_TTL_MINUTES),
        )

        return QRStudentMyCode(
            qr_token=qr_token,
            student_id=student.id,
            full_name=student.user.full_name if student.user else "—",
        )

    async def teacher_scan_student_qr(
        self,
        qr_token: str,
        lesson_id: int,
        teacher_id: uuid.UUID,
    ) -> AttendanceResponse:

        lesson = await self.lesson_repo.get_by_id(lesson_id)

        if not lesson:
            raise HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson.teacher_id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь преподавателем этого занятия",
            )

        payload = decode_token(qr_token)
        if not payload or payload.get("type") != "student_qr":
            raise HTTPException(status_code=400, detail="Недействительный или истёкший QR-код студента")
        try:
            student_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Некорректный QR-код студента")

        
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Студент не найден")

        if student.group_id != lesson.group_id:
            raise HTTPException(
                status_code=403,
                detail="Студент не принадлежит к группе этого занятия",
            )

        
        existing = await self.attendance_repo.get_by_lesson_and_student(
            lesson_id, student_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Этот студент уже отмечен на данном занятии",
            )

        
        attendance = await self.attendance_repo.create(
            lesson_id=lesson_id,
            student_id=student_id,
            status=AttendanceStatus.PRESENT,
            method=AttendanceMethod.QR_TEACHER_SCANNED,
        )

        return AttendanceResponse(
            id=attendance.id,
            lesson_id=attendance.lesson_id,
            student_id=attendance.student_id,
            status=attendance.status,
            method=attendance.method,
            marked_at=attendance.marked_at,
        )
