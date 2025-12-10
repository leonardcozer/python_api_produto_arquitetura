@echo off
REM Script para verificar se python-logging-loki está instalado no container

echo 🔍 Verificando instalação do python-logging-loki...
echo.

echo 📋 Listando pacotes instalados relacionados a loki:
docker compose exec web pip list | findstr /i loki
if errorlevel 1 echo ❌ Nenhum pacote relacionado a loki encontrado

echo.
echo 🔍 Tentando importar o módulo:
docker compose exec web python -c "try:^
    from python_logging_loki import LokiHandler^
    print('✅ python-logging-loki está instalado e pode ser importado')^
    print(f'   Versão do módulo: {LokiHandler.__module__}')^
except ImportError as e:^
    print(f'❌ Erro ao importar: {e}')"

echo.
echo 📦 Verificando requirements.txt no container:
docker compose exec web type requirements.txt | findstr /i loki
if errorlevel 1 echo ❌ python-logging-loki não encontrado no requirements.txt

