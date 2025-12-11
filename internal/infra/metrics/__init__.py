"""
Módulo de métricas do Prometheus
"""
from internal.infra.metrics.prometheus import (
    get_metrics,
    setup_metrics,
    http_request_duration,
    http_request_total,
    http_errors_total,
    loki_logs_sent_total,
    loki_logs_failed_total,
    database_connections_active,
    database_queries_total,
)
from internal.infra.metrics.service_map import (
    record_service_call,
    set_service_dependency,
    set_service_health,
    update_service_throughput,
)

__all__ = [
    "get_metrics",
    "setup_metrics",
    "http_request_duration",
    "http_request_total",
    "http_errors_total",
    "loki_logs_sent_total",
    "loki_logs_failed_total",
    "database_connections_active",
    "database_queries_total",
    "record_service_call",
    "set_service_dependency",
    "set_service_health",
    "update_service_throughput",
]

