import os
from typing import List
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    driver: str = "postgresql"
    user: str = os.getenv("DATABASE_USER", "postgres")
    password: str = os.getenv("DATABASE_PASSWORD", "postgres")
    host: str = os.getenv("DATABASE_HOST", "localhost")
    port: int = int(os.getenv("DATABASE_PORT", "5432"))
    name: str = os.getenv("DATABASE_NAME", "produto_db")
    pool_size: int = 20
    max_overflow: int = 40

    @property
    def database_url(self) -> str:
        return f"{self.driver}+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class CORSConfig(BaseSettings):
    allow_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080"
    ]
    allow_credentials: bool = True
    allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers: List[str] = ["*"]


class ServerConfig(BaseSettings):
    host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    port: int = int(os.getenv("SERVER_PORT", "8000"))
    reload: bool = os.getenv("ENVIRONMENT") == "development"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


class LokiConfig(BaseSettings):
    url: str = os.getenv("LOKI_URL", "http://172.30.0.45:3100")
    job: str = os.getenv("LOKI_JOB", "MONITORAMENTO_PRODUTO")
    enabled: bool = os.getenv("LOKI_ENABLED", "True").lower() == "true"


class Settings(BaseSettings):
    database: DatabaseConfig = DatabaseConfig()
    server: ServerConfig = ServerConfig()
    cors: CORSConfig = CORSConfig()
    loki: LokiConfig = LokiConfig()
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    class Config:
        extra = "allow"
        env_file = ".env"


settings = Settings()
