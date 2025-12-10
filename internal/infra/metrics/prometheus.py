"""
Módulo de métricas do Prometheus para monitoramento da aplicação
"""
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)
from typing import Dict, Any

# Métricas HTTP
http_request_total = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status_code']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

http_errors_total = Counter(
    'http_errors_total',
    'Total de erros HTTP',
    ['method', 'endpoint', 'status_code']
)

# Métricas do Loki
loki_logs_sent_total = Counter(
    'loki_logs_sent_total',
    'Total de logs enviados para o Loki',
    ['level', 'logger']
)

loki_logs_failed_total = Counter(
    'loki_logs_failed_total',
    'Total de falhas ao enviar logs para o Loki'
)

# Métricas de Banco de Dados
database_connections_active = Gauge(
    'database_connections_active',
    'Número de conexões ativas com o banco de dados'
)

database_queries_total = Counter(
    'database_queries_total',
    'Total de queries executadas no banco de dados',
    ['operation', 'table']
)

# Métricas da Aplicação
application_info = Gauge(
    'application_info',
    'Informações da aplicação',
    ['version', 'environment']
)

application_uptime_seconds = Gauge(
    'application_uptime_seconds',
    'Tempo de atividade da aplicação em segundos'
)


def setup_metrics(version: str = "1.0.0", environment: str = "development"):
    """
    Configura as métricas iniciais da aplicação
    
    Args:
        version: Versão da aplicação
        environment: Ambiente de execução
    """
    import time
    start_time = time.time()
    
    # Define informações da aplicação
    application_info.labels(version=version, environment=environment).set(1)
    
    # Atualiza uptime periodicamente (será atualizado por um thread)
    def update_uptime():
        while True:
            uptime = time.time() - start_time
            application_uptime_seconds.set(uptime)
            time.sleep(1)
    
    import threading
    uptime_thread = threading.Thread(target=update_uptime, daemon=True)
    uptime_thread.start()


def get_metrics() -> bytes:
    """
    Retorna as métricas no formato do Prometheus
    
    Returns:
        bytes: Métricas formatadas para o Prometheus
    """
    return generate_latest(REGISTRY)


def get_metrics_content_type() -> str:
    """
    Retorna o content-type para as métricas do Prometheus
    
    Returns:
        str: Content-type apropriado
    """
    return CONTENT_TYPE_LATEST

