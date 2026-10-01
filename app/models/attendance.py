from datetime import datetime

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime

from app.models.base import Base
from app.models.enum import AttendanceMethod, AttendanceStatus


class AttendanceORM(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(
        SQLAlchemyEnum(AttendanceStatus), nullable=False
    )
    method: Mapped[AttendanceMethod] = mapped_column(
        SQLAlchemyEnum(AttendanceMethod), nullable=False
    )
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
