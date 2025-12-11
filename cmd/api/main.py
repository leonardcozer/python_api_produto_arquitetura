#!/usr/bin/env python3
"""
Arquivo principal da aplicação (Entry Point)
Inicializa o FastAPI com todas as configurações, middlewares e rotas
"""

import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

# Adiciona o diretório raiz ao path para imports relativos
sys.path.insert(0, str(__file__).rsplit('/', 3)[0])

from config.config import settings
from internal.infra.database.banco_dados import db
from internal.infra.http.server import create_server
from internal.infra.http.middlewares import configure_middlewares, configure_cors
from internal.infra.logger.zap import LOGGER_MAIN, configure_logging, shutdown_loki_handler
from internal.infra.tracing.opentelemetry_setup import setup_tracing, instrument_fastapi, instrument_sqlalchemy
from internal.modules.produto.routes import router as produto_router
from pkg.apperrors.exception_handlers import register_exception_handlers

# Importa métricas do Prometheus (com tratamento de erro)
METRICS_AVAILABLE = False
try:
    from internal.infra.metrics.prometheus import setup_metrics, get_metrics, get_metrics_content_type
    from internal.infra.metrics.service_map import (
        set_service_dependency,
        set_service_health,
        record_service_call
    )
    METRICS_AVAILABLE = True
except ImportError as e:
    # Log será feito depois que o logger estiver configurado
    _metrics_import_error = str(e)
    # Cria funções stub
    def setup_metrics(*args, **kwargs):
        pass
    def get_metrics():
        return b"# Metrics not available - prometheus_client not installed\n"
    def get_metrics_content_type():
        return "text/plain"
    def set_service_dependency(*args, **kwargs):
        pass
    def set_service_health(*args, **kwargs):
        pass
    def record_service_call(*args, **kwargs):
        pass
except Exception as e:
    _metrics_import_error = str(e)
    def setup_metrics(*args, **kwargs):
        pass
    def get_metrics():
        return b"# Metrics not available\n"
    def get_metrics_content_type():
        return "text/plain"
    def set_service_dependency(*args, **kwargs):
        pass
    def set_service_health(*args, **kwargs):
        pass
    def record_service_call(*args, **kwargs):
        pass

# Configura logging com suporte ao Loki
loki_connected, loki_handler = configure_logging(
    log_level=settings.server.log_level,
    loki_url=settings.loki.url if settings.loki.enabled else None,
    loki_job=settings.loki.job if settings.loki.enabled else None,
    loki_enabled=settings.loki.enabled
)
logger = logging.getLogger(LOGGER_MAIN)

# Log sobre status das métricas
if not METRICS_AVAILABLE:
    try:
        logger.warning(f"⚠️ Métricas do Prometheus não disponíveis: {_metrics_import_error}")
    except:
        logger.warning("⚠️ Métricas do Prometheus não disponíveis")

