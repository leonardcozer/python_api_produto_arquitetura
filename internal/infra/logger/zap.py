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


class LokiHandlerWithLogging(logging.Handler):
    """
    Handler customizado do Loki que adiciona logging sobre o envio de logs
    """
    def __init__(self, loki_handler, loki_url: str, loki_job: str):
        super().__init__()
        self.loki_handler = loki_handler
        self.loki_url = loki_url
        self.loki_job = loki_job
        self.logs_sent = 0
        self.logs_failed = 0
        self.logger = logging.getLogger("loki_sender")
        # Configura o logger para não criar loop infinito
        self.logger.propagate = False
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)
        
    def emit(self, record):
        """Envia o log para o Loki e registra informações sobre o envio"""
        try:
            # Envia o log para o Loki usando o handler original
            self.loki_handler.emit(record)
            
            # Incrementa contador
            self.logs_sent += 1
            
            # Log informativo sobre o envio (a cada 10 logs, no primeiro log, ou em nível DEBUG)
            if self.logs_sent == 1 or self.logs_sent % 10 == 0 or record.levelno == logging.DEBUG:
                endpoint = f"{self.loki_url}/loki/api/v1/push"
                self.logger.info(
                    f"📤 POST para Grafana/Loki | "
                    f"Endpoint: {endpoint} | "
                    f"JOB: {self.loki_job} | "
                    f"Total enviados: {self.logs_sent} | "
                    f"Level: {record.levelname} | "
                    f"Logger: {record.name} | "
                    f"Mensagem: {record.getMessage()[:50]}..."
                )
        except Exception as e:
            # Log de erro se falhar o envio
            self.logs_failed += 1
            endpoint = f"{self.loki_url}/loki/api/v1/push"
            self.logger.error(
                f"❌ Erro no POST para Grafana/Loki | "
                f"Endpoint: {endpoint} | "
                f"JOB: {self.loki_job} | "
                f"Erro: {str(e)} | "
                f"Total falhas: {self.logs_failed}"
            )
    
    def setLevel(self, level):
        """Define o nível do handler"""
        super().setLevel(level)
        self.loki_handler.setLevel(level)
    
    def setFormatter(self, formatter):
        """Define o formatador"""
        super().setFormatter(formatter)
        self.loki_handler.setFormatter(formatter)


def configure_logging(
    log_level: str = "INFO",
    loki_url: Optional[str] = None,
    loki_job: Optional[str] = None,
    loki_enabled: bool = True
) -> bool:
    """
    Configura o sistema de logging da aplicação com suporte ao Loki
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        loki_url: URL do servidor Loki (ex: http://172.30.0.45:3100)
        loki_job: Nome do job para identificação no Loki
        loki_enabled: Se True, habilita o envio de logs para o Loki
    
    Returns:
        bool: True se o Loki foi configurado com sucesso, False caso contrário
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
    loki_connected = False
    if loki_enabled and loki_url and loki_job:
        try:
            from python_logging_loki import LokiHandler
            
            # Cria o handler do Loki
            loki_handler_base = LokiHandler(
                url=f"{loki_url}/loki/api/v1/push",
                tags={"job": loki_job, "application": "produto-api"},
                version="1"
            )
            loki_handler_base.setLevel(level)
            
            # Formato para Loki
            loki_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt=date_format
            )
            loki_handler_base.setFormatter(loki_formatter)
            
            # Cria handler customizado com logging sobre envio
            loki_handler = LokiHandlerWithLogging(
                loki_handler=loki_handler_base,
                loki_url=loki_url,
                loki_job=loki_job
            )
            loki_handler.setLevel(level)
            loki_handler.setFormatter(loki_formatter)
            
            root_logger.addHandler(loki_handler)
            
            # Log inicial sobre configuração do Loki
            logger = logging.getLogger(__name__)
            endpoint = f"{loki_url}/loki/api/v1/push"
            try:
                import python_logging_loki
                loki_version = getattr(python_logging_loki, '__version__', 'desconhecida')
            except:
                loki_version = '0.3.1'
            
            logger.info("=" * 80)
            logger.info("📡 CONFIGURAÇÃO DO GRAFANA/LOKI")
            logger.info(f"   ✅ python-logging-loki v{loki_version} importado com sucesso")
            logger.info(f"   🔗 Endpoint: {endpoint}")
            logger.info(f"   📋 JOB: {loki_job}")
            logger.info(f"   📤 Método: POST")
            logger.info(f"   🏷️  Tags: job={loki_job}, application=produto-api")
            logger.info("   ✅ Handler configurado e pronto para enviar logs")
            logger.info("=" * 80)
            
            # Configura uma função auxiliar para garantir que novos loggers também usem o Loki
            # Isso é importante para loggers criados pelo uvicorn após a inicialização
            def configure_logger_for_loki(logger_name: str):
                """Configura um logger específico para usar o Loki"""
                logger_instance = logging.getLogger(logger_name)
                logger_instance.setLevel(level)
                # Remove handlers existentes
                for handler in logger_instance.handlers[:]:
                    logger_instance.removeHandler(handler)
                # Adiciona nossos handlers
                logger_instance.addHandler(console_handler)
                # Cria novo handler do Loki para este logger específico
                loki_handler_for_logger = LokiHandlerWithLogging(
                    loki_handler=loki_handler_base,
                    loki_url=loki_url,
                    loki_job=loki_job
                )
                loki_handler_for_logger.setLevel(level)
                loki_handler_for_logger.setFormatter(loki_formatter)
                logger_instance.addHandler(loki_handler_for_logger)
                logger_instance.propagate = False
            
            # Cria uma função que será chamada quando o uvicorn iniciar
            # para configurar os loggers do uvicorn
            def ensure_uvicorn_loggers_configured():
                """Garante que os loggers do uvicorn estão configurados para o Loki"""
                logger_names_to_configure = [
                    "uvicorn",
                    "uvicorn.access",
                    "uvicorn.error",
                    "fastapi",
                ]
                for logger_name in logger_names_to_configure:
                    logger_instance = logging.getLogger(logger_name)
                    # Se o logger tem handlers mas não tem o nosso handler do Loki
                    has_loki = any(
                        isinstance(h, LokiHandlerWithLogging) 
                        for h in logger_instance.handlers
                    )
                    if not has_loki:
                        configure_logger_for_loki(logger_name)
            
            # Armazena a função para ser chamada depois
            # Isso será útil quando o uvicorn iniciar
            root_logger._ensure_uvicorn_loggers_configured = ensure_uvicorn_loggers_configured
            
            loki_connected = True
            
        except ImportError as e:
            logger = logging.getLogger(__name__)
            logger.warning(
                f"⚠️ python-logging-loki não pode ser importado. "
                f"Erro: {str(e)} | "
                f"Python path: {sys.path[:3]} | "
                f"Tente: pip install python-logging-loki==0.3.1"
            )
            # Tenta verificar se o pacote está instalado
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "list"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "python-logging-loki" in result.stdout:
                    logger.warning("   ℹ️ O pacote está listado no pip, mas não pode ser importado. Pode ser um problema de path.")
            except Exception:
                pass
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Erro ao configurar Loki handler: {str(e)} | Tipo: {type(e).__name__}")
    else:
        logger = logging.getLogger(__name__)
        if not loki_enabled:
            logger.info("ℹ️ Loki desabilitado")
        else:
            logger.warning("⚠️ Loki não configurado (URL ou JOB não fornecidos)")
    
    return loki_connected
