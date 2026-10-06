
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.core.security import get_password_hash
from app.db.db import AsyncSessionLocal
from app.models.enum import LessonStatus, Role
from app.models.groups import GroupORM
from app.models.lessons import LessonORM
from app.models.students import StudentsORM
from app.models.user import UserORM

TEACHER_EMAIL = "teacher@example.com"
DEFAULT_PASSWORD = "Teacher123!"
STUDENT_PASSWORD = "Student123!"


async def get_or_create_user(session, email: str, name: str, role: Role, password: str) -> UserORM:
    user = (await session.execute(select(UserORM).where(UserORM.email == email))).scalar_one_or_none()
    if user:
        return user
    user = UserORM(email=email, full_name=name, role=role, hashed_password=get_password_hash(password))
    session.add(user)
    await session.flush()
    return user


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        teacher = await get_or_create_user(session, TEACHER_EMAIL, "Иванов Иван Иванович", Role.TEACHER, DEFAULT_PASSWORD)
        await get_or_create_user(session, "admin@example.com", "Администратор", Role.ADMIN, "Admin123!")

        groups = []
        for name, faculty in (("ВСПК-201", "Информационные системы"), ("ВСПК-202", "Педагогика")):
            group = (await session.execute(select(GroupORM).where(GroupORM.name == name))).scalar_one_or_none()
            if not group:
                group = GroupORM(name=name, faculty=faculty)
                session.add(group)
                await session.flush()
            groups.append(group)

        for index in range(1, 31):
            email = f"student{index:02d}@example.com"
            user = await get_or_create_user(session, email, f"Студент {index:02d}", Role.STUDENT, STUDENT_PASSWORD)
            exists = (await session.execute(select(StudentsORM).where(StudentsORM.user_id == user.id))).scalar_one_or_none()
            if not exists:
                session.add(StudentsORM(
                    user_id=user.id,
                    group_id=groups[0].id if index <= 15 else groups[1].id,
                    student_card_number=f"CARD-{index:04d}",
                ))

        lesson_count = await session.scalar(select(func.count(LessonORM.id)).where(LessonORM.teacher_id == teacher.id))
        if not lesson_count:
            subjects = ["Информатика", "Математика", "Русский язык", "Педагогика", "История"]
            now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            for index, subject in enumerate(subjects):
                session.add(LessonORM(
                    subject_name=subject,
                    teacher_id=teacher.id,
                    group_id=groups[index % 2].id,
                    date_time=now + timedelta(days=index, hours=1),
                    classroom=f"{201 + index}",
                    status=LessonStatus.ACTIVE if index == 0 else LessonStatus.PLANNED,
                ))
        await session.commit()
    print("Seed готов: teacher@example.com / Teacher123!, student01@example.com / Student123!")


if __name__ == "__main__":
    asyncio.run(seed())
