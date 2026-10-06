from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

from app.models.base import Base


class GroupORM(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    faculty: Mapped[str] = mapped_column(String(100), nullable=False)

    
    students: Mapped[list["StudentsORM"]] = relationship(
        "StudentsORM", back_populates="group", cascade="all, delete-orphan"
    )
    lessons: Mapped[list["LessonORM"]] = relationship(
        "LessonORM", back_populates="group", cascade="all, delete-orphan"
    )
