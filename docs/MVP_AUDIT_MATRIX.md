# Matriz de Auditoria do MVP v1.0

**Data:** 2026-08-01
**Estado:** MVP publicado e pacotes 1 e 2 da v1.1 validados na Draft PR #11

| Requisito | Implementação | API/serviço | Frontend | Teste | Lacuna/Ação v1.0 |
|---|---|---|---|---|---|
| Cadastro/login/logout/sessão | Auth PBKDF2 + JWT/cookie | `/auth/*` | `/login` | auth/security | Erros consistentes; logout não falha silenciosamente |
| Dashboard/projetos | SQLAlchemy + ownership | `/projects` | `/dashboard` | projects + E2E | Cliente API único e timeout de 30 s |
| Upload PDF | assinatura, MIME, tamanho, MinIO | `/projects/{id}/documents` | detalhe do projeto | documents + E2E | Fluxo exposto na UI |
| Processamento/chunks | pypdf + chunking idempotente | `/documents/{id}/processing` | detalhe do projeto | processing + E2E | v1.1 permite retry de `FAILED` |
| Embeddings/RAG | AI Layer + pgvector | embeddings/search/ask | detalhe do projeto | knowledge + E2E | v1.1 permite reindexar após indisponibilidade |
| Chat/histórico | Chat/Message persistentes | `/chat/{id}/ask`, `/messages` | detalhe do projeto | chats + E2E | Falha persistida é visível sem resposta falsa |
| Evidências | JSON em mensagem do assistente | `ChatService` | fontes por página/chunk/score | E2E | Migration v1.0 |
| Relatório inicial | ResearchReport persistente | `/research/reports` | geração/listagem/reabertura | research + E2E | Evidência validada; falha da lista não bloqueia o projeto |
| Autorização | `AuthorizationService` | recursos subordinados | 401 redireciona; outros erros visíveis | dois usuários no E2E | Não enumera recurso alheio |
| Instalação/uso | documentação versionada | health `version=1.0.0` | versão 1.0 | smoke checklist | Guias v1.0 adicionados |
| CI | workflows backend/frontend | Ruff/mypy/pytest/build | build Next.js | GitHub Checks | Sem deploy ou API paga |

Capacidades CAD, manufatura, CNC e pesquisa continuam disponíveis, mas não fazem
parte do caminho crítico. Seus estados preliminares e gates de revisão permanecem
inalterados.
