#!/bin/bash
# Script para reconstruir o container Docker SEM CACHE

echo "🛑 Parando containers..."
docker compose down

echo "🔨 Reconstruindo imagem Docker SEM CACHE..."
docker compose build --no-cache

echo "🚀 Iniciando containers..."
docker compose up -d

echo "✅ Container reconstruído com sucesso!"
echo "📋 Verificando logs..."
docker compose logs -f web

