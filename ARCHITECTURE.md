# ARCHITECTURE.md — Arquitetura Técnica da Vena_IA Platform

**Status:** Documento Oficial
**Versão:** 1.0
**Decisão arquitetural formal:** `docs/adr/ADR-001.md`
**Documentos relacionados:** `PROJECT.md`, `CONTEXT.md`, `docs/DECISIONS.md`

---

## 1. Estratégia Arquitetural

A Vena_IA Platform adota **Modular Monolith** como arquitetura inicial (`docs/adr/ADR-001.md`, `DEC-003`), com organização de código em **monorepo** (`DEC-004`).

Essa escolha prioriza velocidade de desenvolvimento e simplicidade operacional na fase de fundação, mantendo fronteiras de domínio claras o suficiente para permitir extração futura de serviços quando houver justificativa técnica registrada.

---

## 2. Visão Geral do Fluxo

```text
apps/web (Next.js)
        ↓  HTTP/REST
apps/api (FastAPI)
        ↓
packages/database (SQLAlchemy + Alembic)
        ↓
PostgreSQL + pgvector
        ↑
packages/ai  ←→  services/rag  ←→  OpenAI API
```

Arquivos técnicos (STEP, STL, DXF, IGES) fluem por:

```text
Upload → apps/api → MinIO (armazenamento) → services/parser-* → metadados no PostgreSQL
```

---

## 3. Organização do Repositório

```text
apps/
├── api/            Backend FastAPI (Core, Auth, Projetos, Arquivos, Chat)
└── web/             Frontend Next.js (Dashboard, Console técnico)

packages/
├── ui/               Componentes compartilhados
├── auth/             Lógica de autenticação/autorização
├── engineering/       Regras de domínio de engenharia (CAD/CAM/CNC)
├── ai/                Camada de abstração de provedores de IA
└── database/          Modelos, migrations e acesso a dados

services/
├── rag/               Pipeline de ingestão e busca semântica
├── parser-step/       Interpretação de arquivos STEP
├── parser-dxf/        Interpretação de arquivos DXF
└── parser-stl/         Interpretação de arquivos STL

docs/                  Documentação técnica detalhada e ADRs
tests/                 Testes unitários, integração e e2e
docker/                Configuração de infraestrutura local
scripts/               Scripts de automação e bootstrap
.github/               Templates de issue/PR e workflows de CI
.ai/                   Protocolo de colaboração entre agentes de IA
```

A estrutura completa e a justificativa de cada decisão estão em `docs/DECISIONS.md` (`DEC-004`, `DEC-005`).

---

## 4. Domínios Funcionais

| Domínio | Responsabilidade |
|---|---|
| **Core** | Usuários, autenticação, projetos, dashboard, arquivos, chat |
| **Engenharia** | CAD, CAM, CNC, materiais, ferramentas, processos, simulação |
| **Pesquisa** | Artigos científicos, PDFs, referências, DOE, ANOVA, relatórios |
| **Enterprise** | Lean Manufacturing, OEE, PCP, ERP, Analytics |

---

## 5. Stack Tecnológica

A stack completa está registrada em `PROJECT.md` (Seção 8) e `docs/DECISIONS.md` (`DEC-005`). Resumo:

* **Frontend:** Next.js, React, TypeScript, Tailwind CSS, shadcn/ui.
* **Backend:** Python 3.13, FastAPI, SQLAlchemy, Alembic, Pydantic v2.
* **Dados:** PostgreSQL, pgvector, Redis, MinIO.
* **Infraestrutura:** Docker, Docker Compose, GitHub Actions.
* **IA:** OpenAI API, embeddings, RAG, agentes especializados.

Qualquer substituição de tecnologia central exige novo ADR (`GOVERNANCE.md`, Seção 6).

---

## 6. Princípios Arquiteturais

1. Modular Monolith até haver justificativa técnica para extração de serviço.
2. Domínios com fronteiras claras dentro do monolito (sem acoplamento cruzado direto entre `packages/`).
3. IA como camada de infraestrutura (`packages/ai`), nunca acoplada diretamente à lógica de negócio.
4. Segurança desde a fundação (`DEC-009`, `SECURITY.md`).
5. Nenhuma implementação sem documentação correspondente (`PROJECT.md`, Seção 19).

---

## 7. Evolução Planejada

A evolução por fases (v0.2 Core → v1.0 MVP) está detalhada em `docs/ROADMAP.md`. Mudanças estruturais relevantes nesta arquitetura devem gerar um novo ADR em `docs/adr/`.
