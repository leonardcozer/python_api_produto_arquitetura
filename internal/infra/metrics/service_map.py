"""
Módulo para métricas de Service Map (Node Graph)
Permite visualizar dependências e relacionamentos entre serviços
"""
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Optional

# Métricas de Service Map
service_map_requests_total = Counter(
    'service_map_requests_total',
    'Total de requisições entre serviços',
    ['source_service', 'target_service', 'method', 'status_code']
)

service_map_request_duration_seconds = Histogram(
    'service_map_request_duration_seconds',
    'Duração de requisições entre serviços',
    ['source_service', 'target_service', 'method'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

service_map_errors_total = Counter(
    'service_map_errors_total',
    'Total de erros entre serviços',
    ['source_service', 'target_service', 'error_type']
)

# Métricas de dependências
service_dependency_active = Gauge(
    'service_dependency_active',
    'Indica se uma dependência está ativa',
    ['source_service', 'target_service', 'dependency_type']
)

# Métricas de saúde do serviço
service_health_status = Gauge(
    'service_health_status',
    'Status de saúde do serviço (1=healthy, 0=unhealthy)',
    ['service_name', 'check_type']
)

# Métricas de throughput
service_throughput = Gauge(
    'service_throughput_rps',
    'Requisições por segundo do serviço',
    ['service_name']
)


def record_service_call(
    source_service: str,
    target_service: str,
    method: str,
    duration: float,
    status_code: int,
    error_type: Optional[str] = None
):
    """
    Registra uma chamada entre serviços para o service map
    
    Args:
        source_service: Nome do serviço que faz a chamada
        target_service: Nome do serviço que recebe a chamada
        method: Método HTTP ou tipo de operação
        duration: Duração da chamada em segundos
        status_code: Código de status HTTP
        error_type: Tipo de erro (se houver)
    """
    # Incrementa contador de requisições
    service_map_requests_total.labels(
        source_service=source_service,
        target_service=target_service,
        method=method,
        status_code=str(status_code)
    ).inc()
    
    # Registra duração
    service_map_request_duration_seconds.labels(
        source_service=source_service,
        target_service=target_service,
        method=method
    ).observe(duration)
    
    # Registra erros
    if status_code >= 400 or error_type:
        service_map_errors_total.labels(
            source_service=source_service,
            target_service=target_service,
            error_type=error_type or f"http_{status_code}"
        ).inc()


def set_service_dependency(
    source_service: str,
    target_service: str,
    dependency_type: str,
    active: bool = True
):
    """
    Define o status de uma dependência entre serviços
    
    Args:
        source_service: Serviço que depende
        target_service: Serviço dependido
        dependency_type: Tipo de dependência (database, api, cache, etc)
        active: Se a dependência está ativa
    """
    service_dependency_active.labels(
        source_service=source_service,
        target_service=target_service,
        dependency_type=dependency_type
    ).set(1 if active else 0)


def set_service_health(service_name: str, check_type: str, healthy: bool):
    """
    Define o status de saúde de um serviço
    
    Args:
        service_name: Nome do serviço
        check_type: Tipo de verificação (liveness, readiness, etc)
        healthy: Se o serviço está saudável
    """
    service_health_status.labels(
        service_name=service_name,
        check_type=check_type
    ).set(1 if healthy else 0)


def update_service_throughput(service_name: str, requests_per_second: float):
    """
    Atualiza o throughput (requisições por segundo) de um serviço
    
    Args:
        service_name: Nome do serviço
        requests_per_second: Requisições por segundo
    """
    service_throughput.labels(service_name=service_name).set(requests_per_second)

