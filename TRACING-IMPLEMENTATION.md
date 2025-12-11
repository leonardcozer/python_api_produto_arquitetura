# 🔍 Implementação de Distributed Tracing com Tempo

Este documento descreve a implementação do distributed tracing usando OpenTelemetry e Tempo na aplicação.

## 📋 O que foi implementado

### 1. Módulo de Tracing (`internal/infra/tracing/opentelemetry_setup.py`)

Criado um módulo dedicado para configuração do OpenTelemetry com as seguintes funcionalidades:

- ✅ Configuração automática do TracerProvider
- ✅ Exporter OTLP para Tempo (gRPC)
- ✅ BatchSpanProcessor para envio eficiente de spans
- ✅ Instrumentação automática do FastAPI
- ✅ Instrumentação automática do SQLAlchemy
- ✅ Tratamento de erros e fallback gracioso

### 2. Configuração via Variáveis de Ambiente

Adicionadas novas configurações em `config/config.py`:

```python
class TempoConfig(BaseSettings):
    endpoint: str = os.getenv("TEMPO_ENDPOINT", "http://172.30.0.45:4317")
    enabled: bool = os.getenv("TEMPO_ENABLED", "True").lower() == "true"
```

### 3. Integração na Aplicação

O tracing foi integrado em `cmd/api/main.py`:

- Configuração do Tempo antes de instrumentar a aplicação
- Instrumentação automática do FastAPI para rastrear requisições HTTP
- Instrumentação automática do SQLAlchemy para rastrear queries
- Logs informativos sobre o status do tracing

### 4. Tracing Manual em Services

Exemplo de uso manual de spans em `internal/modules/produto/service.py`:

```python
from internal.infra.tracing.opentelemetry_setup import get_tracer

tracer = get_tracer(__name__)

def criar_produto(self, produto_request):
    span = tracer.start_span("service.criar_produto")
    try:
        # ... código ...
        span.set_attribute("produto.id", produto.id)
        span.set_status(trace.Status(trace.StatusCode.OK))
    except Exception as e:
        span.record_exception(e)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        raise
    finally:
        span.end()
```

## 📦 Dependências Adicionadas

As seguintes dependências foram adicionadas ao `requirements.txt`:

```
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-instrumentation-sqlalchemy==0.42b0
opentelemetry-exporter-otlp-proto-grpc==1.21.0
```

## ⚙️ Configuração

### Variáveis de Ambiente

Adicione ao seu arquivo `.env`:

```env
# Tempo / OpenTelemetry
TEMPO_ENDPOINT=http://172.30.0.45:4317
TEMPO_ENABLED=True
```

**Nota:** O endpoint deve ser no formato `http://host:port` ou apenas `host:port`. O código trata automaticamente formatos incorretos como `http:host:port`.

### Endpoint do Tempo

- **gRPC (OTLP)**: `http://172.30.0.45:4317` (padrão)
- **HTTP (OTLP)**: `http://172.30.0.45:4318` (alternativa)

A implementação atual usa **gRPC** que é mais eficiente.

## 🚀 Como Funciona

### 1. Inicialização

Quando a aplicação inicia:

1. O módulo `opentelemetry_setup.py` verifica se o OpenTelemetry está instalado
2. Se `TEMPO_ENABLED=True`, configura o TracerProvider
3. Cria o OTLPSpanExporter apontando para o Tempo
4. Instrumenta automaticamente o FastAPI e SQLAlchemy

### 2. Durante Requisições

Para cada requisição HTTP:

1. O FastAPIInstrumentor cria automaticamente um span raiz
2. Cada operação de banco de dados cria um span filho (via SQLAlchemyInstrumentor)
3. Spans manuais podem ser criados em services para operações específicas
4. Todos os spans são enviados em batch para o Tempo

### 3. Visualização

No Grafana:

1. Configure o Tempo como data source (veja `TEMPO-SETUP.md`)
2. Acesse **Explore** → Selecione **Tempo**
3. Use queries como:
   - `{service.name="produto-api"}` - Todos os traces do serviço
   - `{service.name="produto-api", http.method="POST"}` - Apenas POSTs
   - `{service.name="produto-api", status_code="500"}` - Apenas erros

## 📊 O que é Rastreado

### Automático (via Instrumentação)

- ✅ Todas as requisições HTTP (método, path, status code, duração)
- ✅ Todas as queries SQL (query, duração, parâmetros)
- ✅ Erros e exceções
- ✅ Headers HTTP relevantes

### Manual (via Spans)

- ✅ Operações de negócio específicas
- ✅ Validações e regras de negócio
- ✅ Integrações externas
- ✅ Processamento assíncrono

## 🔧 Troubleshooting

### Tracing não está funcionando

1. **Verifique se o OpenTelemetry está instalado:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verifique as variáveis de ambiente:**
   ```bash
   echo $TEMPO_ENDPOINT
   echo $TEMPO_ENABLED
   ```

3. **Verifique os logs da aplicação:**
   - Procure por: `🔍 OPEN TELEMETRY / TEMPO CONFIGURADO`
   - Ou: `⚠️ OpenTelemetry não está instalado`

4. **Teste a conectividade com o Tempo:**
   ```bash
   # Verifique se o Tempo está acessível
   curl http://172.30.0.45:3200/ready
   ```

### Traces não aparecem no Grafana

1. **Verifique se o Tempo está recebendo dados:**
   - Acesse o Tempo diretamente: `http://172.30.0.45:3200`
   - Verifique os logs do container Tempo

2. **Verifique a configuração do data source no Grafana:**
   - URL deve ser: `http://172.30.0.45:3200`
   - Teste a conexão no Grafana

3. **Verifique o intervalo de tempo:**
   - No Grafana Explore, selecione um intervalo recente
   - Traces antigos podem não estar disponíveis

### Erro: "OpenTelemetry não está instalado"

Instale as dependências:

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-sqlalchemy opentelemetry-exporter-otlp-proto-grpc
```

Ou use o requirements.txt:

```bash
pip install -r requirements.txt
```

## 📚 Referências

- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Tempo Documentation](https://grafana.com/docs/tempo/latest/)
- [FastAPI Instrumentation](https://opentelemetry.io/docs/instrumentation/python/automatic/fastapi/)
- [SQLAlchemy Instrumentation](https://opentelemetry.io/docs/instrumentation/python/automatic/sqlalchemy/)

## ✅ Checklist de Implementação

- [x] Módulo de tracing criado
- [x] Configuração via variáveis de ambiente
- [x] Integração na aplicação principal
- [x] Instrumentação automática do FastAPI
- [x] Instrumentação automática do SQLAlchemy
- [x] Exemplo de tracing manual em services
- [x] Tratamento de erros e fallback
- [x] Documentação completa
- [x] Dependências adicionadas ao requirements.txt

## 🎯 Próximos Passos

1. **Adicionar mais spans manuais** em operações críticas
2. **Configurar sampling** para reduzir volume de traces em produção
3. **Adicionar baggage** para propagar contexto entre serviços
4. **Configurar alertas** baseados em traces (latência, erros)
5. **Integrar com logs** usando trace IDs nos logs

