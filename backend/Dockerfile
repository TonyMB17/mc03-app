FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/backend/requirements.txt

COPY backend /app/backend

RUN sed -i 's/\r$//' /app/backend/docker-entrypoint.sh \
    && chmod +x /app/backend/docker-entrypoint.sh \
    && mkdir -p /app/backend/uploads /app/backend/processed_uploads /app/backend/backups /app/data_samples

EXPOSE 8000

ENTRYPOINT ["sh", "/app/backend/docker-entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
