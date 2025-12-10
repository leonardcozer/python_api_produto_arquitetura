#!/bin/bash
# Script de teste da API - Execute após iniciar a aplicação com 'make dev'

set -e

BASE_URL="http://localhost:8000"
HEADER="Content-Type: application/json"

echo "================================"
echo "🧪 TESTANDO API PRODUTO"
echo "================================"
echo ""

# 1. Health Check
echo "1️⃣  Verificando Health Check..."
curl -s "$BASE_URL/health" | jq . || echo "❌ Erro ao conectar"
echo ""

# 2. Root Endpoint
echo "2️⃣  Acessando endpoint raiz..."
curl -s "$BASE_URL/" | jq . 
echo ""

# 3. Criar Produto 1
echo "3️⃣  Criando primeiro produto..."
PRODUTO1=$(curl -s -X POST "$BASE_URL/produtos" \
  -H "$HEADER" \
  -d '{
    "nome": "MacBook Pro 14\"",
    "descricao": "Laptop de alta performance com M3 Pro",
    "preco": 11999.99,
    "quantidade": 5,
    "categoria": "Computadores"
  }')
echo "$PRODUTO1" | jq .
PRODUTO1_ID=$(echo "$PRODUTO1" | jq -r '.id')
echo "✅ Produto 1 criado com ID: $PRODUTO1_ID"
echo ""

# 4. Criar Produto 2
echo "4️⃣  Criando segundo produto..."
PRODUTO2=$(curl -s -X POST "$BASE_URL/produtos" \
  -H "$HEADER" \
  -d '{
    "nome": "iPhone 15 Pro",
    "descricao": "Smartphone de última geração",
    "preco": 7999.99,
    "quantidade": 20,
    "categoria": "Smartphones"
  }')
echo "$PRODUTO2" | jq .
PRODUTO2_ID=$(echo "$PRODUTO2" | jq -r '.id')
echo "✅ Produto 2 criado com ID: $PRODUTO2_ID"
echo ""

# 5. Criar Produto 3
echo "5️⃣  Criando terceiro produto..."
PRODUTO3=$(curl -s -X POST "$BASE_URL/produtos" \
  -H "$HEADER" \
  -d '{
    "nome": "AirPods Pro",
    "descricao": "Fones de ouvido com cancelamento de ruído",
    "preco": 2299.99,
    "quantidade": 15,
    "categoria": "Acessórios"
  }')
echo "$PRODUTO3" | jq .
PRODUTO3_ID=$(echo "$PRODUTO3" | jq -r '.id')
echo "✅ Produto 3 criado com ID: $PRODUTO3_ID"
echo ""

# 6. Listar todos os produtos
echo "6️⃣  Listando todos os produtos..."
curl -s "$BASE_URL/produtos?page=1&page_size=10" | jq .
echo ""

# 7. Obter um produto específico
echo "7️⃣  Obtendo produto específico (ID: $PRODUTO1_ID)..."
curl -s "$BASE_URL/produtos/$PRODUTO1_ID" | jq .
echo ""

# 8. Listar por categoria
echo "8️⃣  Listando produtos por categoria (Smartphones)..."
curl -s "$BASE_URL/produtos/categoria/Smartphones?page=1&page_size=10" | jq .
echo ""

# 9. Buscar produtos
echo "9️⃣  Buscando produtos com termo 'iPhone'..."
curl -s "$BASE_URL/produtos/buscar/termo?termo=iPhone&page=1&page_size=10" | jq .
echo ""

# 10. Atualizar produto
echo "🔟 Atualizando produto (ID: $PRODUTO1_ID)..."
curl -s -X PUT "$BASE_URL/produtos/$PRODUTO1_ID" \
  -H "$HEADER" \
  -d '{
    "preco": 10999.99,
    "quantidade": 3
  }' | jq .
echo ""

# 11. Verificar atualização
echo "1️⃣ 1️⃣  Verificando produto atualizado..."
curl -s "$BASE_URL/produtos/$PRODUTO1_ID" | jq .
echo ""

# 12. Deletar produto
echo "1️⃣ 2️⃣  Deletando produto (ID: $PRODUTO2_ID)..."
curl -s -X DELETE "$BASE_URL/produtos/$PRODUTO2_ID" -w "\nStatus: %{http_code}\n"
echo ""

# 13. Tentar obter produto deletado (deve retornar 404)
echo "1️⃣ 3️⃣  Tentando obter produto deletado (deve retornar 404)..."
curl -s "$BASE_URL/produtos/$PRODUTO2_ID" -w "\nStatus: %{http_code}\n" | jq .
echo ""

# 14. Listar final
echo "1️⃣ 4️⃣  Listagem final de produtos..."
curl -s "$BASE_URL/produtos" | jq .
echo ""

echo "================================"
echo "✅ TESTES CONCLUÍDOS COM SUCESSO!"
echo "================================"
