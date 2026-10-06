from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.grades import router as grades_router
from app.api.qr import router as qr_router
from app.api.reports import router as reports_router
from app.api.swipe import router as swipe_router
from app.api.teacher import router as teacher_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Система контроля посещаемости и успеваемости",
    description="REST API ВСПК: занятия, посещаемость по свайпам/QR, оценки и отчёты.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth_router, teacher_router, swipe_router, qr_router, grades_router, reports_router):
    app.include_router(router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Ошибка валидации входных данных",
            "errors": [
                {
                    "field": ".".join(str(part) for part in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
                for error in exc.errors()
            ],
        },
    )


@app.get("/health", tags=["Система"], summary="Проверка состояния сервиса")
async def health() -> dict[str, str]:
    return {"status": "ok"}
