.PHONY: help install run dev test lint format clean docker-build docker-run db-migrate

help:
	@echo "Comandos disponíveis:"
	@echo "  make install        - Instala as dependências do projeto"
	@echo "  make run            - Executa a aplicação em produção"
	@echo "  make dev            - Executa a aplicação em desenvolvimento"
	@echo "  make test           - Executa os testes"
	@echo "  make lint           - Executa verificação de lint"
	@echo "  make format         - Formata o código"
	@echo "  make clean          - Limpa arquivos desnecessários"
	@echo "  make docker-build   - Constrói a imagem Docker"
	@echo "  make docker-run     - Executa a aplicação em um container Docker"
	@echo "  make docker-rebuild - Reconstroi o container com dependências atualizadas"
	@echo "  make db-init        - Inicializa o banco de dados"
	@echo "  make db-clean       - Limpa o banco de dados"

install:
	pip install -r requirements.txt

run:
	python cmd/api/main.py

dev:
	ENVIRONMENT=development DEBUG=True python cmd/api/main.py

test:
	pytest tests/ -v --cov=internal --cov=pkg

lint:
	flake8 internal/ pkg/ config/ cmd/ --max-line-length=120
	pylint internal/ pkg/ config/ cmd/ --disable=all --enable=E,F

format:
	black internal/ pkg/ config/ cmd/ --line-length=120
	isort internal/ pkg/ config/ cmd/

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

docker-build:
	docker build -t api-produto:latest .

docker-run:
	docker run -p 8000:8000 \
		-e DATABASE_HOST=host.docker.internal \
		-e DATABASE_USER=postgres \
		-e DATABASE_PASSWORD=postgres \
		-e DATABASE_NAME=produto_db \
		-e ENVIRONMENT=production \
		api-produto:latest

docker-rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d

docker-rebuild-nocache:
	@echo "🛑 Parando containers..."
	docker compose down
	@echo "🔨 Reconstruindo SEM CACHE..."
	docker compose build --no-cache
	@echo "🚀 Iniciando containers..."
	docker compose up -d
	@echo "✅ Pronto! Verificando logs..."
	docker compose logs -f web

db-init:
	python -c "from internal.infra.database.banco_dados import db; db.init(); db.create_tables(); print('✅ Banco de dados inicializado')"

db-clean:
	python -c "from internal.infra.database.banco_dados import db; db.init(); from internal.modules.produto.entity import Base; Base.metadata.drop_all(bind=db.engine); print('✅ Banco de dados limpo')"

# Targets para desarrollo
.PHONY: install run dev test lint format clean docker-build docker-run db-init db-clean help
