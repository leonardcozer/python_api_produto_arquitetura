"""
Exception handlers globais para a aplicação FastAPI
"""
import logging
import traceback
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from pkg.apperrors.exceptions import (
    AppError,
    NotFoundError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    InternalServerError
)

logger = logging.getLogger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    Handler para exceções customizadas da aplicação
    """
    logger.warning(
        f"AppError: {exc.__class__.__name__} - {exc.message} | "
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"Request ID: {getattr(request.state, 'request_id', 'N/A')}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "status_code": exc.status_code,
            "path": request.url.path,
            "request_id": getattr(request.state, 'request_id', None)
        }
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler para erros de validação do Pydantic
    """
    errors = exc.errors()
    logger.warning(
        f"Validation error: {errors} | "
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"Request ID: {getattr(request.state, 'request_id', 'N/A')}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Erro de validação dos dados de entrada",
            "details": errors,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "path": request.url.path,
            "request_id": getattr(request.state, 'request_id', None)
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler para exceções HTTP do Starlette/FastAPI
    """
    logger.warning(
        f"HTTPException: {exc.status_code} - {exc.detail} | "
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"Request ID: {getattr(request.state, 'request_id', 'N/A')}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
            "request_id": getattr(request.state, 'request_id', None)
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler genérico para exceções não tratadas.
    Em produção, não expõe detalhes do erro.
    """
    request_id = getattr(request.state, 'request_id', 'N/A')
    
    # Log completo do erro
    logger.error(
        f"Unhandled exception: {exc.__class__.__name__} - {str(exc)} | "
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"Request ID: {request_id} | "
        f"Traceback: {traceback.format_exc()}"
    )
    
    # Em desenvolvimento, mostra mais detalhes
    from config.config import settings
    is_development = settings.environment == "development" or settings.debug
    
    error_detail = {
        "error": "InternalServerError",
        "message": "Erro interno do servidor",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "path": request.url.path,
        "request_id": request_id
    }
    
    # Adiciona detalhes apenas em desenvolvimento
    if is_development:
        error_detail["details"] = {
            "exception_type": exc.__class__.__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc().split('\n')
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_detail
    )


def register_exception_handlers(app):
    """
    Registra todos os exception handlers na aplicação FastAPI
    
    Args:
        app: Instância do FastAPI
    """
    # Handlers específicos (ordem importa - mais específicos primeiro)
    app.add_exception_handler(NotFoundError, app_error_handler)
    app.add_exception_handler(BadRequestError, app_error_handler)
    app.add_exception_handler(UnauthorizedError, app_error_handler)
    app.add_exception_handler(ForbiddenError, app_error_handler)
    app.add_exception_handler(ConflictError, app_error_handler)
    app.add_exception_handler(InternalServerError, app_error_handler)
    app.add_exception_handler(AppError, app_error_handler)
    
    # Handler para validação do Pydantic
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    
    # Handler para HTTPException do Starlette
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Handler genérico (deve ser o último)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("✅ Exception handlers registrados com sucesso")

