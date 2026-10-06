# Backend системы посещаемости ВСПК

FastAPI + PostgreSQL + SQLAlchemy 2 + Alembic. Реализованы JWT-авторизация, занятия, свайп-посещаемость, два QR-сценария, оценки только для присутствующих, статистика и CSV для Excel.

## Запуск

```bash
docker compose up --build
```

После запуска:
- Swagger: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/api/v1/openapi.json
- Health: http://localhost:8000/health
- PostgreSQL с хоста: localhost:15432

Миграции и idempotent seed выполняются автоматически при старте API.

## Тестовые аккаунты

| Роль | Логин | Пароль |
|---|---|---|
| Преподаватель | `teacher@example.com` | `Teacher123!` |
| Студент | `student01@example.com` | `Student123!` |
| Администратор | `admin@example.com` | `Admin123!` |

В Swagger нажмите **Authorize**, введите email преподавателя в поле `username` и пароль. Эндпоинт `/api/v1/auth/login` также принимает JSON с полями `email` и `password`.

## Типичный сценарий проверки

1. Авторизоваться преподавателем.
2. `GET /api/v1/teacher/lessons?period=week` и взять `id` активного занятия.
3. `GET /api/v1/attendance/swipe/lessons/{id}/swipe-queue`.
4. `POST /api/v1/attendance/swipe/lessons/{id}/swipe` со статусом `PRESENT`.
5. `POST /api/v1/grades/lessons/{id}/grades` для отмеченного студента.
6. `GET /api/v1/reports/lessons/{id}/summary`.

Для студенческого QR авторизуйтесь студентом и вызовите `GET /api/v1/attendance/qr/student/qr/my-code`.

## Локальные команды

```bash
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
pytest -q
```

Секреты и URL БД задаются через `.env`; перед production обязательно смените `SECRET_KEY` и пароль PostgreSQL.

## Документация для передачи

- `FRONTEND_API.md` — контракт и примеры для frontend.
- `PROJECT_EXPLANATION.md` — архитектура и сценарий объяснения проекта преподавателю.
