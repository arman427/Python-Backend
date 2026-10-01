from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from app.models.base import Base


class GroupORM(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    faculty: Mapped[str] = mapped_column(String(100), nullable=False)
