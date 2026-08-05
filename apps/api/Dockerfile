FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
COPY packages ./packages
COPY apps/api/pyproject.toml ./apps/api/pyproject.toml
COPY apps/api/app ./apps/api/app
COPY apps/api/alembic.ini ./apps/api/alembic.ini
COPY apps/api/migrations ./apps/api/migrations
COPY scripts ./scripts

RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir -e ./apps/api

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
