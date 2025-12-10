# 📦 Estrutura Completa do Projeto

## 🗂️ Árvore de Diretórios

```
my-api-project/
│
├── 📁 cmd/
│   ├── __init__.py
│   └── 📁 api/
│       ├── __init__.py
│       └── main.py ⭐ (Entry Point da Aplicação)
│
├── 📁 config/
│   ├── __init__.py
│   ├── config.py (Carrega variáveis de ambiente com Pydantic)
│   └── config.yaml (Arquivo de configuração YAML)
│
├── 📁 internal/
│   ├── __init__.py
│   │
│   ├── 📁 infra/ (Camada de Infraestrutura)
│   │   ├── __init__.py
│   │   │
│   │   ├── 📁 database/
│   │   │   ├── __init__.py
│   │   │   └── banco_dados.py (Gerenciamento de conexão PostgreSQL com SQLAlchemy)
│   │   │
│   │   ├── 📁 http/
│   │   │   ├── __init__.py
│   │   │   ├── server.py (Configuração do FastAPI)
│   │   │   └── middlewares.py (CORS, Logger, Autenticação)
│   │   │
│   │   └── 📁 logger/
│   │       ├── __init__.py
│   │       └── zap.py (Configuração de Logging)
│   │
│   └── 📁 modules/ (LÓGICA DE NEGÓCIO)
│       ├── __init__.py
│       │
│       └── 📁 produto/ (Módulo de Produtos)
│           ├── __init__.py
│           ├── dto.py (DTOs com Pydantic - Validação de entrada/saída)
│           ├── entity.py (Modelos SQLAlchemy - Mapeamento de tabelas)
│           ├── handler.py (Controllers HTTP - Endpoints FastAPI)
│           ├── repository.py (Data Access - Queries SQL)
│           ├── service.py (Lógica de Negócio - Regras)
│           └── routes.py (Definição de rotas)
│
├── 📁 pkg/ (Código Reutilizável)
│   ├── __init__.py
│   │
│   ├── 📁 apperrors/ (Exceções Customizadas)
│   │   ├── __init__.py
│   │   └── exceptions.py (NotFound, BadRequest, etc)
│   │
│   └── 📁 utils/ (Utilitários)
│       ├── __init__.py
│       └── validators.py (CPF, Email, Telefone, etc)
│
├── .env ⚙️ (Variáveis de Ambiente)
├── .env.example 📝 (Exemplo de .env)
├── requirements.txt 📦 (Dependências Python)
├── Dockerfile 🐳 (Container Docker)
├── Makefile 🛠️ (Automação de Tarefas)
├── README.md 📖 (Documentação Principal)
├── QUICKSTART.md 🚀 (Guia Rápido)
└── ARCHITECTURE.md 📐 (Documentação da Arquitetura)
```

## 📊 Resumo de Arquivos

### Entry Point
- **cmd/api/main.py** → Inicializa o FastAPI e todos os componentes

### Configuração
- **config/config.py** → Carrega env vars e settings com Pydantic
- **config/config.yaml** → Configurações YAML
- **.env** → Variáveis de ambiente

### Infraestrutura
- **internal/infra/database/banco_dados.py** → Conexão PostgreSQL (SQLAlchemy)
- **internal/infra/http/server.py** → Setup FastAPI
- **internal/infra/http/middlewares.py** → CORS, Logger, etc
- **internal/infra/logger/zap.py** → Logging

### Módulo de Produtos (Exemplo)
- **internal/modules/produto/dto.py** → DTOs (Pydantic)
- **internal/modules/produto/entity.py** → Models (SQLAlchemy)
- **internal/modules/produto/handler.py** → Controllers HTTP
- **internal/modules/produto/repository.py** → Data Access
- **internal/modules/produto/service.py** → Lógica de Negócio
- **internal/modules/produto/routes.py** → Rotas

### Utilities
- **pkg/apperrors/exceptions.py** → Exceções personalizadas
- **pkg/utils/validators.py** → Validadores (CPF, Email, etc)

