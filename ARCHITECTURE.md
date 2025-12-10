# 📐 Documentação da Arquitetura

## Visão Geral

Esta API segue a **Arquitetura Limpa (Clean Architecture)** combinada com padrões de **Arquitetura Hexagonal**, garantindo:

- ✅ Separação de responsabilidades
- ✅ Código testável e manutenível
- ✅ Independência de frameworks
- ✅ Facilidade na evolução

## 🏗️ Estrutura em Camadas

```
┌─────────────────────────────────────────────┐
│           HTTP HANDLERS (FastAPI)           │ ← Recebe requisições
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│          DTOs (Pydantic)                    │ ← Validação de entrada/saída
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│        SERVICE (Lógica de Negócio)          │ ← Regras de negócio
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         REPOSITORY (Dados)                  │ ← Queries SQL
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│        ENTITIES (SQLAlchemy Models)         │ ← Modelos de BD
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│             DATABASE (PostgreSQL)           │ ← Persistência
└─────────────────────────────────────────────┘
```

## 📦 Descrição das Camadas

### 1. **Handlers (Internal/Modules/Produto/handler.py)**

**Responsabilidade:** Receber requisições HTTP e coordenar respostas

```python
@router.post("/produtos")
async def criar_produto(produto_request: ProdutoCreateRequest, ...):
    # Recebe a requisição
    # Chama a service
    # Retorna a resposta
    return service.criar_produto(produto_request)
```

**O que faz:**
- ✅ Valida entrada com Pydantic (automático)
- ✅ Transforma DTOs em dados de entrada
- ✅ Trata exceções e retorna HTTP apropriado
- ✅ Define rotas e documentação

**O que NÃO faz:**
- ❌ Lógica de negócio
- ❌ Acesso direto ao banco
- ❌ Transformações complexas

---

### 2. **Services (Internal/Modules/Produto/service.py)**

**Responsabilidade:** Implementar lógica de negócio

```python
class ProdutoService:
    def criar_produto(self, produto_request: ProdutoCreateRequest):
        # Validar preço > 0
        # Validar quantidade >= 0
        # Chamar repository
        # Retornar resposta
        return self.repository.create(...)
```

**O que faz:**
- ✅ Valida regras de negócio
- ✅ Orquestra operações complexas
- ✅ Transforma dados entre camadas
- ✅ Implementa workflows

**O que NÃO faz:**
- ❌ Conhecer detalhes HTTP
- ❌ Executar queries diretas
- ❌ Formatação de respostas

---

### 3. **Repositories (Internal/Modules/Produto/repository.py)**

**Responsabilidade:** Abstrair acesso a dados

```python
class ProdutoRepository:
    def create(self, produto_data: dict) -> Produto:
        # Executa INSERT
        # Retorna entidade
        produto = Produto(**produto_data)
        self.db.add(produto)
        self.db.commit()
        return produto
```

**O que faz:**
- ✅ Executa queries SQL (SQLAlchemy)
- ✅ Transforma dados de/para BD
- ✅ Gerencia transações
- ✅ Implementa paginação

**O que NÃO faz:**
- ❌ Validações de negócio
- ❌ Formatação de saída
- ❌ Coordenação de operações

---

### 4. **DTOs (Internal/Modules/Produto/dto.py)**

**Responsabilidade:** Definir contrato de entrada/saída

```python
class ProdutoCreateRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    preco: float = Field(..., gt=0)
    quantidade: int = Field(default=0, ge=0)

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    preco: float
    criado_em: datetime
```

**O que faz:**
- ✅ Valida entrada com Pydantic
- ✅ Define schema da API
- ✅ Gera documentação automática
- ✅ Serializa saída

**O que NÃO faz:**
- ❌ Lógica
- ❌ Persistência
- ❌ Transformações

---

### 5. **Entities (Internal/Modules/Produto/entity.py)**

**Responsabilidade:** Representar tabelas do banco de dados

```python
class Produto(Base):
    __tablename__ = "produtos"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    preco = Column(Float, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
```

**O que faz:**
- ✅ Mapeia tabelas do BD (SQLAlchemy ORM)
- ✅ Define tipos de coluna
- ✅ Relacionamentos
- ✅ Validações em nível de BD

**O que NÃO faz:**
- ❌ Validação de negócio
- ❌ Serialização
- ❌ Acesso ao BD

---

## 🔄 Fluxo de uma Requisição

```
1. Cliente faz requisição HTTP
   ↓
2. Handler recebe requisição
   ├─ Pydantic valida dados (DTO)
   ├─ Se inválido → retorna 400
   └─ Se válido → continua
   ↓
3. Handler chama Service
   ├─ Service valida regras de negócio
   ├─ Se inválido → exception
   └─ Se válido → continua
   ↓
4. Service chama Repository
   ├─ Repository executa query
   ├─ Commit/Rollback automático
   └─ Retorna Entity
   ↓
5. Service transforma Entity em DTO
   ├─ Pydantic serializa
   └─ Retorna para Handler
   ↓
6. Handler retorna resposta HTTP
   ├─ Status code apropriado
   ├─ JSON formatado
   └─ Headers
   ↓
7. Cliente recebe resposta
```

## 🎯 Exemplo Prático: Criar Produto

### Requisição HTTP
```http
POST /produtos HTTP/1.1
Content-Type: application/json

{
  "nome": "Notebook",
  "preco": 3000.00,
  "quantidade": 10,
  "categoria": "Eletrônicos"
}
```

### 1. Handler recebe
```python
@router.post("/produtos")
async def criar_produto(
    produto_request: ProdutoCreateRequest,  # DTO validado
    service: ProdutoService = Depends(get_produto_service)
):
    return service.criar_produto(produto_request)
```

