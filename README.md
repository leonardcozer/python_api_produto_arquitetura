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
│   │   │   └── middlewares.py       # Middlewares (CORS, Logger, Métricas)
│   │   ├── logger/
│   │   │   └── zap.py               # Configuração de Logs com Loki
│   │   └── metrics/
│   │       └── prometheus.py       # Métricas do Prometheus
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
# Banco de Dados
DATABASE_USER=postgres
DATABASE_PASSWORD=sua_senha
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=produto_db

# Servidor
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Observabilidade - Grafana/Loki
LOKI_URL=http://172.30.0.45:3100
LOKI_JOB=MONITORAMENTO_PRODUTO
LOKI_ENABLED=True
```

**Nota:** O Loki está habilitado por padrão. Para desabilitar, defina `LOKI_ENABLED=False`.

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
# Construir e executar
make docker-build
make docker-run

# Ou usar docker compose
docker compose up --build

# Reconstruir sem cache (quando adicionar novas dependências)
make docker-rebuild-nocache
```

## 📚 Documentação e Endpoints

Após iniciar a aplicação, acesse:

### Documentação
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Observabilidade
- **Métricas Prometheus**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health

## 📊 Observabilidade - Grafana + Loki + Prometheus

A aplicação possui observabilidade completa com integração ao Grafana, Loki e Prometheus, fornecendo logs estruturados e métricas em tempo real.

### 📡 Grafana + Loki (Logs)

A aplicação envia logs automaticamente para o Loki usando um **handler customizado** (`LokiHandler`) implementado em `internal/infra/logger/zap.py`. Este handler faz POST diretamente para o endpoint do Loki via HTTP, **sem dependências externas** (não utiliza `python-logging-loki`), proporcionando maior controle e flexibilidade.

#### Configuração

Os logs são enviados automaticamente quando as seguintes variáveis de ambiente estão configuradas:

- `LOKI_URL`: URL do servidor Loki (padrão: http://172.30.0.45:3100)
- `LOKI_JOB`: Nome do job para identificação no Loki (padrão: MONITORAMENTO_PRODUTO)
- `LOKI_ENABLED`: Habilita/desabilita o envio de logs (padrão: True)

#### Funcionalidades

- ✅ Envio automático de todos os logs para o Loki
- ✅ Envio em batch (10 logs ou timeout de 5 segundos)
- ✅ Logs informativos sobre cada POST enviado
- ✅ Tratamento de erros sem bloquear a aplicação
- ✅ Thread em background para processamento assíncrono

#### Visualização no Grafana

1. Acesse o Grafana na URL configurada
2. Configure o Loki como fonte de dados (se ainda não estiver configurado)
3. Use a query `{job="MONITORAMENTO_PRODUTO"}` para filtrar os logs da aplicação
4. Crie painéis e alertas conforme necessário

#### Logs Disponíveis

Todos os logs da aplicação são enviados ao Loki, incluindo:
- Logs de inicialização e shutdown
- Logs de requisições HTTP (via middleware)
- Logs de operações de banco de dados
- Logs de serviços e repositórios
- Logs de erros e exceções
- Logs do Uvicorn e FastAPI

### 📈 Prometheus (Métricas)

A aplicação expõe métricas do Prometheus no endpoint `/metrics` para monitoramento e alertas.

#### Endpoint de Métricas

```
GET /metrics
```

Retorna métricas no formato do Prometheus.

#### Métricas Disponíveis

**Métricas HTTP:**
- `http_requests_total`: Total de requisições HTTP (labels: method, endpoint, status_code)
- `http_request_duration_seconds`: Duração das requisições (histograma)
- `http_errors_total`: Total de erros HTTP (status >= 400)

**Métricas do Loki:**
- `loki_logs_sent_total`: Total de logs enviados para o Loki (labels: level, logger)
- `loki_logs_failed_total`: Total de falhas ao enviar logs

**Métricas da Aplicação:**
- `application_info`: Informações da aplicação (version, environment)
- `application_uptime_seconds`: Tempo de atividade da aplicação

**Métricas de Banco de Dados (preparadas):**
- `database_connections_active`: Conexões ativas
- `database_queries_total`: Total de queries (labels: operation, table)

#### Configuração do Prometheus

Adicione ao seu `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'produto-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

#### Visualização no Grafana

1. Configure o Prometheus como fonte de dados no Grafana
2. Crie dashboards usando as métricas disponíveis
3. Configure alertas baseados nas métricas

#### Exemplo de Queries PromQL

```promql
# Taxa de requisições por segundo
rate(http_requests_total[5m])

# Percentil 95 da duração das requisições
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Taxa de erros
rate(http_errors_total[5m])

# Logs enviados para o Loki por minuto
rate(loki_logs_sent_total[1m])
```

## 🔌 Endpoints

### Health Check
```
GET /health
```

Retorna o status da aplicação:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

### Métricas Prometheus
```
GET /metrics
```

Retorna métricas no formato do Prometheus para coleta e visualização.

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
- ✅ Métricas do Prometheus para monitoramento
- ✅ Separação de responsabilidades
- ✅ DTOs para transferência de dados
- ✅ CORS configurável
- ✅ Pool de conexões otimizado
- ✅ Observabilidade completa (Logs + Métricas)
- ✅ Handler customizado do Loki (sem dependências externas)
- ✅ Envio assíncrono de logs em batch

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

### Core
- **FastAPI** 0.104.1 - Framework web assíncrono
- **SQLAlchemy** 2.0.23 - ORM para Python
- **Pydantic** 2.5.0 - Validação de dados
- **psycopg2-binary** 2.9.9 - Driver PostgreSQL
- **Uvicorn** 0.24.0 - Servidor ASGI

### Observabilidade
- **prometheus-client** 0.20.0 - Métricas do Prometheus
- **requests** 2.32.5 - Cliente HTTP para envio de logs ao Loki
- **Handler Customizado Loki** - Implementação própria para envio de logs (sem dependências externas)

### Utilitários
- **python-dotenv** 1.0.0 - Gerenciamento de env vars
- **pydantic-settings** 2.1.0 - Configurações com Pydantic
- **pyyaml** 6.0.1 - Suporte a YAML

## 📄 Licença

MIT

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou um pull request.

---

**Desenvolvido com ❤️ em Python**
