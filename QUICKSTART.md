# 🚀 Quick Start - API Produto

## 1️⃣ Instalação Rápida

```bash
# Navegar até o projeto
cd /home/leonardocozer/arquitetura/python/api/produto

# Instalar dependências
pip install -r requirements.txt
```

## 2️⃣ Configurar PostgreSQL

### Opção A: PostgreSQL Local

```bash
# Criar banco de dados
createdb produto_db -U postgres

# Ou usar psql
psql -U postgres -c "CREATE DATABASE produto_db;"
```

### Opção B: PostgreSQL com Docker

```bash
docker run --name postgres-produto \
  -e POSTGRES_DB=produto_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15
```

## 3️⃣ Iniciar a Aplicação

```bash
# Desenvolvimento (com hot-reload)
make dev

# Ou manualmente
python cmd/api/main.py
```

A aplicação estará disponível em: **http://localhost:8000**

## 4️⃣ Acessar Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 5️⃣ Exemplos de Requisições

### Criar um Produto

```bash
curl -X POST http://localhost:8000/produtos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "MacBook Pro",
    "descricao": "Laptop de alta performance",
    "preco": 12999.99,
    "quantidade": 5,
    "categoria": "Eletrônicos"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "nome": "MacBook Pro",
  "descricao": "Laptop de alta performance",
  "preco": 12999.99,
  "quantidade": 5,
  "categoria": "Eletrônicos",
  "criado_em": "2025-12-10T14:30:00",
  "atualizado_em": "2025-12-10T14:30:00"
}
```

### Listar Produtos

```bash
curl http://localhost:8000/produtos?page=1&page_size=10
```

### Obter um Produto Específico

```bash
curl http://localhost:8000/produtos/1
```

### Listar por Categoria

```bash
curl "http://localhost:8000/produtos/categoria/Eletrônicos?page=1&page_size=10"
```

### Buscar Produtos

```bash
curl "http://localhost:8000/produtos/buscar/termo?termo=macbook&page=1&page_size=10"
```

### Atualizar Produto

```bash
curl -X PUT http://localhost:8000/produtos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "preco": 11999.99,
    "quantidade": 3
  }'
```

### Deletar Produto

```bash
curl -X DELETE http://localhost:8000/produtos/1
```

## 🛠️ Comandos Úteis

```bash
# Ver todos os comandos disponíveis
make help

# Inicializar banco de dados
make db-init

# Limpar banco de dados
make db-clean

# Rodar testes
make test

# Formatar código
make format

# Verificar código
make lint

# Limpar arquivos temporários
make clean
```

## 🐳 Executar com Docker

```bash
# Construir imagem
make docker-build

# Executar container
make docker-run
```

## 📝 Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e ajuste conforme necessário:

```bash
cp .env.example .env
```

Edite o `.env` com suas configurações:

```env
# Banco de dados
DATABASE_USER=postgres
DATABASE_PASSWORD=sua_senha
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=produto_db

# Servidor
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO

# Ambiente
ENVIRONMENT=development
DEBUG=True
```

## ✅ Verificar se está funcionando

Acesse: http://localhost:8000/health

Resposta esperada:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

## 🐛 Troubleshooting

### Erro: "Nenhum módulo nomeado 'config'"

Certifique-se de que está executando o comando a partir do diretório raiz do projeto:
```bash
cd /home/leonardocozer/arquitetura/python/api/produto
```

### Erro: "Conexão com banco recusada"

Verifique se PostgreSQL está rodando:
```bash
# Linux/Mac
psql -U postgres -c "SELECT version();"

# Ou com Docker
docker ps | grep postgres
```

### Erro: "Porta 8000 já em uso"

Mude a porta no `.env`:
```env
SERVER_PORT=8001
```

## 📚 Estrutura de Arquivos

```
produto-api/
├── cmd/api/main.py              ← Entry Point
├── config/                       ← Configurações
├── internal/
│   ├── infra/                    ← Infraestrutura
│   └── modules/produto/          ← Lógica de Produtos
├── pkg/                          ← Código reutilizável
├── requirements.txt              ← Dependências
├── Dockerfile                    ← Container
├── Makefile                      ← Automação
└── README.md                     ← Documentação
```

## 🎯 Próximos Passos

1. ✅ Aplicação instalada e rodando
2. 📚 Explorar documentação no Swagger UI
3. 🧪 Criar testes unitários
4. 🔐 Implementar autenticação (JWT)
5. 📦 Deploy em produção

---

**Pronto para usar! 🎉**
