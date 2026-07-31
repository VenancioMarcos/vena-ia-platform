# Vena_IA Platform

**Engenharia inteligente para manufatura CNC.**

Vena_IA é uma plataforma profissional baseada em Inteligência Artificial aplicada à Engenharia Mecânica, integrando CAD, CAM, CNC, simulação, pesquisa científica, manufatura inteligente e gestão industrial. O projeto é simultaneamente um produto de software, uma base científica de pesquisa e um ativo estratégico do ecossistema Vena_IA.

Este repositório é desenvolvido com apoio intensivo de múltiplos agentes de Inteligência Artificial (ChatGPT, Claude, Codex, GitHub Copilot, Gemini e agentes próprios) sob um protocolo formal de colaboração — ver [`AGENTS.md`](AGENTS.md) e [`.ai/ACP.md`](.ai/ACP.md).

---

## Status Atual

**Fase:** v1.0 — MVP integrado em validação de release.

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

## Stack

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

## Instalação rápida

```bash
# 1. Configurar ambiente
cp .env.example .env
# Preencher AUTH_SECRET_KEY com segredo aleatório de pelo menos 32 bytes

# 2. Validar, construir e iniciar
docker compose config
docker compose build api web
docker compose up -d
docker compose exec api alembic upgrade head
```

Instruções completas e testadas: [`docs/INSTALLATION.md`](docs/INSTALLATION.md).
Fluxo do usuário: [`docs/QUICKSTART.md`](docs/QUICKSTART.md).

## Rotas Iniciais da API

* `GET /health`
* `POST /auth/register`
* `POST /auth/login`
* `GET /auth/me`
* `POST /auth/logout`
* `GET|POST /users`, `/projects`, `/files`, `/chat` — sessão obrigatória
* `GET|POST|DELETE /documents` — sessão e autorização por projeto
* `POST /chat/{project_id}/ask` — resposta RAG com histórico e evidências
* `GET|POST /research/reports` — relatórios técnicos iniciais em rascunho

Identidade é aceita somente por cookie HttpOnly ou Bearer token validado.
`X-User-ID` não autentica.

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
| [`docs/INSTALLATION.md`](docs/INSTALLATION.md) | Instalação local validada |
| [`docs/QUICKSTART.md`](docs/QUICKSTART.md) | Guia rápido do usuário |
| [`docs/MVP_AUDIT_MATRIX.md`](docs/MVP_AUDIT_MATRIX.md) | Evidência requisito → implementação |

---

## Como Contribuir

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md) para branches, Conventional Commits, checklist de Pull Request e fluxo Git recomendado. Agentes de IA devem também seguir [`AGENTS.md`](AGENTS.md) e [`.ai/ACP.md`](.ai/ACP.md).

---

## Roadmap Resumido

v0.1 Foundation ✅ → v0.2 Core ✅ → v0.3 IA Base ✅ → v0.4 Upload ✅ → v0.4.1 Security Gate ✅ → v0.5 RAG ✅ → v0.6 CAD ✅ → v0.7 CAM ✅ → v0.8 CNC ✅ → v0.9 Pesquisa ✅ → v1.0 MVP em validação.

Detalhes completos em [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## Licença

Ver [`LICENSE`](LICENSE).
