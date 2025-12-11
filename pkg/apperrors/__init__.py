"""
Exceções personalizadas da aplicação
"""
from pkg.apperrors.exceptions import (
    AppError,
    NotFoundError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    InternalServerError
)
from pkg.apperrors.exception_handlers import register_exception_handlers

__all__ = [
    "AppError",
    "NotFoundError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "InternalServerError",
    "register_exception_handlers",
]

