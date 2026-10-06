from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Integer, Text

from app.models.base import Base


class GradeORM(Base):
    __tablename__ = "grades"
    __table_args__ = (
        UniqueConstraint("lesson_id", "student_id", name="uq_grade_lesson_student"),
        CheckConstraint("grade_value BETWEEN 2 AND 5", name="ck_grade_value"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    grade_value: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    
    lesson: Mapped["LessonORM"] = relationship("LessonORM", back_populates="grades")
    student: Mapped["StudentsORM"] = relationship("StudentsORM", back_populates="grades")
