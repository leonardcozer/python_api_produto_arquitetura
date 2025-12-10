import logging
from fastapi import FastAPI
from config.config import settings

logger = logging.getLogger(__name__)


def create_server() -> FastAPI:
    """Cria e configura a aplicação FastAPI"""
    app = FastAPI(
        title="API Produto",
        description="API para gerenciamento de produtos",
        version="1.0.0",
        debug=settings.debug,
    )
    
    logger.info(f"FastAPI server created - Environment: {settings.environment}")
    return app


def configure_logging(log_level: str = "INFO"):
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger.info(f"Logging configured with level: {log_level}")
