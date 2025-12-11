# 📊 Service Map - Monitoramento de Arquitetura

Este diretório contém configurações para visualizar a arquitetura do sistema usando Node Graph no Grafana, similar ao exemplo mostrado.

## 🎯 O que é o Service Map?

O Service Map (Node Graph) é uma visualização que mostra:
- **Nós (Nodes)**: Representam serviços ou componentes do sistema
- **Arestas (Edges)**: Representam conexões/dependências entre serviços
- **Métricas**: Tempo de resposta, requisições por segundo, taxa de erros
- **Status**: Indicadores visuais de saúde (verde = saudável, vermelho = problemas)

## 📁 Estrutura

```
grafana/
├── dashboards/
│   └── service-map.json          # Dashboard do Service Map
└── provisioning/
    └── dashboards/
        └── dashboards.yml        # Configuração de provisionamento
```

## 🚀 Como Configurar

### 1. Configurar Prometheus como Data Source

No Grafana, adicione o Prometheus como data source:
- URL: `http://prometheus:9090` (ou sua URL do Prometheus)
- Access: Server (default)

### 2. Importar o Dashboard

**Opção A: Via UI do Grafana**
1. Acesse Grafana → Dashboards → Import
2. Cole o conteúdo de `grafana/dashboards/service-map.json`
3. Selecione o data source do Prometheus
4. Clique em "Import"

**Opção B: Via Provisioning (Recomendado)**
1. Copie os arquivos para o volume do Grafana:
   ```bash
   docker cp grafana/dashboards/service-map.json grafana:/etc/grafana/provisioning/dashboards/
   docker cp grafana/provisioning/dashboards/dashboards.yml grafana:/etc/grafana/provisioning/dashboards/
   ```
2. Reinicie o Grafana

### 3. Verificar Métricas

As seguintes métricas devem estar disponíveis no Prometheus:

```promql
# Total de requisições entre serviços
service_map_requests_total

# Duração de requisições
service_map_request_duration_seconds

# Erros entre serviços
service_map_errors_total

# Status de dependências
service_dependency_active

# Saúde dos serviços
service_health_status

# Throughput
service_throughput_rps
```

## 📊 Queries do Node Graph

### Query Principal (Edges)
```promql
service_map_requests_total
```

### Configuração do Node
- **Main Stat**: `rate(service_map_request_duration_seconds_sum[5m]) / rate(service_map_request_duration_seconds_count[5m])` (ms)
- **Secondary Stat**: `rate(service_map_requests_total[5m])` (req/s)
- **Arc**: `service_map_errors_total` (erros)

### Configuração das Edges
- **Main Stat**: Tempo médio de resposta
- **Secondary Stat**: Requisições por segundo

## 🎨 Personalização

### Adicionar Novos Serviços

Para adicionar um novo serviço ao mapa, registre chamadas usando:

```python
from internal.infra.metrics.service_map import record_service_call

record_service_call(
    source_service="produto-api",
    target_service="novo-servico",
    method="GET",
    duration=0.123,
    status_code=200
)
```

### Adicionar Dependências

```python
from internal.infra.metrics.service_map import set_service_dependency

set_service_dependency(
    source_service="produto-api",
    target_service="redis",
    dependency_type="cache",
    active=True
)
```

## 🔍 Serviços Mapeados Atualmente

1. **produto-api** - API principal
2. **postgresql** - Banco de dados
3. **grafana** - Cliente do Grafana (quando acessa métricas)
4. **prometheus** - Cliente do Prometheus (quando coleta métricas)
5. **external-client** - Clientes externos genéricos

## 📈 Métricas Disponíveis

### Por Serviço
- Tempo médio de resposta (ms)
- Requisições por segundo (req/s)
- Taxa de erros (%)
- Status de saúde (healthy/unhealthy)

### Por Conexão
- Latência entre serviços
- Throughput entre serviços
- Taxa de erros na conexão

## 🛠️ Troubleshooting

### O Node Graph não aparece
1. Verifique se o Prometheus está coletando as métricas
2. Verifique se o data source está configurado corretamente
3. Verifique se há dados no intervalo de tempo selecionado

### Serviços não aparecem
1. Verifique se as métricas estão sendo geradas:
   ```bash
   curl http://localhost:8000/metrics | grep service_map
   ```
2. Verifique se o Prometheus está coletando:
   ```bash
   curl http://prometheus:9090/api/v1/query?query=service_map_requests_total
   ```

### Métricas não atualizam
1. Verifique o intervalo de scrape do Prometheus
2. Verifique se a aplicação está gerando métricas
3. Verifique os logs da aplicação

## 📚 Referências

- [Grafana Node Graph Documentation](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/node-graph/)
- [Prometheus Service Discovery](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Service Mesh Observability](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/node-graph/)

