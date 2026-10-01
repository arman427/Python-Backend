import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from app.models.base import Base


class StudentsORM(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    student_card_number: Mapped[str] = mapped_column(String(50), nullable=False)
