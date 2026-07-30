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

## 7. Security Gate v0.4.1

```text
Frontend
  → POST /auth/login
  → cookie HttpOnly / Bearer JWT assinado
  → get_current_user
  → identidade e papel confirmados no banco
  → AuthorizationService
  → recurso próprio, regra administrativa ou resposta segura
```

Senhas são protegidas por PBKDF2-HMAC-SHA256. A autenticação reside em
`apps/api/app/modules/auth`; regras reutilizáveis de papel e propriedade ficam em
`authorization.py`. O frontend nunca define `owner_id` ou `role`.

Uploads passam por tamanho, normalização, extensão, MIME e magic bytes antes de
serem enviados ao MinIO. Na v0.4.1, apenas PDF é permitido.

Detalhes formais: `docs/adr/ADR-0009-security-gate-authentication.md`.

---

## 8. Evolução Planejada

A evolução por fases (v0.2 Core → v1.0 MVP) está detalhada em `docs/ROADMAP.md`. Mudanças estruturais relevantes nesta arquitetura devem gerar um novo ADR em `docs/adr/`.

---

## 9. Fundação RAG v0.5

```text
PDF validado no MinIO
  → TextExtractor (pypdf)
  → páginas com texto normalizado
  → ChunkingStrategy configurável
  → DocumentChunkRepository
  → PostgreSQL: document_chunks
  → AIService: embeddings
  → PostgreSQL/pgvector: vetores + índice HNSW
  → busca semântica autenticada por projeto
  → AIService: resposta fundamentada nos trechos recuperados
```

O processamento permanece no domínio `documents` do monólito modular e reutiliza
a autorização por proprietário/papel da v0.4.1. Contratos `Protocol` isolam
extractor, chunker, repository e service. Embeddings e geração permanecem
desacoplados por `AIService`; pgvector fornece similaridade por cosseno. O prompt
trata documentos como dados não confiáveis e exige resposta restrita ao contexto
recuperado. Decisão formal:
`docs/adr/ADR-0010-rag-foundation.md`.

---

## 10. CAD Inicial v0.6

```text
STEP Part 21 validado no MinIO
  → CADAnalysisService (autorização do documento)
  → StepTextParser (leitura textual conservadora)
  → metadados + entidades + pontos + envelope preliminar
  → relatório técnico com limitações explícitas
```

O parser não executa conteúdo do arquivo e não afirma propriedades topológicas.
Volume e propriedades de massa exigem futuro kernel OpenCascade validado. Decisão:
`docs/adr/ADR-0011-step-parser-foundation.md`.
