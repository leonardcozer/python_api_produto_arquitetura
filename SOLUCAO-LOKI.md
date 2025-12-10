# Solução: Instalação do python-logging-loki no Docker

## Problema
O pacote `python-logging-loki` não está sendo instalado no container Docker, mesmo estando no `requirements.txt`.

## Causa
O Docker está usando cache das camadas anteriores, então a nova dependência não é instalada.

## Solução Completa

### 1. Parar os containers
```bash
docker compose down
```

### 2. Remover a imagem antiga (opcional, mas recomendado)
```bash
docker rmi produto-web
# ou
docker rmi $(docker images -q produto-web)
```

### 3. Reconstruir SEM CACHE
```bash
docker compose build --no-cache
```

### 4. Iniciar os containers
```bash
docker compose up
```

## Verificação

Após reconstruir, verifique se o pacote foi instalado:

```bash
docker compose exec web pip list | grep loki
```

Ou execute o script de verificação:
```bash
# Linux/Mac
./verify-loki-install.sh

# Windows
verify-loki-install.bat
```

## Solução Alternativa: Instalar Manualmente no Container

Se ainda não funcionar, instale manualmente:

```bash
docker compose exec web pip install python-logging-loki==0.3.1
docker compose restart web
```

## Comandos Úteis

### Verificar se o pacote está no requirements.txt
```bash
docker compose exec web cat /app/requirements.txt
```

### Verificar pacotes instalados
```bash
docker compose exec web pip list
```

### Testar importação do módulo
```bash
docker compose exec web python -c "from python_logging_loki import LokiHandler; print('OK')"
```

## Após Instalação Bem-Sucedida

Você deve ver nos logs:
```
📡 CONFIGURAÇÃO DO GRAFANA/LOKI
   🔗 Endpoint: http://172.30.0.45:3100/loki/api/v1/push
   📋 JOB: MONITORAMENTO_PRODUTO
   ✅ Handler configurado e pronto para enviar logs
```

Em vez de:
```
⚠️ python-logging-loki não instalado
```

