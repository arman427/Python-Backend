from datetime import datetime

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Boolean, DateTime, String

from app.models.base import Base
from app.models.enum import QRType


class QRSessionORM(Base):
    __tablename__ = "qr_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    qr_token: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    type: Mapped[QRType] = mapped_column(SQLAlchemyEnum(QRType), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_used: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
