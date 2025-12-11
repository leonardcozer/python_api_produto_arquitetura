import logging
from sqlalchemy.orm import Session

from internal.modules.produto.repository import ProdutoRepository
from internal.modules.produto.dto import ProdutoCreateRequest, ProdutoUpdateRequest, ProdutoResponse, ProdutoListResponse
from pkg.apperrors.exceptions import NotFoundError, BadRequestError
from internal.infra.tracing.opentelemetry_setup import get_tracer

logger = logging.getLogger("service")
tracer = get_tracer(__name__)

# Importa trace para status (se disponível)
try:
    from opentelemetry import trace
    TRACE_AVAILABLE = True
except ImportError:
    TRACE_AVAILABLE = False
    trace = None


class ProdutoService:
    """Service contém a lógica de negócio relacionada a Produtos"""

    def __init__(self, repository: ProdutoRepository):
        self.repository = repository

    def criar_produto(self, produto_request: ProdutoCreateRequest) -> ProdutoResponse:
        """Cria um novo produto com validações de negócio"""
        # Cria span para tracing
        if tracer:
            span = tracer.start_span("service.criar_produto")
        else:
            span = None
        
        try:
            if span:
                span.set_attribute("produto.nome", produto_request.nome)
                span.set_attribute("produto.categoria", produto_request.categoria)
            
            # Validações de negócio
            if produto_request.preco < 0.01:
                if span and TRACE_AVAILABLE:
                    span.record_exception(BadRequestError("O preço deve ser maior que 0"))
                    span.set_status(trace.Status(trace.StatusCode.ERROR, "Preço inválido"))
                raise BadRequestError("O preço deve ser maior que 0")
            
            if produto_request.quantidade < 0:
                if span and TRACE_AVAILABLE:
                    span.record_exception(BadRequestError("A quantidade não pode ser negativa"))
                    span.set_status(trace.Status(trace.StatusCode.ERROR, "Quantidade inválida"))
                raise BadRequestError("A quantidade não pode ser negativa")

            produto_data = produto_request.dict()
            produto = self.repository.create(produto_data)
            logger.info(f"Produto criado via service: {produto.id}")
            
            if span and TRACE_AVAILABLE:
                span.set_attribute("produto.id", produto.id)
                span.set_status(trace.Status(trace.StatusCode.OK))
            
            return ProdutoResponse.from_orm(produto)
        except Exception as e:
            logger.error(f"Erro ao criar produto: {str(e)}")
            if span and TRACE_AVAILABLE:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise
        finally:
            if span:
                span.end()

    def obter_produto(self, produto_id: int) -> ProdutoResponse:
        """Obtém um produto pelo ID"""
        try:
            produto = self.repository.get_by_id(produto_id)
            return ProdutoResponse.from_orm(produto)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao obter produto: {str(e)}")
            raise

    def listar_produtos(self, page: int = 1, page_size: int = 10) -> ProdutoListResponse:
        """Lista todos os produtos com paginação"""
        try:
            if page < 1:
                raise BadRequestError("O número da página deve ser maior que 0")
            
            if page_size < 1 or page_size > 100:
                raise BadRequestError("O tamanho da página deve estar entre 1 e 100")

            skip = (page - 1) * page_size
            produtos, total = self.repository.get_all(skip=skip, limit=page_size)
            
            items = [ProdutoResponse.from_orm(p) for p in produtos]
            return ProdutoListResponse(
                total=total,
                page=page,
                page_size=page_size,
                items=items
            )
        except Exception as e:
            logger.error(f"Erro ao listar produtos: {str(e)}")
            raise

    def listar_por_categoria(self, categoria: str, page: int = 1, page_size: int = 10) -> ProdutoListResponse:
        """Lista produtos de uma categoria específica"""
        try:
            if page < 1:
                raise BadRequestError("O número da página deve ser maior que 0")
            
            if page_size < 1 or page_size > 100:
                raise BadRequestError("O tamanho da página deve estar entre 1 e 100")

            skip = (page - 1) * page_size
            produtos, total = self.repository.get_by_categoria(categoria, skip=skip, limit=page_size)
            
            items = [ProdutoResponse.from_orm(p) for p in produtos]
            return ProdutoListResponse(
                total=total,
                page=page,
                page_size=page_size,
                items=items
            )
        except Exception as e:
            logger.error(f"Erro ao listar por categoria: {str(e)}")
            raise

    def buscar_produtos(self, termo: str, page: int = 1, page_size: int = 10) -> ProdutoListResponse:
        """Busca produtos por termo"""
        try:
            if not termo or len(termo.strip()) < 2:
                raise BadRequestError("O termo de busca deve ter pelo menos 2 caracteres")
            
            if page < 1:
                raise BadRequestError("O número da página deve ser maior que 0")
            
            if page_size < 1 or page_size > 100:
                raise BadRequestError("O tamanho da página deve estar entre 1 e 100")

            skip = (page - 1) * page_size
            produtos, total = self.repository.search(termo, skip=skip, limit=page_size)
            
            items = [ProdutoResponse.from_orm(p) for p in produtos]
            return ProdutoListResponse(
                total=total,
                page=page,
                page_size=page_size,
                items=items
            )
        except Exception as e:
            logger.error(f"Erro ao buscar produtos: {str(e)}")
            raise

    def atualizar_produto(self, produto_id: int, produto_request: ProdutoUpdateRequest) -> ProdutoResponse:
        """Atualiza um produto existente"""
        try:
            # Validações de negócio
            if produto_request.preco is not None and produto_request.preco < 0.01:
                raise BadRequestError("O preço deve ser maior que 0")
            
            if produto_request.quantidade is not None and produto_request.quantidade < 0:
                raise BadRequestError("A quantidade não pode ser negativa")

            produto_data = produto_request.dict(exclude_unset=True)
            produto = self.repository.update(produto_id, produto_data)
            logger.info(f"Produto atualizado via service: {produto_id}")
            return ProdutoResponse.from_orm(produto)
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {str(e)}")
            raise

    def deletar_produto(self, produto_id: int) -> bool:
        """Deleta um produto"""
        try:
            sucesso = self.repository.delete(produto_id)
            logger.info(f"Produto deletado via service: {produto_id}")
            return sucesso
        except Exception as e:
            logger.error(f"Erro ao deletar produto: {str(e)}")
            raise
