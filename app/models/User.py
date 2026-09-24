from datetime import datetime

from sqlalchemy import DateTime, String, Text, func

from app.models.Base import Base, IdMixin
from sqlalchemy.orm import Mapped, mapped_column


class User(Base, IdMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(
        String(100), default="Гость", server_default="Гость"
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)

    refresh_token: Mapped[str | None] = mapped_column(
        String(512), nullable=True, default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
