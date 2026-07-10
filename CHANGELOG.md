# CHANGELOG.md

Todas as mudanças relevantes do Vena_IA Platform são registradas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/) e versionamento [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Adicionado
* Foundation Pack v1.0 — governança, protocolo de colaboração entre IAs (`.ai/`), 7 novos ADRs (`ADR-0002` a `ADR-0008`) e documentação institucional completa (`GOVERNANCE.md`, `AGENTS.md`, `CONTEXT.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`).

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
