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
]

