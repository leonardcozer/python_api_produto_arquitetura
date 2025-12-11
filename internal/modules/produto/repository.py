import logging
from sqlalchemy.orm import Session
from sqlalchemy import func

from internal.modules.produto.entity import Produto
from pkg.apperrors.exceptions import NotFoundError

logger = logging.getLogger("repository")


class ProdutoRepository:
    """Repository para operações de banco de dados relacionadas a Produtos"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, produto_data: dict) -> Produto:
        """Cria um novo produto no banco de dados"""
        try:
            produto = Produto(**produto_data)
            self.db.add(produto)
            self.db.commit()
            self.db.refresh(produto)
            logger.info(f"Produto criado com sucesso: {produto.id}")
            return produto
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar produto: {str(e)}")
            raise

    def get_by_id(self, produto_id: int) -> Produto:
        """Obtém um produto pelo ID"""
        produto = self.db.query(Produto).filter(Produto.id == produto_id).first()
        if not produto:
            logger.warning(f"Produto não encontrado: {produto_id}")
            raise NotFoundError(f"Produto com ID {produto_id} não encontrado")
        return produto

    def get_all(self, skip: int = 0, limit: int = 10) -> tuple[list[Produto], int]:
        """Obtém todos os produtos com paginação"""
        total = self.db.query(func.count(Produto.id)).scalar()
        produtos = self.db.query(Produto).offset(skip).limit(limit).all()
        logger.info(f"Buscados {len(produtos)} produtos (total: {total})")
        return produtos, total

    def get_by_categoria(self, categoria: str, skip: int = 0, limit: int = 10) -> tuple[list[Produto], int]:
        """Obtém produtos por categoria"""
        total = self.db.query(func.count(Produto.id)).filter(
            Produto.categoria == categoria
        ).scalar()
        produtos = self.db.query(Produto).filter(
            Produto.categoria == categoria
        ).offset(skip).limit(limit).all()
        logger.info(f"Buscados {len(produtos)} produtos da categoria {categoria}")
        return produtos, total

    def search(self, termo: str, skip: int = 0, limit: int = 10) -> tuple[list[Produto], int]:
        """
        Busca produtos por nome ou descrição.
        O termo já deve estar sanitizado antes de chegar aqui.
        """
        # Usa bind parameter para prevenir SQL injection
        # O termo já foi sanitizado no handler/service
        search_pattern = f"%{termo}%"
        query = self.db.query(Produto).filter(
            (Produto.nome.ilike(search_pattern)) |
            (Produto.descricao.ilike(search_pattern))
        )
        total = query.count()
        produtos = query.offset(skip).limit(limit).all()
        logger.info(f"Encontrados {len(produtos)} produtos para '{termo}'")
        return produtos, total

    def update(self, produto_id: int, produto_data: dict) -> Produto:
        """Atualiza um produto existente"""
        try:
            produto = self.get_by_id(produto_id)
            
            # Atualiza apenas os campos fornecidos
            for key, value in produto_data.items():
                if value is not None:
                    setattr(produto, key, value)
            
            self.db.commit()
            self.db.refresh(produto)
            logger.info(f"Produto atualizado com sucesso: {produto_id}")
            return produto
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar produto {produto_id}: {str(e)}")
            raise

    def delete(self, produto_id: int) -> bool:
        """Deleta um produto"""
        try:
            produto = self.get_by_id(produto_id)
            self.db.delete(produto)
            self.db.commit()
            logger.info(f"Produto deletado com sucesso: {produto_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar produto {produto_id}: {str(e)}")
            raise
