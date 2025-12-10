import logging
import sys
from typing import Optional

# Nomes dos loggers
LOGGER_MAIN = "main"
LOGGER_DATABASE = "database"
LOGGER_API = "api"
LOGGER_SERVICE = "service"
LOGGER_REPOSITORY = "repository"


def get_logger(name: str) -> logging.Logger:
    """Obtém um logger configurado"""
    return logging.getLogger(name)


def configure_logging(
    log_level: str = "INFO",
    loki_url: Optional[str] = None,
    loki_job: Optional[str] = None,
    loki_enabled: bool = True
):
    """
    Configura o sistema de logging da aplicação com suporte ao Loki
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        loki_url: URL do servidor Loki (ex: http://172.30.0.45:3100)
        loki_job: Nome do job para identificação no Loki
        loki_enabled: Se True, habilita o envio de logs para o Loki
    """
    # Remove handlers existentes para evitar duplicação
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configura o nível de log
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Formato padrão dos logs
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Handler para console (sempre ativo)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para Loki (se habilitado e configurado)
    if loki_enabled and loki_url and loki_job:
        try:
            from python_logging_loki import LokiHandler
            
            # Cria o handler do Loki
            loki_handler = LokiHandler(
                url=f"{loki_url}/loki/api/v1/push",
                tags={"job": loki_job, "application": "produto-api"},
                version="1"
            )
            loki_handler.setLevel(level)
            
            # Formato para Loki (JSON-like)
            loki_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt=date_format
            )
            loki_handler.setFormatter(loki_formatter)
            
            root_logger.addHandler(loki_handler)
            
            logger = logging.getLogger(__name__)
            logger.info(f"✅ Loki handler configurado - URL: {loki_url}, JOB: {loki_job}")
        except ImportError:
            logger = logging.getLogger(__name__)
            logger.warning("⚠️ python-logging-loki não instalado. Instale com: pip install python-logging-loki")
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Erro ao configurar Loki handler: {str(e)}")
    else:
        logger = logging.getLogger(__name__)
        if not loki_enabled:
            logger.info("ℹ️ Loki desabilitado")
        else:
            logger.warning("⚠️ Loki não configurado (URL ou JOB não fornecidos)")
