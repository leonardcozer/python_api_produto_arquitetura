# API Produto - Python FastAPI

Uma API REST completa para gerenciamento de produtos desenvolvida com **FastAPI**, **SQLAlchemy**, **Pydantic** e **PostgreSQL**, seguindo a arquitetura limpa e hexagonal.

## 🏗️ Arquitetura

```
my-api-project/
├── cmd/
│   └── api/
│       └── main.py                  # Entry Point
│
├── config/
│   ├── config.py                    # Carregamento de variáveis de ambiente
│   └── config.yaml                  # Configurações locais
│
├── internal/
│   ├── infra/                       # Camada de Infraestrutura
│   │   ├── database/
│   │   │   └── banco_dados.py       # Conexão com PostgreSQL
│   │   ├── http/
│   │   │   ├── server.py            # Configuração FastAPI
│   │   │   └── middlewares.py       # Middlewares (CORS, Logger)
│   │   └── logger/
│   │       └── zap.py               # Configuração de Logs
│   │
│   └── modules/                     # Módulos de Negócio
│       └── produto/                 # Módulo de Produtos
│           ├── dto.py               # DTOs (Pydantic)
│           ├── entity.py            # Models (SQLAlchemy)
│           ├── handler.py           # Controllers/Handlers
│           ├── repository.py        # Queries SQL
│           ├── routes.py            # Definição de rotas
│           └── service.py           # Lógica de negócio
│
├── pkg/                             # Código reutilizável
│   ├── apperrors/                   # Exceções customizadas
│   └── utils/                       # Validadores e utilitários
│
├── .env                             # Variáveis de ambiente
├── requirements.txt                 # Dependências Python
├── Dockerfile                       # Containerização
├── Makefile                         # Automação de tarefas
└── README.md                        # Documentação
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- PostgreSQL 12+
- pip

### Passos

1. **Clone o repositório:**
```bash
git clone <seu-repositorio>
cd produto-api
```

2. **Instale as dependências:**
```bash
make install
```

Ou manualmente:
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
DATABASE_USER=postgres
DATABASE_PASSWORD=sua_senha
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=produto_db
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Configuração do Loki (Grafana)
LOKI_URL=http://172.30.0.45:3100
LOKI_JOB=MONITORAMENTO_PRODUTO
LOKI_ENABLED=True
```

4. **Inicialize o banco de dados:**
```bash
make db-init
```

## 🏃 Execução

### Desenvolvimento (com hot-reload)
```bash
make dev
```

### Produção
```bash
make run
```

### Docker
```bash
make docker-build
make docker-run
```

## 📚 Documentação da API

Após iniciar a aplicação, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📊 Observabilidade com Grafana + Loki

A aplicação está configurada para enviar logs automaticamente para o Loki, permitindo visualização e análise no Grafana.

### Configuração

Os logs são enviados automaticamente quando as seguintes variáveis de ambiente estão configuradas:

- `LOKI_URL`: URL do servidor Loki (padrão: http://172.30.0.45:3100)
- `LOKI_JOB`: Nome do job para identificação no Loki (padrão: MONITORAMENTO_PRODUTO)
- `LOKI_ENABLED`: Habilita/desabilita o envio de logs (padrão: True)

### Visualização no Grafana

1. Acesse o Grafana na URL configurada
2. Configure o Loki como fonte de dados (se ainda não estiver configurado)
3. Use a query `{job="MONITORAMENTO_PRODUTO"}` para filtrar os logs da aplicação
4. Crie painéis e alertas conforme necessário

### Logs Disponíveis

Todos os logs da aplicação são enviados ao Loki, incluindo:
- Logs de inicialização e shutdown
- Logs de requisições HTTP (via middleware)
- Logs de operações de banco de dados
- Logs de serviços e repositórios
- Logs de erros e exceções

## 🔌 Endpoints

### Health Check
```
GET /health
```

### Produtos

#### Criar Produto
```
POST /produtos
Content-Type: application/json

{
  "nome": "Notebook Dell",
  "descricao": "Notebook de alta performance",
  "preco": 4999.99,
  "quantidade": 10,
  "categoria": "Eletrônicos"
}
```

#### Listar Produtos
```
GET /produtos?page=1&page_size=10
```

#### Obter Produto
```
GET /produtos/{id}
```

#### Listar por Categoria
```
GET /produtos/categoria/{categoria}?page=1&page_size=10
```

#### Buscar Produtos
```
GET /produtos/buscar/termo?termo=notebook&page=1&page_size=10
```

#### Atualizar Produto
```
PUT /produtos/{id}
Content-Type: application/json

{
  "nome": "Notebook Dell XPS",
  "preco": 5499.99
}
```

#### Deletar Produto
```
DELETE /produtos/{id}
```

## 🧪 Testes

```bash
make test
```

## 🔍 Lint e Formatting

### Verificar código
```bash
make lint
```

### Formatar código
```bash
make format
```

## 🗃️ Banco de Dados

### Criar tabelas
```bash
make db-init
```

### Limpar banco
```bash
make db-clean
```

## 📦 Comandos Úteis

```bash
make help      # Mostra todos os comandos disponíveis
make clean     # Limpa arquivos temporários
```

## 🏗️ Estrutura de Camadas

### 1. **Camada de Apresentação (Handler)**
- Recebe requisições HTTP
- Valida entrada com Pydantic
- Retorna respostas HTTP

### 2. **Camada de Negócio (Service)**
- Implementa regras de negócio
- Orquestra operações
- Realiza validações complexas

### 3. **Camada de Dados (Repository)**
- Executa queries SQL
- Interage com o banco de dados
- Retorna modelos de entidade

### 4. **Camada de Infraestrutura**
- Configuração de banco de dados
- Middlewares HTTP
- Logging

## 🔐 Boas Práticas

- ✅ Validação em múltiplas camadas
- ✅ Tratamento de erros robusto
- ✅ Logging detalhado com integração Loki/Grafana
- ✅ Separação de responsabilidades
- ✅ DTOs para transferência de dados
- ✅ CORS configurável
- ✅ Pool de conexões otimizado
- ✅ Observabilidade com Grafana + Loki

## 📝 Exemplo de Uso Completo

```bash
# 1. Iniciar a aplicação
make dev

# 2. Criar um produto (em outro terminal)
curl -X POST http://localhost:8000/produtos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Mouse Logitech",
    "descricao": "Mouse wireless confortável",
    "preco": 99.90,
    "quantidade": 50,
    "categoria": "Periféricos"
  }'

# 3. Listar produtos
curl http://localhost:8000/produtos

# 4. Buscar especifico
curl http://localhost:8000/produtos/1

# 5. Atualizar
curl -X PUT http://localhost:8000/produtos/1 \
  -H "Content-Type: application/json" \
  -d '{"preco": 89.90}'

# 6. Deletar
curl -X DELETE http://localhost:8000/produtos/1
```

## 🛠️ Tecnologias

- **FastAPI** 0.104.1 - Framework web assíncrono
- **SQLAlchemy** 2.0.23 - ORM para Python
- **Pydantic** 2.5.0 - Validação de dados
- **psycopg2** 2.9.9 - Driver PostgreSQL
- **Uvicorn** 0.24.0 - Servidor ASGI
- **python-dotenv** 1.0.0 - Gerenciamento de env vars
- **python-logging-loki** 0.3.2 - Integração com Loki para observabilidade

## 📄 Licença

MIT

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou um pull request.

---

**Desenvolvido com ❤️ em Python**
