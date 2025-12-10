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
from internal.infra.http.server import create_server, configure_logging
from internal.infra.http.middlewares import configure_middlewares, configure_cors
from internal.infra.logger.zap import LOGGER_MAIN
from internal.modules.produto.routes import router as produto_router

# Configura logging
configure_logging(settings.server.log_level)
logger = logging.getLogger(LOGGER_MAIN)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para gerenciar o ciclo de vida da aplicação
    Inicializa recursos ao iniciar e limpa ao desligar
    """
    # Inicialização (startup)
    logger.info("🚀 Iniciando aplicação...")
    try:
        db.init()
        db.create_tables()
        logger.info("✅ Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco de dados: {str(e)}")
        raise

    yield

    # Limpeza (shutdown)
    logger.info("🛑 Encerrando aplicação...")
    db.close()
    logger.info("✅ Aplicação encerrada com sucesso")


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI"""
    
    # Cria a instância do FastAPI
    app = create_server()
    app.router.lifespan_context = lifespan
    
    # Configura CORS
    configure_cors(app, settings.cors)
    
    # Configura middlewares
    configure_middlewares(app)
    
    # Registra as rotas
    app.include_router(produto_router)
    
    # Rota de health check
    @app.get(
        "/health",
        tags=["Health"],
        summary="Health Check",
        description="Verifica se a aplicação está rodando"
    )
    async def health_check():
        """Endpoint para verificar se a aplicação está saudável"""
        return {
            "status": "healthy",
            "environment": settings.environment,
            "version": "1.0.0"
        }
    
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
    
    return app


# Cria a instância global da aplicação
app = create_app()


def main():
    """Função principal que inicia o servidor"""
    logger.info("=" * 80)
    logger.info(f"🌐 Iniciando servidor em http://{settings.server.host}:{settings.server.port}")
    logger.info(f"📚 Documentação em http://{settings.server.host}:{settings.server.port}/docs")
    logger.info(f"🔧 Ambiente: {settings.environment}")
    logger.info(f"📝 Nível de log: {settings.server.log_level}")
    logger.info("=" * 80)
    
    # Inicia o servidor Uvicorn
    uvicorn.run(
        "cmd.api.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        log_level=settings.server.log_level.lower(),
    )


if __name__ == "__main__":
    main()
