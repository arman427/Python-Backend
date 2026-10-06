import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

from app.models.base import Base


class StudentsORM(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_students_user_id"),
        UniqueConstraint("student_card_number", name="uq_students_card_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    student_card_number: Mapped[str] = mapped_column(String(50), nullable=False)

    
    user: Mapped["UserORM"] = relationship("UserORM", back_populates="student_profile")
    group: Mapped["GroupORM"] = relationship("GroupORM", back_populates="students")
    attendance_records: Mapped[list["AttendanceORM"]] = relationship(
        "AttendanceORM", back_populates="student"
    )
    grades: Mapped[list["GradeORM"]] = relationship(
        "GradeORM", back_populates="student"
    )
