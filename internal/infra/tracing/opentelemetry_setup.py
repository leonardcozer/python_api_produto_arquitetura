"""
Configuração do OpenTelemetry para distributed tracing com Tempo
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Flag para verificar se o tracing está disponível
TRACING_AVAILABLE = False

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    TRACING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ OpenTelemetry não disponível: {str(e)}")
    TRACING_AVAILABLE = False


def setup_tracing(
    tempo_endpoint: Optional[str] = None,
    service_name: str = "produto-api",
    enabled: bool = True
) -> bool:
    """
    Configura o OpenTelemetry para enviar traces para o Tempo
    
    Args:
        tempo_endpoint: URL do endpoint OTLP do Tempo (ex: http://172.30.0.45:4317)
        service_name: Nome do serviço para identificação nos traces
        enabled: Se True, habilita o tracing
    
    Returns:
        bool: True se o tracing foi configurado com sucesso, False caso contrário
    """
    if not TRACING_AVAILABLE:
        logger.warning("⚠️ OpenTelemetry não está instalado. Instale com: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc")
        return False
    
    if not enabled:
        logger.info("ℹ️ Tracing desabilitado")
        return False
    
    if not tempo_endpoint:
        logger.warning("⚠️ Tempo endpoint não fornecido. Tracing não será configurado.")
        return False
    
    try:
        # Remove http:// ou https:// se presente (OTLPSpanExporter espera apenas host:port)
        # Também corrige formato incorreto como "http:172.30.0.45:4317"
        endpoint = tempo_endpoint.replace("http://", "").replace("https://", "").replace("http:", "").replace("https:", "")
        
        # Configura o Resource com informações do serviço
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "development")
        })
        
        # Configura o TracerProvider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        
        # Configura o exporter OTLP para Tempo
        otlp_exporter = OTLPSpanExporter(
            endpoint=endpoint,
            insecure=True  # Use False em produção com TLS
        )
        
        # Configura o BatchSpanProcessor para envio em batch
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        logger.info("=" * 80)
        logger.info("🔍 OPEN TELEMETRY / TEMPO CONFIGURADO")
        logger.info(f"   🔗 Endpoint: {endpoint}")
        logger.info(f"   📋 Service: {service_name}")
        logger.info(f"   ✅ Tracing habilitado e pronto para enviar traces")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar OpenTelemetry: {str(e)}")
        return False


def get_tracer(name: str):
    """
    Obtém um tracer para criar spans
    
    Args:
        name: Nome do tracer (geralmente __name__ do módulo)
    
    Returns:
        Tracer: Instância do tracer ou None se não disponível
    """
    if not TRACING_AVAILABLE:
        return None
    
    try:
        return trace.get_tracer(name)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao obter tracer: {str(e)}")
        return None


def instrument_fastapi(app):
    """
    Instrumenta o FastAPI para tracing automático
    
    Args:
        app: Instância do FastAPI
    """
    if not TRACING_AVAILABLE:
        return
    
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
        logger.info("✅ FastAPI instrumentado para tracing")
    except ImportError:
        logger.warning("⚠️ FastAPIInstrumentor não disponível")
    except Exception as e:
        logger.error(f"❌ Erro ao instrumentar FastAPI: {str(e)}")


def instrument_sqlalchemy():
    """
    Instrumenta o SQLAlchemy para tracing de queries
    """
    if not TRACING_AVAILABLE:
        return
    
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLAlchemyInstrumentor().instrument()
        logger.info("✅ SQLAlchemy instrumentado para tracing")
    except ImportError:
        logger.warning("⚠️ SQLAlchemyInstrumentor não disponível")
    except Exception as e:
        logger.error(f"❌ Erro ao instrumentar SQLAlchemy: {str(e)}")

