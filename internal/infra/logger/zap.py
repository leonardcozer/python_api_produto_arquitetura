import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Optional
from queue import Queue
from threading import Thread

# Nomes dos loggers
LOGGER_MAIN = "main"
LOGGER_DATABASE = "database"
LOGGER_API = "api"
LOGGER_SERVICE = "service"
LOGGER_REPOSITORY = "repository"


def get_logger(name: str) -> logging.Logger:
    """Obtém um logger configurado"""
    return logging.getLogger(name)


class LokiHandler(logging.Handler):
    """
    Handler customizado que envia logs diretamente para o Grafana/Loki via POST
    """
    def __init__(self, loki_url: str, loki_job: str, batch_size: int = 10, timeout: int = 5):
        super().__init__()
        self.loki_url = loki_url.rstrip('/')
        self.loki_endpoint = f"{self.loki_url}/loki/api/v1/push"
        self.loki_job = loki_job
        self.batch_size = batch_size
        self.timeout = timeout
        self.logs_sent = 0
        self.logs_failed = 0
        self.log_queue = Queue()
        self.batch = []
        self.last_send = time.time()
        self._shutdown = False
        self._shutdown_event = None
        
        # Logger para informações sobre envio (sem loop infinito)
        self.sender_logger = logging.getLogger("loki_sender")
        self.sender_logger.propagate = False
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.sender_logger.addHandler(console_handler)
        self.sender_logger.setLevel(logging.INFO)
        
        # Thread para processar batch de logs (não é daemon para permitir graceful shutdown)
        self.worker_thread = Thread(target=self._process_batch, daemon=False)
        self.worker_thread.start()
        
    def _format_log_entry(self, record: logging.LogRecord) -> dict:
        """Formata um log record para o formato do Loki"""
        # Formata a mensagem
        try:
            message = self.format(record)
        except Exception:
            message = record.getMessage()
        
        # Converte timestamp para nanosegundos (Loki requer nanosegundos)
        timestamp_ns = int(record.created * 1_000_000_000)
        
        # Tags/Labels para o Loki
        labels = {
            "job": self.loki_job,
            "application": "produto-api",
            "level": record.levelname.lower(),
            "logger": record.name,
        }
        
        return {
            "stream": labels,
            "values": [[str(timestamp_ns), message]]
        }
    
    def _send_to_loki(self, entries: list) -> bool:
        """Envia um batch de logs para o Loki"""
        if not entries:
            return True
        
        try:
            import requests
            
            # Formata o payload no formato esperado pelo Loki
            payload = {
                "streams": entries
            }
            
            # Faz o POST para o Loki
            response = requests.post(
                self.loki_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code in [200, 204]:
                return True
            else:
                self.sender_logger.warning(
                    f"⚠️ Loki retornou status {response.status_code}: {response.text[:100]}"
                )
                return False
                
        except ImportError:
            self.sender_logger.error("❌ Biblioteca 'requests' não está instalada")
            return False
        except Exception as e:
            self.sender_logger.error(f"❌ Erro ao enviar para Loki: {str(e)}")
            return False
    
    def _process_batch(self):
        """Processa batch de logs em background"""
        # Importa métricas do Prometheus
        try:
            from internal.infra.metrics.prometheus import (
                loki_logs_sent_total,
                loki_logs_failed_total,
            )
            METRICS_AVAILABLE = True
        except ImportError:
            METRICS_AVAILABLE = False
        
        while not self._shutdown:
            try:
                # Coleta logs do queue
                entries = []
                start_time = time.time()
                
                # Espera até ter batch_size logs ou timeout de 5 segundos
                while len(entries) < self.batch_size and (time.time() - start_time) < 5 and not self._shutdown:
                    try:
                        entry = self.log_queue.get(timeout=1)
                        entries.append(entry)
                    except:
                        break
                
                # Se tem logs, envia
                if entries:
                    if self._send_to_loki(entries):
                        self.logs_sent += len(entries)
                        
                        # Coleta métricas do Prometheus
                        if METRICS_AVAILABLE:
                            for entry in entries:
                                # Extrai level e logger do entry (armazenados no emit)
                                level = entry.get('_record_level', 'unknown')
                                logger_name = entry.get('_record_logger', 'unknown')
                                loki_logs_sent_total.labels(
                                    level=level,
                                    logger=logger_name
                                ).inc()
                        
                        if self.logs_sent % 10 == 0 or len(entries) > 0:
                            self.sender_logger.info(
                                f"📤 POST para Grafana/Loki | "
                                f"Endpoint: {self.loki_endpoint} | "
                                f"JOB: {self.loki_job} | "
                                f"Total enviados: {self.logs_sent} | "
                                f"Batch: {len(entries)} logs"
                            )
                    else:
                        self.logs_failed += len(entries)
                        
                        # Coleta métricas de falhas
                        if METRICS_AVAILABLE:
                            loki_logs_failed_total.inc(len(entries))
                
                # Se está em shutdown e não há mais logs, sai do loop
                if self._shutdown and self.log_queue.empty():
                    break
                        
            except Exception as e:
                if not self._shutdown:
                    self.sender_logger.error(f"❌ Erro no processamento de batch: {str(e)}")
                    time.sleep(1)
        
        # Envia logs restantes antes de encerrar
        self._flush_remaining_logs(METRICS_AVAILABLE)
        self.sender_logger.info(f"🛑 Loki handler encerrado. Total enviados: {self.logs_sent}, Falhas: {self.logs_failed}")
    
    def _flush_remaining_logs(self, metrics_available: bool = False):
        """Envia logs restantes na queue antes de encerrar"""
        remaining_entries = []
        try:
            # Coleta todos os logs restantes da queue
            while not self.log_queue.empty():
                try:
                    entry = self.log_queue.get_nowait()
                    remaining_entries.append(entry)
                except:
                    break
            
            # Envia em batch
            if remaining_entries:
                self.sender_logger.info(f"📤 Enviando {len(remaining_entries)} logs restantes antes do shutdown...")
                if self._send_to_loki(remaining_entries):
                    self.logs_sent += len(remaining_entries)
                    if metrics_available:
                        for entry in remaining_entries:
                            level = entry.get('_record_level', 'unknown')
                            logger_name = entry.get('_record_logger', 'unknown')
                            try:
                                from internal.infra.metrics.prometheus import loki_logs_sent_total
                                loki_logs_sent_total.labels(level=level, logger=logger_name).inc()
                            except:
                                pass
                else:
                    self.logs_failed += len(remaining_entries)
        except Exception as e:
            self.sender_logger.error(f"❌ Erro ao fazer flush de logs: {str(e)}")
    
    def shutdown(self, timeout: float = 10.0):
        """
        Encerra o handler de forma graciosa, aguardando processamento de logs pendentes
        
        Args:
            timeout: Tempo máximo (em segundos) para aguardar o processamento
        """
        if self._shutdown:
            return
        
        self.sender_logger.info("🛑 Iniciando graceful shutdown do Loki handler...")
        self._shutdown = True
        
        # Aguarda a thread terminar ou timeout
        self.worker_thread.join(timeout=timeout)
        
        if self.worker_thread.is_alive():
            self.sender_logger.warning(f"⚠️ Thread do Loki não terminou em {timeout}s, forçando encerramento")
        else:
            self.sender_logger.info("✅ Loki handler encerrado com sucesso")
    
    def emit(self, record: logging.LogRecord):
        """Adiciona o log ao queue para envio"""
        try:
            # Formata o log para o formato do Loki
            entry = self._format_log_entry(record)
            # Armazena informações do record no entry para uso nas métricas
            entry['_record_level'] = record.levelname.lower()
            entry['_record_logger'] = record.name
            # Adiciona ao queue (não bloqueia)
            self.log_queue.put_nowait(entry)
        except Exception as e:
            # Se falhar, apenas registra o erro sem bloquear
            self.sender_logger.error(f"❌ Erro ao adicionar log ao queue: {str(e)}")


# Armazena referência global do handler do Loki para graceful shutdown
_loki_handler_instance: Optional[LokiHandler] = None


def configure_logging(
    log_level: str = "INFO",
    loki_url: Optional[str] = None,
    loki_job: Optional[str] = None,
    loki_enabled: bool = True
) -> tuple[bool, Optional[LokiHandler]]:
    """
    Configura o sistema de logging da aplicação com suporte ao Loki
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        loki_url: URL do servidor Loki (ex: http://172.30.0.45:3100)
        loki_job: Nome do job para identificação no Loki
        loki_enabled: Se True, habilita o envio de logs para o Loki
    
    Returns:
        tuple: (bool, Optional[LokiHandler]) - (True se configurado, instância do handler)
    """
    global _loki_handler_instance
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
            # Cria o handler customizado do Loki (sem dependência externa)
            loki_handler = LokiHandler(
                loki_url=loki_url,
                loki_job=loki_job,
                batch_size=10,
                timeout=5
            )
            loki_handler.setLevel(level)
            
            # Formato para Loki
            loki_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt=date_format
            )
            loki_handler.setFormatter(loki_formatter)
            
            root_logger.addHandler(loki_handler)
            
            # Armazena referência global para graceful shutdown
            _loki_handler_instance = loki_handler
            
            # Log inicial sobre configuração do Loki
            logger = logging.getLogger(__name__)
            endpoint = f"{loki_url}/loki/api/v1/push"
            
            logger.info("=" * 80)
            logger.info("📡 CONFIGURAÇÃO DO GRAFANA/LOKI")
            logger.info("   ✅ Handler customizado criado com sucesso")
            logger.info(f"   🔗 Endpoint: {endpoint}")
            logger.info(f"   📋 JOB: {loki_job}")
            logger.info(f"   📤 Método: POST")
            logger.info(f"   🏷️  Tags: job={loki_job}, application=produto-api")
            logger.info("   ✅ Handler configurado e pronto para enviar logs")
            logger.info("   📦 Envio em batch (10 logs ou 5 segundos)")
            logger.info("=" * 80)
            
            # Configura uma função auxiliar para garantir que novos loggers também usem o Loki
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
                loki_handler_for_logger = LokiHandler(
                    loki_url=loki_url,
                    loki_job=loki_job,
                    batch_size=10,
                    timeout=5
                )
                loki_handler_for_logger.setLevel(level)
                loki_handler_for_logger.setFormatter(loki_formatter)
                logger_instance.addHandler(loki_handler_for_logger)
                logger_instance.propagate = False
            
            # Cria uma função que será chamada quando o uvicorn iniciar
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
                        isinstance(h, LokiHandler) 
                        for h in logger_instance.handlers
                    )
                    if not has_loki:
                        configure_logger_for_loki(logger_name)
            
            # Armazena a função para ser chamada depois
            root_logger._ensure_uvicorn_loggers_configured = ensure_uvicorn_loggers_configured
            
            loki_connected = True
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Erro ao configurar Loki handler: {str(e)} | Tipo: {type(e).__name__}")
            loki_connected = False
            _loki_handler_instance = None
    else:
        logger = logging.getLogger(__name__)
        if not loki_enabled:
            logger.info("ℹ️ Loki desabilitado")
        else:
            logger.warning("⚠️ Loki não configurado (URL ou JOB não fornecidos)")
    
    # Sempre retorna uma tupla
    return loki_connected, _loki_handler_instance


def shutdown_loki_handler(timeout: float = 10.0):
    """
    Encerra o handler do Loki de forma graciosa
    
    Args:
        timeout: Tempo máximo para aguardar processamento
    """
    global _loki_handler_instance
    if _loki_handler_instance:
        _loki_handler_instance.shutdown(timeout=timeout)
        _loki_handler_instance = None
