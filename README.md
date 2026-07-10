# Vena_IA Platform

Engenharia inteligente para manufatura CNC.

Vena_IA é uma plataforma profissional baseada em Inteligência Artificial aplicada à Engenharia Mecânica, integrando CAD, CAM, CNC, simulação, pesquisa científica, manufatura inteligente e gestão industrial.

## Status

Fase atual: **v0.1 — Foundation**.

Base documental e estrutura inicial do monorepo em execução.

## Arquitetura

A arquitetura inicial oficial é **Modular Monolith**, conforme registrado em:

* `PROJECT.md`
* `docs/adr/ADR-001.md`
* `docs/ROADMAP.md`
* `docs/DECISIONS.md`

## Stack Inicial

Frontend:

* Next.js
* React
* TypeScript
* Tailwind CSS
* shadcn/ui

Backend:

* Python 3.13
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic v2

Infraestrutura:

* PostgreSQL
* pgvector
* Redis
* MinIO
* Docker Compose

IA:

* OpenAI API
* Embeddings
* RAG
* Agentes especializados

## Estrutura

```text
apps/
├── api/
└── web/

packages/
├── ui/
├── auth/
├── engineering/
├── ai/
└── database/

services/
├── rag/
├── parser-step/
├── parser-dxf/
└── parser-stl/

docs/
tests/
docker/
scripts/
.github/
```

## Desenvolvimento Local

Copie o arquivo de ambiente:

```bash
cp .env.example .env
```

Suba os serviços de infraestrutura:

```bash
docker compose up postgres redis minio
```

Execute a API:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Execute o frontend:

```bash
cd apps/web
npm install
npm run dev
```

## Rotas Iniciais

API:

* `GET /health`
* `GET /users`
* `GET /projects`
* `GET /files`
* `GET /chat`

## Governança

Toda alteração significativa deve atualizar documentação correspondente e, quando aplicável, criar ADR ou registrar decisão em `docs/DECISIONS.md`.

