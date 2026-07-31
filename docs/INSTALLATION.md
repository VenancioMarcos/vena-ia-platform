# Instalação local — Vena_IA Platform v1.0

## Requisitos

* Git;
* Docker Desktop com Docker Compose;
* Python 3.13 para execução/testes locais da API;
* Node.js 22 e pnpm 11 para execução local do frontend.

## Configuração

```powershell
git clone https://github.com/VenancioMarcos/vena-ia-platform.git
cd vena-ia-platform
Copy-Item .env.example .env
```

Edite `.env` e substitua os valores `change_me`. Gere
`AUTH_SECRET_KEY` com pelo menos 32 bytes aleatórios. `OPENAI_API_KEY` é opcional
para subir a plataforma, mas embeddings e respostas reais exigem um provedor
configurado. Nunca versione `.env`.

## Inicialização com Docker

```powershell
docker compose config
docker compose build api web
docker compose up -d
docker compose exec api alembic upgrade head
```

URLs:

* Web: `http://localhost:3000`
* API: `http://localhost:8000`
* OpenAPI: `http://localhost:8000/docs`
* Health/version: `http://localhost:8000/health`
* MinIO Console: `http://localhost:9001`

## Desenvolvimento e testes

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install -e "apps/api[dev]"
python -m ruff check .
python -m mypy packages/ai
python -m pytest apps/api

pnpm --dir apps/web install --frozen-lockfile
pnpm --dir apps/web typecheck
pnpm --dir apps/web build
```

Para API local fora do Docker, ajuste hosts de PostgreSQL/Redis/MinIO para
`localhost`, aplique `alembic upgrade head` dentro de `apps/api` e execute
`uvicorn app.main:app --reload`.

## Parada e diagnóstico

```powershell
docker compose ps
docker compose logs api
docker compose down
```

`docker compose down -v` apaga volumes locais e só deve ser usado em ambiente
descartável após confirmação. Erros de IA sem chave devem ser controlados; use os
providers determinísticos apenas nos testes. PDF sem camada textual requer OCR,
que não faz parte da v1.0.
