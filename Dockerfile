FROM python:3.11-slim-bullseye

WORKDIR /app

# Instala dependências do sistema
RUN sed -i 's|http://deb.debian.org/debian|https://deb.debian.org/debian|g' /etc/apt/sources.list \
     && sed -i 's|http://security.debian.org|https://security.debian.org|g' /etc/apt/sources.list \
     && apt-get update \
     && apt-get install -y --no-install-recommends \
         gcc \
         postgresql-client \
     && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Comando padrão
CMD ["python", "cmd/api/main.py"]
