import logging
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Importa métricas do Prometheus
try:
    from internal.infra.metrics.prometheus import (
        http_request_total,
        http_request_duration,
        http_errors_total,
    )
    from internal.infra.metrics.service_map import record_service_call
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    logger.warning("⚠️ Métricas do Prometheus não disponíveis")


class LoggerMiddleware(BaseHTTPMiddleware):
    """Middleware para registrar todas as requisições HTTP e coletar métricas"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Adiciona o request_id ao estado da requisição
        request.state.request_id = request_id
        
        # Normaliza o endpoint (remove IDs para evitar cardinalidade alta)
        endpoint = self._normalize_endpoint(request.url.path)
        method = request.method
        
        # Log da requisição
        logger.info(
            f"[{request_id}] {method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            logger.error(f"[{request_id}] Erro na requisição: {str(e)}")
            raise
        finally:
            # Calcula tempo de processamento
            process_time = time.time() - start_time
            
            # Coleta métricas do Prometheus
            if METRICS_AVAILABLE:
                # Incrementa contador de requisições
                http_request_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=str(status_code)
                ).inc()
                
                # Registra duração da requisição
                http_request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(process_time)
                
                # Registra erros (status >= 400)
                if status_code >= 400:
                    http_errors_total.labels(
                        method=method,
                        endpoint=endpoint,
                        status_code=str(status_code)
                    ).inc()
                
                # Registra no service map (requisição externa para a API)
                # Assumindo que a requisição vem de um cliente externo
                try:
                    client_name = request.headers.get("User-Agent", "unknown-client")
                    # Simplifica o nome do cliente
                    if "grafana" in client_name.lower():
                        client_name = "grafana"
                    elif "prometheus" in client_name.lower():
                        client_name = "prometheus"
                    else:
                        client_name = "external-client"
                    
                    record_service_call(
                        source_service=client_name,
                        target_service="produto-api",
                        method=method,
                        duration=process_time,
                        status_code=status_code,
                        error_type=None if status_code < 400 else f"http_{status_code}"
                    )
                except Exception as e:
                    # Não falha se service map não estiver disponível
                    pass
        
        # Log da resposta
        logger.info(
            f"[{request_id}] Status: {status_code} - "
            f"Duration: {process_time:.3f}s"
        )
        
        # Adiciona headers personalizados
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _normalize_endpoint(self, path: str) -> str:
        """
        Normaliza o endpoint removendo IDs para evitar cardinalidade alta nas métricas
        
        Exemplos:
        /produtos/123 -> /produtos/{id}
        /produtos/123/categoria -> /produtos/{id}/categoria
        """
        import re
        # Substitui números por {id}
        normalized = re.sub(r'/\d+', '/{id}', path)
        # Remove múltiplos {id} consecutivos
        normalized = re.sub(r'/\{id\}(/\{id\})*', '/{id}', normalized)
        return normalized


def configure_cors(app, cors_config):
    """Configura CORS na aplicação"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.allow_origins,
        allow_credentials=cors_config.allow_credentials,
        allow_methods=cors_config.allow_methods,
        allow_headers=cors_config.allow_headers,
    )
    logger.info("CORS configured successfully")


def configure_middlewares(app):
    """Configura todos os middlewares da aplicação"""
    app.add_middleware(LoggerMiddleware)
    logger.info("Middlewares configured successfully")
