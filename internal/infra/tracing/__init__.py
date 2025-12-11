"""
Módulo de distributed tracing com OpenTelemetry
"""
from internal.infra.tracing.opentelemetry_setup import (
    setup_tracing,
    get_tracer,
    instrument_fastapi,
    instrument_sqlalchemy,
    TRACING_AVAILABLE
)

__all__ = [
    "setup_tracing",
    "get_tracer",
    "instrument_fastapi",
    "instrument_sqlalchemy",
    "TRACING_AVAILABLE",
]

