from datetime import datetime

from sqlalchemy import func

from app.models.Base import Base, IdMixin
from sqlalchemy.orm import Mapped, mapped_column

class User(Base, IdMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(default="Гость")
    email: Mapped[str] = mapped_column(unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(nullable=True)
    hashed_password: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )