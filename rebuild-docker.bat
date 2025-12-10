@echo off
REM Script para reconstruir o container Docker com as dependências atualizadas

echo 🛑 Parando containers...
docker compose down

echo 🔨 Reconstruindo imagem Docker...
docker compose build --no-cache

echo 🚀 Iniciando containers...
docker compose up -d

echo ✅ Container reconstruído com sucesso!
echo 📋 Verificando logs...
docker compose logs -f web

