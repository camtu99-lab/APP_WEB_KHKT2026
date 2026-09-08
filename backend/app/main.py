import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import auth, users
from app.core.config import settings
from app.core.exceptions import AppError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chemgenie")

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="CHEMGENIE Backend API — nền tảng học tập và luyện thi Hóa học THPT.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.warning("AppError %s: %s (%s)", exc.code, exc.message, request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.code, "message": exc.message}},
    )


@app.get("/health", tags=["system"])
def health_check():
    return {"success": True, "data": {"status": "ok", "app": settings.APP_NAME, "env": settings.ENVIRONMENT}}


app.include_router(auth.router)
app.include_router(users.router)
