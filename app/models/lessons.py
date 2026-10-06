import uuid
from datetime import datetime

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, String

from app.models.base import Base
from app.models.enum import LessonStatus


class LessonORM(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False)
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="RESTRICT"), nullable=False)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    classroom: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[LessonStatus] = mapped_column(
        SQLAlchemyEnum(LessonStatus), nullable=False, default=LessonStatus.PLANNED
    )

    
    teacher: Mapped["UserORM"] = relationship("UserORM", back_populates="lessons_as_teacher")
    group: Mapped["GroupORM"] = relationship("GroupORM", back_populates="lessons")
    attendance_records: Mapped[list["AttendanceORM"]] = relationship(
        "AttendanceORM", back_populates="lesson", cascade="all, delete-orphan"
    )
    grades: Mapped[list["GradeORM"]] = relationship(
        "GradeORM", back_populates="lesson", cascade="all, delete-orphan"
    )
    qr_sessions: Mapped[list["QRSessionORM"]] = relationship(
        "QRSessionORM", back_populates="lesson", cascade="all, delete-orphan"
    )
