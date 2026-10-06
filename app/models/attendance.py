from datetime import datetime

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from app.models.base import Base
from app.models.enum import AttendanceMethod, AttendanceStatus


class AttendanceORM(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("lesson_id", "student_id", name="uq_attendance_lesson_student"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(
        SQLAlchemyEnum(AttendanceStatus), nullable=False
    )
    method: Mapped[AttendanceMethod] = mapped_column(
        SQLAlchemyEnum(AttendanceMethod), nullable=False
    )
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    
    lesson: Mapped["LessonORM"] = relationship("LessonORM", back_populates="attendance_records")
    student: Mapped["StudentsORM"] = relationship("StudentsORM", back_populates="attendance_records")
