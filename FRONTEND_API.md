# Контракт API для frontend

## Подключение

- Локальный base URL: `http://127.0.0.1:8000/api/v1`
- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/api/v1/openapi.json`
- Все даты приходят в ISO 8601, например `2026-10-06T12:00:00Z`.
- Защищённые запросы должны содержать `Authorization: Bearer <access_token>`.

Frontend может сгенерировать типизированный API-клиент напрямую из OpenAPI JSON.

## Тестовые пользователи

| Роль | Email | Пароль |
|---|---|---|
| Преподаватель | `teacher@example.com` | `Teacher123!` |
| Студент | `student01@example.com` | `Student123!` |
| Администратор | `admin@example.com` | `Admin123!` |

## Авторизация

### `POST /auth/login`

JSON-запрос:

```json
{
  "email": "teacher@example.com",
  "password": "Teacher123!"
}
```

Ответ:

```json
{
  "access_token": "JWT",
  "refresh_token": "JWT",
  "token_type": "bearer",
  "id": "UUID",
  "full_name": "Иванов Иван Иванович",
  "email": "teacher@example.com",
  "role": "TEACHER",
  "avatar_url": null
}
```

`access_token` хранится на стороне клиента и отправляется в Bearer-заголовке. При его истечении вызывается `POST /auth/refresh`:

```json
{
  "refresh_token": "JWT"
}
```

### Остальные auth endpoints

| Метод | Путь | Назначение |
|---|---|---|
| POST | `/auth/register` | Регистрация пользователя |
| GET | `/auth/me` | Профиль текущего пользователя |
| POST | `/auth/refresh` | Обновление пары токенов |

## Занятия преподавателя

| Метод | Путь | Данные |
|---|---|---|
| GET | `/teacher/lessons?period=week` | Занятия на неделю; также поддерживается `today` |
| GET | `/teacher/lessons/{lesson_id}/students` | Студенты группы занятия |
| POST | `/teacher/lessons` | Создание занятия |
| PATCH | `/teacher/lessons/{lesson_id}/status` | Изменение статуса занятия |

Создание занятия:

```json
{
  "subject_name": "Информатика",
  "group_id": 1,
  "date_time": "2026-10-07T09:00:00Z",
  "classroom": "201"
}
```

Изменение статуса:

```json
{
  "status": "ACTIVE"
}
```

Статусы: `PLANNED`, `ACTIVE`, `FINISHED`.

## Посещаемость: свайпы

### `GET /attendance/swipe/lessons/{lesson_id}/swipe-queue`

Возвращает неотмеченных студентов:

```json
{
  "students": [
    {
      "student_id": 1,
      "full_name": "Студент 01",
      "avatar_url": null,
      "student_card_number": "CARD-0001"
    }
  ],
  "total_count": 15
}
```

### `POST /attendance/swipe/lessons/{lesson_id}/swipe`

```json
{
  "student_id": 1,
  "status": "PRESENT"
}
```

Для свайпа разрешены `PRESENT` и `ABSENT`. Ответ содержит следующего студента и `remaining_count`.

## Посещаемость: QR

| Сценарий | Метод и путь | Кто вызывает |
|---|---|---|
| Учитель показывает динамический QR | POST `/attendance/qr/lessons/{lesson_id}/qr/generate` | Преподаватель |
| Студент подтверждает QR учителя | POST `/attendance/qr/student/qr/confirm` | Студент |
| Студент получает личный QR | GET `/attendance/qr/student/qr/my-code` | Студент |
| Учитель сканирует QR студента | POST `/attendance/qr/teacher/qr/scan-student` | Преподаватель |

Подтверждение QR учителя:

```json
{
  "qr_token": "TOKEN",
  "latitude": 48.708,
  "longitude": 44.513
}
```

Сканирование личного QR студента:

```json
{
  "qr_token": "TOKEN",
  "lesson_id": 1
}
```

Динамический QR учителя действует 30 секунд. Личный QR студента подписан JWT и действует 120 минут.

## Оценки

| Метод | Путь | Назначение |
|---|---|---|
| POST | `/grades/lessons/{lesson_id}/grades` | Выставить оценку |
| GET | `/grades/lessons/{lesson_id}/grades` | Получить оценки занятия |

```json
{
  "student_id": 1,
  "grade_value": 5,
  "comment": "Отличная работа"
}
```

Допустимы оценки 2–5. Оценка создаётся только при посещаемости `PRESENT` или `LATE`. Повторная оценка за то же занятие запрещена.

## Отчёты

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/reports/lessons/{lesson_id}/summary` | Посещаемость, средний балл и детализация |
| GET | `/reports/export/excel?lesson_id=1` | CSV-ведомость, совместимая с Excel |

## Обработка ошибок

Backend возвращает стандартные HTTP-коды:

- `400` — нарушено бизнес-правило;
- `401` — нет или истёк JWT;
- `403` — не подходит роль или пользователь не владелец занятия;
- `404` — объект не найден;
- `409` — конфликт данных;
- `422` — неправильное тело или параметры запроса.

Основной текст ошибки находится в `detail`:

```json
{
  "detail": "Невозможно выставить оценку отсутствующему студенту"
}
```
