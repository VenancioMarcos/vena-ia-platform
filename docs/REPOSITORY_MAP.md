# Mapa do Repositório

**Data da auditoria:** 2026-07-29
**Arquitetura:** monorepo com Modular Monolith

| Área | Responsabilidade | Estado |
|---|---|---|
| `apps/api` | API FastAPI, persistência e módulos de domínio | IMPLEMENTED |
| `apps/api/app/modules/users` | usuários e papéis | PARTIAL |
| `apps/api/app/modules/projects` | projetos | IMPLEMENTED |
| `apps/api/app/modules/files` | metadados legados de arquivos | PARTIAL |
| `apps/api/app/modules/chats` | chats e mensagens persistentes | PARTIAL |
| `apps/api/app/modules/documents` | upload, MinIO, catálogo e estados | IMPLEMENTED |
| `apps/api/app/modules/ai` | endpoints da camada de IA | IMPLEMENTED |
| `packages/ai` | contratos, factory, service e provider OpenAI | IMPLEMENTED |
| `apps/web` | landing page e dashboard de projetos | PARTIAL |
| `packages/auth` | autenticação compartilhada | PLACEHOLDER |
| `packages/database` | pacote compartilhado de banco | PLACEHOLDER |
| `packages/ui` | componentes compartilhados | PLACEHOLDER |
| `packages/engineering` | domínio CAD/CAM/CNC | PLACEHOLDER |
| `services/rag` | ingestão e busca semântica | PLACEHOLDER |
| `services/parser-step` | parser STEP | PLACEHOLDER |
| `services/parser-dxf` | parser DXF | PLACEHOLDER |
| `services/parser-stl` | parser STL | PLACEHOLDER |
| `apps/api/tests` | testes backend e AI Layer | IMPLEMENTED |
| `tests` | testes transversais/e2e | PLACEHOLDER |
| `.github/workflows` | CI de backend e frontend | IMPLEMENTED |
| `docker-compose.yml` | PostgreSQL/pgvector, Redis, MinIO, API e Web | IMPLEMENTED |
| `docs/research` | documentação acadêmica | PLACEHOLDER |

## Tecnologias localizadas

- Python 3.13 como alvo; FastAPI, Pydantic v2, SQLAlchemy e Alembic.
- PostgreSQL 17 com pgvector; SQLite em memória nos testes.
- Redis e MinIO.
- Next.js 15, React 19, TypeScript e Tailwind CSS.
- Pytest, Ruff, mypy e GitHub Actions.
- Docker e Docker Compose.
- OpenAI API por adaptador HTTP próprio.

## Configurações e integração

- Configuração: `.env.example`, `apps/api/app/core/config.py`, `apps/web/next.config.ts`.
- Banco: duas migrations Alembic; head `4c3d8f1a2b7e`.
- Armazenamento: MinIO no módulo Documents.
- IA externa: OpenAI, desabilitada quando `OPENAI_API_KEY` não está configurada.
- CI: `backend-ci.yml` e `frontend-ci.yml`; não há CD/deploy automático.

## Ausências confirmadas

- autenticação real;
- parser, OCR, chunking, indexação, pgvector aplicado e RAG;
- CAD, CAM, CNC, G-code e simulação;
- testes frontend/e2e;
- notebooks e artefatos acadêmicos além da estrutura documental;
- observabilidade além do health check e tratamento básico de erros.