### Auxiliares
- **requirements.txt** → Dependências: FastAPI, SQLAlchemy, Pydantic, etc
- **Dockerfile** → Container Docker pronto para produção
- **Makefile** → Automação: install, run, dev, test, etc
- **README.md** → Documentação completa
- **QUICKSTART.md** → Guia rápido de início

## 🎯 Fluxo de Requisição

```
Cliente HTTP
    ↓
[FastAPI Router - handler.py]
    ↓
[Pydantic DTO - Validação]
    ↓
[Service - Lógica de Negócio]
    ↓
[Repository - Data Access]
    ↓
[SQLAlchemy - Queries SQL]
    ↓
[PostgreSQL - Database]
    ↓
[Entity - Resultado]
    ↓
[DTO - Serialização]
    ↓
[JSON Response]
    ↓
Cliente HTTP
```

## 🔑 Responsabilidades por Camada

| Camada | Arquivo | Responsabilidade |
|--------|---------|------------------|
| **API** | handler.py | Receber HTTP, validar com DTO, orquestrar resposta |
| **Validação** | dto.py | Pydantic - valida entrada/saída |
| **Negócio** | service.py | Lógica, regras, orquestração |
| **Dados** | repository.py | Queries SQL, transações |
| **BD** | entity.py | Mapeamento SQLAlchemy |
| **Infra** | banco_dados.py | Conexão, pool, migrations |

## 📚 Tecnologias Utilizadas

| Componente | Tecnologia | Versão | Propósito |
|-----------|-----------|--------|----------|
| **Framework Web** | FastAPI | 0.104.1 | API REST assíncrona |
| **Servidor** | Uvicorn | 0.24.0 | Servidor ASGI |
| **ORM** | SQLAlchemy | 2.0.23 | Mapeamento de objetos |
| **Validação** | Pydantic | 2.5.0 | DTOs e validação |
| **Banco de Dados** | PostgreSQL | - | Persistência |
| **Driver BD** | psycopg2 | 2.9.9 | Conexão PostgreSQL |
| **Env Vars** | python-dotenv | 1.0.0 | Variáveis de ambiente |

## 🚀 Quick Start

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar .env
cp .env.example .env

# 3. Iniciar aplicação
make dev

# 4. Acessar docs
# http://localhost:8000/docs
```

## 🧩 Como Adicionar Novo Módulo

Exemplo: Criar módulo de "Categorias"

```bash
# 1. Criar estrutura
mkdir -p internal/modules/categoria

# 2. Criar arquivos (copiar de produto como template):
touch internal/modules/categoria/{__init__,dto,entity,handler,repository,service,routes}.py

# 3. Implementar:
#    - dto.py: CategoriaCreateRequest, CategoriaResponse
#    - entity.py: Class Categoria(Base)
#    - repository.py: CategoriaRepository
#    - service.py: CategoriaService
#    - handler.py: @router.post(), @router.get(), etc
#    - routes.py: exportar router

# 4. Registrar em cmd/api/main.py:
from internal.modules.categoria.routes import router as categoria_router
app.include_router(categoria_router)
```

## ✅ Checklist de Implementação

- ✅ Estrutura de diretórios criada
- ✅ FastAPI configurado com middlewares
- ✅ SQLAlchemy com PostgreSQL
- ✅ Pydantic para validação
- ✅ Módulo de Produtos completo (CRUD)
- ✅ Tratamento de erros customizado
- ✅ Logging estruturado
- ✅ Documentação automática (Swagger)
- ✅ Docker preparado
- ✅ Makefile com automação
- ✅ Exemplos de uso
- ✅ Documentação da arquitetura

## 🎓 Próximos Passos

1. **Testes Unitários** → pytest
2. **Autenticação** → JWT tokens
3. **Rate Limiting** → Proteção contra abuso
4. **Caching** → Redis
5. **CI/CD** → GitHub Actions
6. **Monitoring** → Prometheus, Grafana
7. **API Versioning** → v1, v2
8. **Documentação OpenAPI** → Swagger

---

**Projeto pronto para produção! 🎉**
