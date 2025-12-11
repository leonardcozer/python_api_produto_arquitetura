import logging
from typing import Generator
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from internal.modules.produto.dto import ProdutoCreateRequest, ProdutoUpdateRequest, ProdutoResponse, ProdutoListResponse
from internal.modules.produto.service import ProdutoService
from internal.modules.produto.repository import ProdutoRepository
from internal.infra.database.banco_dados import db
from pkg.apperrors.exceptions import NotFoundError, BadRequestError
from pkg.utils.input_validators import (
    sanitize_search_term,
    sanitize_category,
    validate_page_params,
    validate_id
)

logger = logging.getLogger("api")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter uma sessão do banco de dados.
    Usa context manager para garantir fechamento adequado da sessão.
    """
    with db.get_session() as session:
        yield session


def get_produto_service(db: Session = Depends(get_db)) -> ProdutoService:
    """Dependency para obter a service de produto"""
    repository = ProdutoRepository(db)
    return ProdutoService(repository)


router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.post(
    "",
    response_model=ProdutoResponse,
    status_code=201,
    summary="Criar novo produto",
    responses={
        201: {"description": "Produto criado com sucesso"},
        400: {"description": "Dados inválidos"},
    }
)
async def criar_produto(
    produto_request: ProdutoCreateRequest,
    service: ProdutoService = Depends(get_produto_service)
):
    """
    Cria um novo produto
    
    - **nome**: Nome do produto (obrigatório)
    - **descricao**: Descrição do produto
    - **preco**: Preço do produto (obrigatório, deve ser > 0)
    - **quantidade**: Quantidade em estoque
    - **categoria**: Categoria do produto (obrigatório)
    """
    try:
        return service.criar_produto(produto_request)
    except BadRequestError as e:
        logger.warning(f"Erro de validação ao criar produto: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Obter um produto",
    responses={
        200: {"description": "Produto encontrado"},
        404: {"description": "Produto não encontrado"},
    }
)
async def obter_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_produto_service)
):
    """Obtém um produto específico pelo ID"""
    # Valida o ID antes de processar
    validate_id(produto_id, "ID do produto")
    return service.obter_produto(produto_id)


@router.get(
    "",
    response_model=ProdutoListResponse,
    summary="Listar todos os produtos",
    responses={
        200: {"description": "Lista de produtos"},
        400: {"description": "Parâmetros inválidos"},
    }
)
async def listar_produtos(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: ProdutoService = Depends(get_produto_service)
):
    """
    Lista todos os produtos com paginação
    
    - **page**: Número da página (padrão: 1)
    - **page_size**: Quantidade de itens por página (padrão: 10, máximo: 100)
    """
    # Valida parâmetros de paginação
    page, page_size = validate_page_params(page, page_size)
    return service.listar_produtos(page=page, page_size=page_size)


@router.get(
    "/categoria/{categoria}",
    response_model=ProdutoListResponse,
    summary="Listar produtos por categoria",
    responses={
        200: {"description": "Lista de produtos da categoria"},
        400: {"description": "Parâmetros inválidos"},
    }
)
async def listar_por_categoria(
    categoria: str,
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: ProdutoService = Depends(get_produto_service)
):
    """
    Lista produtos de uma categoria específica
    
    - **categoria**: Categoria dos produtos
    - **page**: Número da página (padrão: 1)
    - **page_size**: Quantidade de itens por página (padrão: 10, máximo: 100)
    """
    # Sanitiza e valida categoria
    categoria = sanitize_category(categoria)
    # Valida parâmetros de paginação
    page, page_size = validate_page_params(page, page_size)
    return service.listar_por_categoria(categoria, page=page, page_size=page_size)


@router.get(
    "/buscar/termo",
    response_model=ProdutoListResponse,
    summary="Buscar produtos",
    responses={
        200: {"description": "Resultados da busca"},
        400: {"description": "Termo de busca inválido"},
    }
)
async def buscar_produtos(
    termo: str = Query(..., min_length=2, description="Termo para buscar"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: ProdutoService = Depends(get_produto_service)
):
    """
    Busca produtos por nome ou descrição
    
    - **termo**: Termo a buscar (mínimo 2 caracteres)
    - **page**: Número da página (padrão: 1)
    - **page_size**: Quantidade de itens por página (padrão: 10, máximo: 100)
    """
    # Sanitiza o termo de busca (previne SQL injection)
    termo = sanitize_search_term(termo)
    # Valida parâmetros de paginação
    page, page_size = validate_page_params(page, page_size)
    return service.buscar_produtos(termo, page=page, page_size=page_size)


@router.put(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Atualizar um produto",
    responses={
        200: {"description": "Produto atualizado com sucesso"},
        400: {"description": "Dados inválidos"},
        404: {"description": "Produto não encontrado"},
    }
)
async def atualizar_produto(
    produto_id: int,
    produto_request: ProdutoUpdateRequest,
    service: ProdutoService = Depends(get_produto_service)
):
    """
    Atualiza um produto existente
    
    - **produto_id**: ID do produto a atualizar
    - Todos os campos são opcionais
    """
    # Valida o ID antes de processar
    validate_id(produto_id, "ID do produto")
    return service.atualizar_produto(produto_id, produto_request)


@router.delete(
    "/{produto_id}",
    status_code=204,
    summary="Deletar um produto",
    responses={
        204: {"description": "Produto deletado com sucesso"},
        404: {"description": "Produto não encontrado"},
    }
)
async def deletar_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_produto_service)
):
    """Deleta um produto específico"""
    # Valida o ID antes de processar
    validate_id(produto_id, "ID do produto")
    service.deletar_produto(produto_id)
    return None
