# 🔍 Tempo - Distributed Tracing Setup

Guia para configurar o Tempo (distributed tracing) no Grafana.

## 📋 O que é o Tempo?

O Tempo é um sistema de distributed tracing do Grafana Labs que permite rastrear requisições através de múltiplos serviços, visualizando o fluxo completo de uma operação.

## 🔗 URL do Tempo

Baseado na sua configuração atual:
- **Grafana**: `172.30.0.45:3000`
- **Loki**: `http://172.30.0.45:3100`

A URL do Tempo deve ser:

### Se o Tempo está no mesmo servidor:
```
http://172.30.0.45:3200
```

### Se o Tempo está em um container Docker (mesma rede):
```
http://tempo:3200
```

### Se o Tempo está em outro servidor:
```
http://<IP_DO_TEMPO>:3200
```

## ⚠️ Por que `localhost:3200` não funciona?

O erro "Please enter a valid URL" ocorre porque:
1. O Grafana está rodando em `172.30.0.45:3000`
2. Quando você usa `localhost`, o Grafana tenta acessar `localhost` **do ponto de vista do container/servidor do Grafana**
3. Se o Tempo não está rodando no mesmo container/servidor, `localhost` não funcionará

## 🚀 Como Verificar se o Tempo está Rodando

### Verificar se o Tempo está acessível:

```bash
# Teste direto
curl http://172.30.0.45:3200/ready

# Ou se estiver em Docker
curl http://tempo:3200/ready
```

### Verificar se a porta está aberta:

```bash
# No servidor onde o Tempo deveria estar
netstat -tuln | grep 3200
# ou
ss -tuln | grep 3200
```

## 📦 Instalando o Tempo (se ainda não estiver instalado)

### Opção 1: Docker Compose

Adicione ao seu `docker-compose.yml`:

```yaml
services:
  tempo:
    image: grafana/tempo:latest
    container_name: tempo
    command: ["-config.file=/etc/tempo.yaml"]
    volumes:
      - ./tempo-config.yaml:/etc/tempo.yaml
      - tempo-data:/var/tempo
    ports:
      - "3200:3200"  # HTTP
      - "4317:4317"  # OTLP gRPC
      - "4318:4318"  # OTLP HTTP
    networks:
      - observability

volumes:
  tempo-data:

networks:
  observability:
    external: false
```

### Opção 2: Standalone

```bash
docker run -d \
  --name tempo \
  -p 3200:3200 \
  -p 4317:4317 \
  -p 4318:4318 \
  grafana/tempo:latest \
  -config.file=/etc/tempo.yaml
```

## ⚙️ Configuração do Tempo

Crie um arquivo `tempo-config.yaml`:

```yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        http:
          endpoint: 0.0.0.0:4318
        grpc:
          endpoint: 0.0.0.0:4317

ingester:
  max_block_duration: 5m

compactor:
  compaction:
    block_retention: 1h
    compacted_block_retention: 10m

storage:
  trace:
    backend: local
    local:
      path: /var/tempo/traces
    pool:
      max_workers: 100
      queue_depth: 10000
```

## 🔧 Configuração no Grafana

1. **Acesse**: Grafana → Connections → Data sources → Add data source
2. **Selecione**: Tempo
3. **URL**: Use uma das opções abaixo baseado na sua infraestrutura:

   **Se Tempo está no mesmo servidor:**
   ```
   http://172.30.0.45:3200
   ```

   **Se Tempo está em Docker (mesma rede):**
   ```
   http://tempo:3200
   ```

   **Se Tempo está em outro servidor:**
   ```
   http://<IP_DO_SERVIDOR_TEMPO>:3200
   ```

4. **Clique em "Save & Test"**

## 🐍 Integrando Tempo na Aplicação Python

Para enviar traces para o Tempo, você precisa integrar OpenTelemetry:

### 1. Instalar dependências

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-exporter-otlp
```

### 2. Adicionar ao `requirements.txt`

```
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-exporter-otlp==1.21.0
```

### 3. Configurar na aplicação

Adicione ao `cmd/api/main.py`:

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Configurar OpenTelemetry
def setup_tracing():
    trace.set_tracer_provider(TracerProvider())
    
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://172.30.0.45:4318/v1/traces",  # OTLP HTTP endpoint
        headers={}
    )
    
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrumenta o FastAPI
    FastAPIInstrumentor.instrument_app(app)

# Chame no create_app()
setup_tracing()
```

### 4. Variáveis de ambiente

Adicione ao `.env`:

```env
# Tempo / OpenTelemetry
TEMPO_URL=http://172.30.0.45:3200
OTLP_ENDPOINT=http://172.30.0.45:4318
TRACING_ENABLED=True
```

## ✅ Testando a Conexão

### 1. Teste direto do Tempo

```bash
curl http://172.30.0.45:3200/ready
# Deve retornar: {"status":"ready"}
```

### 2. Teste do Grafana

No Grafana, após configurar o data source:
- Clique em "Save & Test"
- Deve aparecer: "Data source is working"

### 3. Verificar traces

1. Acesse: Grafana → Explore
2. Selecione o data source "Tempo"
3. Execute uma query de trace (ex: `{service_name="produto-api"}`)

## 🔍 Troubleshooting

### Erro: "Please enter a valid URL"

**Causa**: URL incorreta ou Tempo não acessível

**Solução**:
1. Verifique se o Tempo está rodando: `curl http://172.30.0.45:3200/ready`
2. Use o IP correto (não `localhost`)
3. Verifique firewall/portas abertas

### Erro: "Connection refused"

**Causa**: Tempo não está rodando ou porta incorreta

**Solução**:
1. Verifique se o container/serviço do Tempo está ativo
2. Verifique a porta (padrão: 3200)
3. Verifique logs do Tempo

### Erro: "Network unreachable"

**Causa**: Problema de rede entre Grafana e Tempo

**Solução**:
1. Se estiver em Docker, verifique se estão na mesma network
2. Verifique conectividade: `ping <IP_DO_TEMPO>`
3. Verifique firewall

## 📚 Referências

- [Tempo Documentation](https://grafana.com/docs/tempo/latest/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Grafana Tempo Setup](https://grafana.com/docs/tempo/latest/setup/)

## 🎯 Resumo Rápido

**URL para usar no Grafana (baseado na sua infraestrutura):**

```
http://172.30.0.45:3200
```

**Se não funcionar, tente:**
- `http://tempo:3200` (se estiver em Docker)
- `http://<IP_DO_SERVIDOR>:3200` (se estiver em outro servidor)

**Importante**: Nunca use `localhost` se o Grafana e Tempo estão em containers/servidores diferentes!

