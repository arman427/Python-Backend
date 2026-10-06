from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.qr_session import QRSessionORM
from app.models.enum import QRType


class QRSessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_token(self, qr_token: str) -> QRSessionORM | None:
        result = await self.db.execute(
            select(QRSessionORM).where(QRSessionORM.qr_token == qr_token)
        )
        return result.scalar_one_or_none()

    async def get_active_by_lesson(self, lesson_id: int) -> QRSessionORM | None:

        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(QRSessionORM).where(
                QRSessionORM.lesson_id == lesson_id,
                QRSessionORM.is_used == False,
                QRSessionORM.expires_at > now,
                QRSessionORM.type == QRType.TEACHER_DYNAMIC,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        lesson_id: int,
        qr_token: str,
        qr_type: QRType,
        expires_at: datetime,
    ) -> QRSessionORM:
        session = QRSessionORM(
            lesson_id=lesson_id,
            qr_token=qr_token,
            type=qr_type,
            expires_at=expires_at,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def mark_used(self, qr_session: QRSessionORM) -> None:
        qr_session.is_used = True
        await self.db.commit()
