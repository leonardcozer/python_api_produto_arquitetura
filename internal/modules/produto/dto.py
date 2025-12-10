from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProdutoCreateRequest(BaseModel):
    """DTO para criar um novo produto"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do produto")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição do produto")
    preco: float = Field(..., gt=0, description="Preço do produto")
    quantidade: int = Field(default=0, ge=0, description="Quantidade em estoque")
    categoria: str = Field(..., min_length=1, max_length=100, description="Categoria do produto")

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Notebook Dell",
                "descricao": "Notebook de alta performance",
                "preco": 4999.99,
                "quantidade": 10,
                "categoria": "Eletrônicos"
            }
        }


class ProdutoUpdateRequest(BaseModel):
    """DTO para atualizar um produto"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, max_length=1000)
    preco: Optional[float] = Field(None, gt=0)
    quantidade: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = Field(None, min_length=1, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Notebook Dell XPS",
                "preco": 5499.99,
                "quantidade": 8
            }
        }


class ProdutoResponse(BaseModel):
    """DTO para resposta de um produto"""
    id: int
    nome: str
    descricao: Optional[str]
    preco: float
    quantidade: int
    categoria: str
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "nome": "Notebook Dell",
                "descricao": "Notebook de alta performance",
                "preco": 4999.99,
                "quantidade": 10,
                "categoria": "Eletrônicos",
                "criado_em": "2025-12-10T10:30:00",
                "atualizado_em": "2025-12-10T10:30:00"
            }
        }


class ProdutoListResponse(BaseModel):
    """DTO para resposta de lista de produtos"""
    total: int
    page: int
    page_size: int
    items: list[ProdutoResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 10,
                "items": []
            }
        }
