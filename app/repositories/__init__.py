from app.repositories.user import UserRepository
from app.repositories.lesson import LessonRepository
from app.repositories.student import StudentRepository
from app.repositories.attendance import AttendanceRepository
from app.repositories.grade import GradeRepository
from app.repositories.qr_session import QRSessionRepository
from app.repositories.group import GroupRepository

__all__ = [
    "UserRepository",
    "LessonRepository",
    "StudentRepository",
    "AttendanceRepository",
    "GradeRepository",
    "QRSessionRepository",
    "GroupRepository",
]