### 2. Service executa lógica
```python
def criar_produto(self, produto_request: ProdutoCreateRequest):
    # Validação 1: Preço positivo
    if produto_request.preco <= 0:
        raise BadRequestError("Preço deve ser positivo")
    
    # Validação 2: Quantidade não negativa
    if produto_request.quantidade < 0:
        raise BadRequestError("Quantidade não pode ser negativa")
    
    # Transforma para dict
    produto_data = produto_request.dict()
    
    # Chama repository
    produto = self.repository.create(produto_data)
    
    # Transforma entidade em DTO
    return ProdutoResponse.from_orm(produto)
```

### 3. Repository persiste
```python
def create(self, produto_data: dict) -> Produto:
    produto = Produto(**produto_data)  # Cria entidade
    self.db.add(produto)               # Adiciona à sessão
    self.db.commit()                   # Persiste
    self.db.refresh(produto)           # Recarrega IDs gerados
    return produto
```

### 4. Entity é persistida
```sql
INSERT INTO produtos 
(nome, preco, quantidade, categoria, criado_em, atualizado_em) 
VALUES 
('Notebook', 3000.00, 10, 'Eletrônicos', NOW(), NOW())
```

### 5. Resposta retorna
```json
{
  "id": 1,
  "nome": "Notebook",
  "preco": 3000.00,
  "quantidade": 10,
  "categoria": "Eletrônicos",
  "criado_em": "2025-12-10T14:30:00",
  "atualizado_em": "2025-12-10T14:30:00"
}
```

---

## 🛡️ Padrões de Tratamento de Erros

### Erros Customizados

```python
# AppErrors padronizados
NotFoundError         # 404
BadRequestError       # 400
UnauthorizedError     # 401
ForbiddenError        # 403
ConflictError         # 409
InternalServerError   # 500
```

### Fluxo de Exceção

```python
try:
    produto = service.criar_produto(dto)  # Pode lançar exceção
except NotFoundError as e:
    return HTTPException(status_code=404, detail=str(e))
except BadRequestError as e:
    return HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Erro: {str(e)}")
    return HTTPException(status_code=500, detail="Erro interno")
```

---

## 📊 Dependency Injection

FastAPI usa Dependency Injection para injetar dependências:

```python
def get_db() -> Session:
    """Fornece sessão do banco"""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

def get_produto_service(db: Session = Depends(get_db)) -> ProdutoService:
    """Fornece serviço com repository injetado"""
    repository = ProdutoRepository(db)
    return ProdutoService(repository)

@router.post("/produtos")
async def criar_produto(
    produto_request: ProdutoCreateRequest,
    service: ProdutoService = Depends(get_produto_service)  # Injeção!
):
    return service.criar_produto(produto_request)
```

**Benefícios:**
- ✅ Testabilidade (pode mockar dependências)
- ✅ Reutilização
- ✅ Separação de responsabilidades
- ✅ Configuração flexível

---

## 🧪 Testabilidade

Cada camada pode ser testada isoladamente:

```python
# Testar Handler
@pytest.mark.asyncio
async def test_criar_produto():
    # Mock service
    mock_service = MagicMock()
    mock_service.criar_produto.return_value = produto_response
    
    # Testar handler com mock
    response = await criar_produto(dto, service=mock_service)
    assert response.id == 1

# Testar Service
def test_service_valida_preco():
    service = ProdutoService(mock_repository)
    
    # Deve rejeitar preço negativo
    with pytest.raises(BadRequestError):
        service.criar_produto(dto_preco_negativo)

# Testar Repository
def test_repository_create():
    repo = ProdutoRepository(db_session)
    
    produto = repo.create({...})
    assert produto.id is not None
```

---

## 🔌 Middleware e Infraestrutura

### Middlewares (Internal/Infra/HTTP/middlewares.py)

```python
# Logger Middleware - registra todas as requisições
class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        # ... logging
        response = await call_next(request)
        # ... log de resposta
        return response

# CORS Middleware - permite requisições entre domínios
configure_cors(app, cors_config)
```

### Database (Internal/Infra/Database/banco_dados.py)

```python
class Database:
    def init(self):
        # Cria engine com pool de conexões
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=40
        )
    
    def get_session(self) -> Session:
        # Retorna nova sessão
        return self.SessionLocal()
    
    def create_tables(self):
        # Cria schema no BD
        Base.metadata.create_all(bind=self.engine)
```

---

## 🔄 Ciclo de Vida da Aplicação

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("🚀 Iniciando aplicação...")
    db.init()
    db.create_tables()
    
    yield  # Aplicação roda
    
    # SHUTDOWN
    logger.info("🛑 Encerrando aplicação...")
    db.close()
```

---

## 📈 Escalabilidade

### Como expandir para novos módulos

```
internal/modules/
├── produto/          ← Existente
│   ├── dto.py
│   ├── entity.py
│   ├── handler.py
│   ├── repository.py
│   ├── service.py
│   └── routes.py
│
└── categoria/        ← Novo módulo
    ├── dto.py
    ├── entity.py
    ├── handler.py
    ├── repository.py
    ├── service.py
    └── routes.py
```

Adicionar no `main.py`:
```python
from internal.modules.categoria.routes import router as categoria_router
app.include_router(categoria_router)
```

---

## 🎓 Conclusão

Esta arquitetura oferece:

- **Manutenibilidade**: Código organizado e testável
- **Escalabilidade**: Fácil adicionar novos módulos
- **Flexibilidade**: Trocar implementações sem afetar outras camadas
- **Clareza**: Responsabilidades bem definidas
- **Qualidade**: Validação em múltiplos níveis

---

**Arquitetura pensada para crescer com sua aplicação! 🚀**
