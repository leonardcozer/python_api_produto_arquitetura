import logging
import time
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

from config.config import settings

# Importa métricas de service map
try:
    from internal.infra.metrics.service_map import record_service_call
    SERVICE_MAP_AVAILABLE = True
except ImportError:
    SERVICE_MAP_AVAILABLE = False

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
                pool_recycle=3600,  # Recicla conexões após 1 hora
                connect_args={
                    "connect_timeout": 10,  # Timeout de conexão de 10 segundos
                }
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

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager para obter uma sessão do banco de dados.
        Garante que a sessão seja fechada mesmo em caso de exceção.
        
        Usage:
            with db.get_session() as session:
                # usar session
        """
        if self.SessionLocal is None:
            self.init()
        
        session = self.SessionLocal()
        start_time = time.time()
        try:
            yield session
            session.commit()
            
            # Registra chamada bem-sucedida no service map
            if SERVICE_MAP_AVAILABLE:
                try:
                    duration = time.time() - start_time
                    record_service_call(
                        source_service="produto-api",
                        target_service="postgresql",
                        method="query",
                        duration=duration,
                        status_code=200
                    )
                except:
                    pass
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            
            # Registra erro no service map
            if SERVICE_MAP_AVAILABLE:
                try:
                    duration = time.time() - start_time
                    record_service_call(
                        source_service="produto-api",
                        target_service="postgresql",
                        method="query",
                        duration=duration,
                        status_code=500,
                        error_type="database_error"
                    )
                except:
                    pass
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error in database session: {str(e)}")
            
            # Registra erro no service map
            if SERVICE_MAP_AVAILABLE:
                try:
                    duration = time.time() - start_time
                    record_service_call(
                        source_service="produto-api",
                        target_service="postgresql",
                        method="query",
                        duration=duration,
                        status_code=500,
                        error_type="unexpected_error"
                    )
                except:
                    pass
            raise
        finally:
            session.close()

    def check_connection(self) -> bool:
        """
        Verifica se a conexão com o banco de dados está funcionando
        
        Returns:
            bool: True se a conexão está OK, False caso contrário
        """
        try:
            if self.engine is None:
                return False
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False

    def get_pool_status(self) -> dict:
        """
        Retorna o status do pool de conexões
        
        Returns:
            dict: Status do pool (size, checked_in, checked_out, overflow, invalid)
        """
        if self.engine is None:
            return {
                "pool_size": 0,
                "checked_in": 0,
                "checked_out": 0,
                "overflow": 0,
                "invalid": 0
            }
        
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }

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
