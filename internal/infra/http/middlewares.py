import logging
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggerMiddleware(BaseHTTPMiddleware):
    """Middleware para registrar todas as requisições HTTP"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Adiciona o request_id ao estado da requisição
        request.state.request_id = request_id
        
        # Log da requisição
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        response = await call_next(request)
        
        # Log da resposta
        process_time = time.time() - start_time
        logger.info(
            f"[{request_id}] Status: {response.status_code} - "
            f"Duration: {process_time:.3f}s"
        )
        
        # Adiciona headers personalizados
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


def configure_cors(app, cors_config):
    """Configura CORS na aplicação"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.allow_origins,
        allow_credentials=cors_config.allow_credentials,
        allow_methods=cors_config.allow_methods,
        allow_headers=cors_config.allow_headers,
    )
    logger.info("CORS configured successfully")


def configure_middlewares(app):
    """Configura todos os middlewares da aplicação"""
    app.add_middleware(LoggerMiddleware)
    logger.info("Middlewares configured successfully")
