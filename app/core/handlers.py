from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.exceptions import BusinessException


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(BusinessException)
    async def business_exception_handler(_, exc):

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error,
                "message": exc.message,
                "details": exc.details,
            },
        )