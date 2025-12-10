import logging

# Nomes dos loggers
LOGGER_MAIN = "main"
LOGGER_DATABASE = "database"
LOGGER_API = "api"
LOGGER_SERVICE = "service"
LOGGER_REPOSITORY = "repository"


def get_logger(name: str) -> logging.Logger:
    """Obtém um logger configurado"""
    return logging.getLogger(name)


def configure_logging(log_level: str = "INFO"):
    """Configura o sistema de logging da aplicação"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
