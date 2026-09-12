FROM python:3.13.11-slim-bookworm@sha256:20080e807bfc404f8450b185cf0fc95d553462673598549613735f70a5b4d5d0

WORKDIR /app

ARG PIP_VERSION=26.1.2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY pyproject.toml ./
COPY packages ./packages
COPY apps/api/pyproject.toml ./apps/api/pyproject.toml
COPY apps/api/app ./apps/api/app
COPY apps/api/alembic.ini ./apps/api/alembic.ini
COPY apps/api/migrations ./apps/api/migrations
COPY scripts ./scripts

RUN apt-get update \
    && apt-get install --yes --no-install-recommends libgl1 \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir "pip==${PIP_VERSION}" \
    && python -m pip install --no-cache-dir . ./apps/api \
    && groupadd --system vena-ia \
    && useradd --system --gid vena-ia --home-dir /app --no-create-home vena-ia \
    && chown -R vena-ia:vena-ia /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"]

USER vena-ia

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
