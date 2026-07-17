# CHANGELOG.md

Todas as mudanças relevantes do Vena_IA Platform são registradas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/) e versionamento [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Adicionado
* Foundation Pack v1.0 — governança, protocolo de colaboração entre IAs (`.ai/`), 7 novos ADRs (`ADR-0002` a `ADR-0008`) e documentação institucional completa (`GOVERNANCE.md`, `AGENTS.md`, `CONTEXT.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`).

---

## [0.3.0] — 2026-07-16 — IA Base

### Adicionado
* AI abstraction layer em `packages/ai`, com contratos tipados para providers, factory e service sem registry global.
* Provider OpenAI com suporte a chat, embeddings e completion.
* Rotas FastAPI `GET /ai/providers` e `POST /ai/{provider}/{chat|embeddings|completion}` com Dependency Injection.
* Mapeamento de erros de provider para HTTP 400, 404, 502 e 503.
* Testes automatizados da AI Layer, totalizando 21 testes aprovados na API.

### Alterado
* AI Layer formalizada como pacote Python instalável na versão `0.3.0` e incluída no runtime Docker da API.
* Backend CI ampliado para mudanças em `packages/ai`, com `ruff`, `mypy` e `pytest` em Python 3.13.
* Metadados da API atualizados para `0.3.0`.

---

## [0.1.0] — 2026-07-10 — Foundation

### Adicionado
* Documentação fundadora: `PROJECT.md`, `docs/adr/ADR-001.md`, `docs/ROADMAP.md`, `docs/DECISIONS.md`.
* Estrutura inicial do monorepo: `apps/`, `packages/`, `services/`, `docs/`, `tests/`, `docker/`, `scripts/`, `.github/`.
* Scaffold de backend (`apps/api`, FastAPI) com endpoint `/health` e rotas iniciais de usuários, projetos, arquivos e chat.
* Scaffold de frontend (`apps/web`, Next.js) com tela inicial em formato de console técnico.
* `docker-compose.yml` com PostgreSQL + pgvector, Redis, MinIO, API e Web.
* Templates de issue e Pull Request, workflows iniciais de CI.
* Repositório publicado publicamente em `github.com/VenancioMarcos/vena-ia-platform`.

### Decidido
* Arquitetura Modular Monolith (`ADR-001`).
* Organização em monorepo (`DEC-004`).
* Stack tecnológica inicial (`DEC-005`).
* Escopo do MVP v1.0 (`DEC-006`).

---

## Convenção de Versão

* **MAJOR** — mudança incompatível na plataforma ou na arquitetura fundamental.
* **MINOR** — nova versão executiva do roadmap (v0.2 Core, v0.3 IA Base etc.) ou funcionalidade relevante.
* **PATCH** — correções e ajustes que não alteram escopo funcional.