# Mensagem informativa sobre Grafana/Loki
if loki_connected:
    logger.info("=" * 80)
    logger.info("📊 GRAFANA + LOKI CONECTADO E ATIVO")
    logger.info(f"   🔗 URL: {settings.loki.url}")
    logger.info(f"   📋 JOB: {settings.loki.job}")
    logger.info(f"   📤 Endpoint POST: {settings.loki.url}/loki/api/v1/push")
    logger.info("   ✅ Todos os logs estão sendo enviados para o Grafana/Loki")
    logger.info("   📝 Logs de envio serão exibidos a cada 10 logs ou em nível DEBUG")
    logger.info("=" * 80)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para gerenciar o ciclo de vida da aplicação
    Inicializa recursos ao iniciar e limpa ao desligar
    """
    # Inicialização (startup)
    logger.info("🚀 Iniciando aplicação...")
    
    # Garante que os loggers do uvicorn também estão configurados para o Loki
    if loki_connected:
        root_logger = logging.getLogger()
        if hasattr(root_logger, '_ensure_uvicorn_loggers_configured'):
            root_logger._ensure_uvicorn_loggers_configured()
            logger.info("✅ Loggers do Uvicorn configurados para Grafana/Loki")
    
    try:
        db.init()
        db.create_tables()
        logger.info("✅ Banco de dados inicializado com sucesso")
        
        # Registra dependência do banco de dados no service map
        if METRICS_AVAILABLE:
            try:
                set_service_dependency(
                    source_service="produto-api",
                    target_service="postgresql",
                    dependency_type="database",
                    active=True
                )
                set_service_health("produto-api", "readiness", True)
                set_service_health("produto-api", "liveness", True)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao registrar métricas de service map: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco de dados: {str(e)}")
        if METRICS_AVAILABLE:
            try:
                set_service_health("produto-api", "readiness", False)
                set_service_dependency(
                    source_service="produto-api",
                    target_service="postgresql",
                    dependency_type="database",
                    active=False
                )
            except:
                pass
        raise

    yield

    # Limpeza (shutdown)
    logger.info("🛑 Encerrando aplicação...")
    
    # Graceful shutdown do Loki handler
    if loki_connected:
        try:
            shutdown_loki_handler(timeout=10.0)
            logger.info("✅ Loki handler encerrado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar Loki handler: {str(e)}")
    
    # Fecha conexão com banco de dados
    try:
        db.close()
        logger.info("✅ Conexão com banco de dados fechada")
    except Exception as e:
        logger.error(f"❌ Erro ao fechar banco de dados: {str(e)}")
    
    logger.info("✅ Aplicação encerrada com sucesso")


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI"""
    
    # Cria a instância do FastAPI
    app = create_server()
    app.router.lifespan_context = lifespan
    
    # Configura OpenTelemetry/Tempo (deve ser antes de instrumentar)
    tempo_connected = False
    if settings.tempo.enabled:
        try:
            tempo_connected = setup_tracing(
                tempo_endpoint=settings.tempo.endpoint,
                service_name="produto-api",
                enabled=settings.tempo.enabled
            )
            if tempo_connected:
                # Instrumenta SQLAlchemy para tracing de queries
                instrument_sqlalchemy()
        except Exception as e:
            logger.error(f"❌ Erro ao configurar Tempo: {str(e)}")
    
    # Instrumenta FastAPI para tracing automático (deve ser antes de registrar rotas)
    if tempo_connected:
        try:
            instrument_fastapi(app)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao instrumentar FastAPI: {str(e)}")
    
    # Registra exception handlers globais (deve ser antes das rotas)
    register_exception_handlers(app)
    
    # Configura CORS
    configure_cors(app, settings.cors)
    
    # Configura middlewares
    configure_middlewares(app)
    
    # Configura métricas do Prometheus
    if METRICS_AVAILABLE:
        try:
            setup_metrics(version="1.0.0", environment=settings.environment)
            logger.info("✅ Métricas do Prometheus configuradas")
        except Exception as e:
            logger.error(f"❌ Erro ao configurar métricas: {str(e)}")
    
    # Rota de métricas do Prometheus (sempre registrada)
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Endpoint para expor métricas do Prometheus"""
        from fastapi.responses import Response
        if not METRICS_AVAILABLE:
            return Response(
                content=b"# Metrics not available - prometheus_client not installed\n# Install with: pip install prometheus-client\n",
                media_type="text/plain",
                status_code=200  # Retorna 200 mesmo sem métricas
            )
        try:
            metrics_data = get_metrics()
            return Response(
                content=metrics_data,
                media_type=get_metrics_content_type()
            )
        except Exception as e:
            logger.error(f"❌ Erro ao gerar métricas: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                content=f"# Error generating metrics: {str(e)}\n".encode(),
                media_type="text/plain",
                status_code=500
            )
    
    logger.info("✅ Rota /metrics registrada")
    
    # Registra as rotas
    app.include_router(produto_router)
    
    # Log de debug: lista todas as rotas registradas
    routes_list = [route.path for route in app.routes if hasattr(route, 'path')]
    logger.info(f"✅ Rotas registradas: {routes_list}")
    
    # Rota de health check (liveness probe)
    @app.get(
        "/health",
        tags=["Health"],
        summary="Health Check",
        description="Verifica se a aplicação está rodando (liveness probe)"
    )
    async def health_check():
        """Endpoint para verificar se a aplicação está viva"""
        return {
            "status": "healthy",
            "service": "produto-api",
            "environment": settings.environment,
            "version": "1.0.0"
        }
    
    # Rota de readiness probe
    @app.get(
        "/ready",
        tags=["Health"],
        summary="Readiness Check",
        description="Verifica se a aplicação está pronta para receber requisições"
    )
    async def readiness_check():
        """
        Endpoint para verificar se a aplicação está pronta.
        Verifica conexão com banco de dados e outras dependências críticas.
        """
        checks = {
            "database": False,
            "loki": False,
            "status": "unhealthy"
        }
        
        # Verifica conexão com banco de dados
        try:
            checks["database"] = db.check_connection()
            # Atualiza métricas de service map
            if METRICS_AVAILABLE:
                try:
                    set_service_health("produto-api", "readiness", checks["database"])
                    set_service_dependency(
                        source_service="produto-api",
                        target_service="postgresql",
                        dependency_type="database",
                        active=checks["database"]
                    )
                except:
                    pass
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            checks["database"] = False
            if METRICS_AVAILABLE:
                try:
                    set_service_health("produto-api", "readiness", False)
                except:
                    pass
        
        # Verifica status do Loki (se habilitado)
        if loki_connected:
            checks["loki"] = True  # Simplificado - poderia verificar conexão real
        else:
            checks["loki"] = True  # Não é crítico se desabilitado
        
        # Determina status geral
        if checks["database"]:
            checks["status"] = "ready"
            status_code = 200
        else:
            checks["status"] = "not_ready"
            status_code = 503
        
        # Adiciona informações do pool
        try:
            pool_status = db.get_pool_status()
            checks["database_pool"] = pool_status
        except Exception:
            pass
        
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status_code,
            content={
                "status": checks["status"],
                "checks": checks,
                "service": "produto-api",
                "environment": settings.environment,
                "version": "1.0.0"
            }
        )
    
    # Rota raiz
    @app.get(
        "/",
        tags=["Root"],
        summary="Root Endpoint",
        description="Endpoint raiz da aplicação"
    )
    async def root():
        """Endpoint raiz da API"""
        return {
            "message": "API Produto",
            "version": "1.0.0",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    
    logger.info("✅ Aplicação configurada com sucesso")
    logger.info(f"📊 Documentação disponível em: http://{settings.server.host}:{settings.server.port}/docs")
    logger.info(f"📈 Métricas Prometheus disponíveis em: http://{settings.server.host}:{settings.server.port}/metrics")
    
    return app


# Cria a instância global da aplicação
app = create_app()


def main():
    """Função principal que inicia o servidor"""
    logger.info("=" * 80)
    logger.info(f"🌐 Iniciando servidor em http://{settings.server.host}:{settings.server.port}")
    logger.info(f"📚 Documentação em http://{settings.server.host}:{settings.server.port}/docs")
    logger.info(f"📈 Métricas Prometheus em http://{settings.server.host}:{settings.server.port}/metrics")
    logger.info(f"🔧 Ambiente: {settings.environment}")
    logger.info(f"📝 Nível de log: {settings.server.log_level}")
    if loki_connected:
        logger.info(f"📊 Grafana/Loki: CONECTADO - JOB: {settings.loki.job}")
        # Garante que os loggers do uvicorn também estão configurados
        root_logger = logging.getLogger()
        if hasattr(root_logger, '_ensure_uvicorn_loggers_configured'):
            root_logger._ensure_uvicorn_loggers_configured()
    else:
        logger.info("📊 Grafana/Loki: DESCONECTADO")
    
    # Verifica status do Tempo
    try:
        from internal.infra.tracing.opentelemetry_setup import TRACING_AVAILABLE
        if TRACING_AVAILABLE and settings.tempo.enabled:
            logger.info(f"🔍 Tempo/OpenTelemetry: CONECTADO - Endpoint: {settings.tempo.endpoint}")
        elif settings.tempo.enabled:
            logger.info("🔍 Tempo/OpenTelemetry: DESCONECTADO (biblioteca não instalada)")
        else:
            logger.info("🔍 Tempo/OpenTelemetry: DESABILITADO")
    except:
        logger.info("🔍 Tempo/OpenTelemetry: NÃO CONFIGURADO")
    
    logger.info("=" * 80)
    
    # Inicia o servidor Uvicorn
    # Usa log_config=None para usar o logger já configurado
    # Isso garante que todos os logs do uvicorn também vão para o Loki
    uvicorn.run(
        "cmd.api.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        log_level=settings.server.log_level.lower(),
        log_config=None,  # Usa o logger já configurado
    )


if __name__ == "__main__":
    main()
