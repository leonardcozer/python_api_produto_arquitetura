# 🗺️ Service Map - Guia de Configuração

Este guia explica como configurar o Service Map (Node Graph) no Grafana para visualizar a arquitetura do sistema, similar ao exemplo mostrado.

## 📋 O que foi Implementado

### 1. Métricas de Service Map

Criado o módulo `internal/infra/metrics/service_map.py` que expõe as seguintes métricas:

- `service_map_requests_total` - Total de requisições entre serviços
- `service_map_request_duration_seconds` - Duração de requisições entre serviços
- `service_map_errors_total` - Total de erros entre serviços
- `service_dependency_active` - Status de dependências ativas
- `service_health_status` - Status de saúde dos serviços
- `service_throughput_rps` - Requisições por segundo por serviço

### 2. Integração Automática

As métricas são coletadas automaticamente em:
- **Middleware HTTP**: Registra chamadas de clientes externos para a API
- **Database**: Registra chamadas da API para o PostgreSQL
- **Health Checks**: Atualiza status de saúde e dependências

### 3. Dashboard do Grafana

Criado dashboard em `grafana/dashboards/service-map.json` com:
- Node Graph principal mostrando serviços e conexões
- Painéis de métricas (RPS, latência, erros, saúde)

## 🚀 Como Configurar

### Passo 1: Verificar Métricas

Verifique se as métricas estão sendo expostas:

```bash
curl http://localhost:8000/metrics | grep service_map
```

Você deve ver métricas como:
```
service_map_requests_total{source_service="external-client",target_service="produto-api",method="GET",status_code="200"} 10.0
service_map_request_duration_seconds_bucket{source_service="produto-api",target_service="postgresql",method="query",le="0.1"} 5.0
```

### Passo 2: Configurar Prometheus

Certifique-se de que o Prometheus está coletando métricas da aplicação:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'produto-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Passo 3: Importar Dashboard no Grafana

**Opção A: Via UI (Recomendado para teste)**

1. Acesse Grafana → Dashboards → Import
2. Abra o arquivo `grafana/dashboards/service-map.json`
3. Copie o conteúdo JSON completo
4. Cole no campo "Import via panel json"
5. Selecione o data source do Prometheus
6. Clique em "Import"

**Opção B: Via Provisioning (Recomendado para produção)**

1. Monte o diretório `grafana/` no container do Grafana:
   ```yaml
   # docker-compose.yml
   volumes:
     - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
     - ./grafana/provisioning:/etc/grafana/provisioning
   ```

2. Reinicie o Grafana

### Passo 4: Configurar Node Graph

O Node Graph precisa de queries específicas. Configure assim:

**Query Principal (Edges - Conexões):**
```promql
service_map_requests_total
```

**Configuração do Node:**
- **Main Stat**: `rate(service_map_request_duration_seconds_sum[5m]) / rate(service_map_request_duration_seconds_count[5m]) * 1000` (ms)
- **Secondary Stat**: `rate(service_map_requests_total[5m])` (req/s)
- **Arc (Erros)**: `rate(service_map_errors_total[5m])`

**Configuração das Edges:**
- **Main Stat**: `rate(service_map_request_duration_seconds_sum[5m]) / rate(service_map_request_duration_seconds_count[5m]) * 1000` (ms)
- **Secondary Stat**: `rate(service_map_requests_total[5m])` (req/s)

## 🎨 Personalização

### Adicionar Novos Serviços

Para adicionar um novo serviço ao mapa, use:

```python
from internal.infra.metrics.service_map import (
    record_service_call,
    set_service_dependency
)

# Registrar chamada entre serviços
record_service_call(
    source_service="produto-api",
    target_service="redis",
    method="GET",
    duration=0.05,
    status_code=200
)

# Registrar dependência
set_service_dependency(
    source_service="produto-api",
    target_service="redis",
    dependency_type="cache",
    active=True
)
```

### Adicionar Métricas Customizadas

```python
from internal.infra.metrics.service_map import update_service_throughput

# Atualizar throughput
update_service_throughput("produto-api", 10.5)  # 10.5 req/s
```

## 📊 Serviços Mapeados

Atualmente, o sistema mapeia:

1. **produto-api** - API principal
   - Recebe chamadas de: `external-client`, `grafana`, `prometheus`
   - Faz chamadas para: `postgresql`

2. **postgresql** - Banco de dados
   - Recebe chamadas de: `produto-api`

3. **external-client** - Clientes externos genéricos
   - Faz chamadas para: `produto-api`

4. **grafana** - Quando acessa métricas
   - Faz chamadas para: `produto-api`

5. **prometheus** - Quando coleta métricas
   - Faz chamadas para: `produto-api`

## 🔍 Troubleshooting

### Node Graph não mostra nada

1. **Verifique se há dados:**
   ```bash
   curl "http://prometheus:9090/api/v1/query?query=service_map_requests_total"
   ```

2. **Verifique o intervalo de tempo:**
   - Selecione um intervalo que contenha dados (ex: últimos 15 minutos)

3. **Verifique as queries:**
   - Certifique-se de que a query `service_map_requests_total` retorna dados

### Serviços não aparecem

1. **Gere tráfego:**
   ```bash
   # Faça algumas requisições
   curl http://localhost:8000/health
   curl http://localhost:8000/produtos
   ```

2. **Aguarde alguns segundos** para o Prometheus coletar

3. **Atualize o dashboard**

### Métricas não aparecem no Prometheus

1. **Verifique se a aplicação está expondo métricas:**
   ```bash
   curl http://localhost:8000/metrics | grep service_map
   ```

2. **Verifique a configuração do Prometheus:**
   - Target está acessível?
   - Scrape interval está configurado?

3. **Verifique os logs do Prometheus**

## 📈 Exemplos de Queries PromQL

### Requisições por segundo entre serviços
```promql
rate(service_map_requests_total[5m])
```

### Tempo médio de resposta
```promql
rate(service_map_request_duration_seconds_sum[5m]) / 
rate(service_map_request_duration_seconds_count[5m]) * 1000
```

### Taxa de erros
```promql
rate(service_map_errors_total[5m])
```

### Status de saúde
```promql
service_health_status
```

### Dependências ativas
```promql
service_dependency_active
```

## 🎯 Próximos Passos

1. ✅ Métricas básicas implementadas
2. ⚠️ Adicionar mais serviços (Redis, cache, etc)
3. ⚠️ Adicionar alertas baseados no service map
4. ⚠️ Criar dashboards adicionais para análise detalhada

## 📚 Referências

- [Grafana Node Graph](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/node-graph/)
- [Prometheus Service Discovery](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Service Mesh Observability](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/node-graph/)

