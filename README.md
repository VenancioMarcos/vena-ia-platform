# Vena_IA Platform

**Engenharia inteligente para manufatura CNC.**

Vena_IA é uma plataforma profissional baseada em Inteligência Artificial aplicada à Engenharia Mecânica, integrando CAD, CAM, CNC, simulação, pesquisa científica, manufatura inteligente e gestão industrial. O projeto é simultaneamente um produto de software, uma base científica de pesquisa e um ativo estratégico do ecossistema Vena_IA.

Este repositório é desenvolvido com apoio intensivo de múltiplos agentes de Inteligência Artificial (ChatGPT, Claude, Codex, GitHub Copilot, Gemini e agentes próprios) sob um protocolo formal de colaboração — ver [`AGENTS.md`](AGENTS.md) e [`.ai/ACP.md`](.ai/ACP.md).

---

## Status Atual

**Fase:** v0.1 — Foundation ✅ concluída → v0.2 — Core em preparação.

Para o estado técnico exato (o que está implementado vs. apenas planejado), ver [`CONTEXT.md`](CONTEXT.md) — leitura obrigatória antes de qualquer contribuição.

---

## Objetivos

* Criar um copiloto inteligente de engenharia, da interpretação de um modelo CAD ao planejamento de fabricação, cálculo de parâmetros, geração de G-code e relatório técnico.
* Servir de base científica para pesquisa aplicada em engenharia e IA.
* Evoluir como produto comercial escalável para engenharia e indústria.

Objetivos completos em [`PROJECT.md`](PROJECT.md).

---

## Arquitetura

**Modular Monolith**, organizado em monorepo. Decisão formal em [`docs/adr/ADR-001.md`](docs/adr/ADR-001.md); visão técnica completa em [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Stack Prevista

* **Frontend:** Next.js, React, TypeScript, Tailwind CSS, shadcn/ui
* **Backend:** Python 3.13, FastAPI, SQLAlchemy, Alembic, Pydantic v2
* **Dados:** PostgreSQL, pgvector, Redis, MinIO
* **Infraestrutura:** Docker, Docker Compose, GitHub Actions
* **IA:** OpenAI API, embeddings, RAG, agentes especializados

## Organização do Repositório

```text
apps/            Backend (api) e Frontend (web)
packages/         Código compartilhado (ui, auth, engineering, ai, database)
services/         Serviços de domínio (rag, parser-step, parser-dxf, parser-stl)
docs/             Documentação técnica detalhada e ADRs
tests/            Testes unitários, integração e e2e
docker/           Infraestrutura local
scripts/          Automação e bootstrap
.github/          Templates de issue/PR e workflows de CI
.ai/              Protocolo de colaboração entre agentes de IA
```

Detalhes em [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Desenvolvimento Local

```bash
# 1. Configurar ambiente
cp .env.example .env

# 2. Subir infraestrutura
docker compose up postgres redis minio

# 3. Backend
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload

# 4. Frontend
cd apps/web
npm install
npm run dev
```

## Rotas Iniciais da API

* `GET /health`
* `GET /users`
* `GET /projects`
* `GET /files`
* `GET /chat`

---

## Documentação

| Documento | Conteúdo |
|---|---|
| [`PROJECT.md`](PROJECT.md) | Documento mestre — fonte oficial de verdade do projeto |
| [`CONTEXT.md`](CONTEXT.md) | Estado atual do projeto (leitura obrigatória) |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Arquitetura técnica completa |
| [`GOVERNANCE.md`](GOVERNANCE.md) | Regras de governança, segurança e propriedade intelectual |
| [`AGENTS.md`](AGENTS.md) | Papéis e responsabilidades dos agentes de IA |
| [`.ai/ACP.md`](.ai/ACP.md) | Protocolo de colaboração entre agentes de IA |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Como contribuir |
| [`SECURITY.md`](SECURITY.md) | Política de segurança |
| [`ROADMAP.md`](ROADMAP.md) | Resumo executivo do roadmap |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Roadmap executivo completo |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Registro vivo de decisões |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de versões |

---

## Como Contribuir

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md) para branches, Conventional Commits, checklist de Pull Request e fluxo Git recomendado. Agentes de IA devem também seguir [`AGENTS.md`](AGENTS.md) e [`.ai/ACP.md`](.ai/ACP.md).

---

## Roadmap Resumido

v0.1 Foundation ✅ → v0.2 Core → v0.3 IA Base → v0.4 Upload e Base de Conhecimento → v0.5 RAG → v0.6 CAD → v0.7 CAM → v0.8 CNC → v0.9 Pesquisa Científica → v1.0 MVP.

Detalhes completos em [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## Licença

Ver [`LICENSE`](LICENSE).
