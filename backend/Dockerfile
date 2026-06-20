FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema para psycopg y pymupdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala uv
RUN pip install --no-cache-dir uv

# Copia archivos de dependencias
COPY pyproject.toml .
RUN uv pip install --system -e "."

# Copia el código
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
