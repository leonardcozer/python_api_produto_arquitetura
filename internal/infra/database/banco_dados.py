import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from config.config import settings

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def init(self):
        """Inicializa a conexão com o banco de dados"""
        try:
            self.engine = create_engine(
                settings.database.database_url,
                poolclass=QueuePool,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                echo=settings.debug,
                pool_pre_ping=True,  # Verifica se a conexão está viva antes de usar
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def get_session(self) -> Session:
        """Retorna uma nova sessão do banco de dados"""
        if self.SessionLocal is None:
            self.init()
        return self.SessionLocal()

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

    def create_tables(self):
        """Cria todas as tabelas no banco de dados"""
        try:
            # Importa todos os modelos para garantir que estejam registrados
            from internal.modules.produto.entity import Base as ProdutoBase
            
            # Cria as tabelas
            ProdutoBase.metadata.create_all(bind=self.engine)
            logger.info("All tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise


# Instância global do banco de dados
db = Database()
