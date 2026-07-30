# CONTEXT.md — Contexto Operacional do Projeto Vena_IA Platform

**Status:** Documento Oficial
**Versão:** 2.0
**Última atualização:** 2026-07-30
**Documentos relacionados:** `PROJECT.md`, `AGENTS.md`, `.ai/ACP.md`, `docs/PERMANENT_OPERATIONAL_LIMITS.md`

---

## 1. Propósito deste documento

O `CONTEXT.md` existe para eliminar perda de contexto entre sessões de trabalho e entre diferentes agentes de IA (ChatGPT, Claude, Codex, GitHub Copilot, Gemini, agentes próprios).

Antes de qualquer IA iniciar uma tarefa neste repositório, ela deve ler este documento. Ele resume o estado atual do projeto de forma que qualquer agente — humano ou artificial — consiga retomar o trabalho sem depender de memória de conversas anteriores.

Este documento é atualizado sempre que uma mudança relevante de estado ocorre (nova fase concluída, nova decisão arquitetural, mudança de prioridade).

---

## 2. O que é a Vena_IA Platform

Plataforma de Inteligência Artificial aplicada à Engenharia Mecânica e Manufatura CNC, com três frentes simultâneas: produto de software comercial, base científica para pesquisa acadêmica e ativo estratégico de automação para o ecossistema Vena_IA.

Missão, visão e objetivos estratégicos completos estão em `PROJECT.md`.

---

## 3. Estado atual do projeto

* **Fase:** v0.1 — Foundation ✅ → v0.2 — Core ✅ → v0.3 — IA Base ✅ → v0.4.0 — Upload ✅ → v0.4.1 — Security Gate publicada ✅ → v0.5 — RAG Foundation implementada e em preparação para revisão.
* **Repositório:** público, em `github.com/VenancioMarcos/vena-ia-platform`.
* **Arquitetura:** Modular Monolith (`docs/adr/ADR-001.md`), com organização em `apps/`, `packages/`, `services/`.
* **Backend:** `apps/api` v0.5.0 com persistência SQLAlchemy, senha PBKDF2, JWT HS256 assinado, cookie HttpOnly/Bearer, expiração e autorização centralizada. `X-User-ID` não autentica. Cadastro força `member`; identidade e propriedade vêm do token validado. Alembic possui as migrations `2aea3ea35160`, `4c3d8f1a2b7e`, `8a1c4e2f9b30` e `b7f3c9d2e614`.
* **AI Layer:** `packages/ai` fornece contratos tipados, factory, service e provider OpenAI. Os endpoints de chat, embeddings e completion exigem usuário autenticado.
* **Documents/RAG Foundation:** upload e catálogo no MinIO continuam protegidos por proprietário/papel e restritos a PDFs validados. A v0.5 extrai texto por página com `pypdf`, cria chunks configuráveis e persiste rastreabilidade por documento, página, índice e offsets. Os estados `UPLOADED`, `PROCESSING`, `READY` e `FAILED` refletem o resultado da ingestão.
* **Frontend:** `apps/web` possui cadastro/login, sessão por cookie HttpOnly, logout, tratamento de 401/403 e dashboard que cria projetos usando exclusivamente a identidade autenticada. Typecheck e build de produção foram aprovados.
* **Testes:** suíte `pytest` ampliada para autenticação, autorização, upload por magic bytes, extração PDF, chunking, persistência, rastreabilidade, estados e endpoints da fundação RAG. Ruff e mypy integral em 64 arquivos estão aprovados nesta entrega; a validação final inclui migration e regressões completas. Persistência de testes usa SQLite em memória (`DEC-011`); PostgreSQL continua oficial (`DEC-005`).
* **Infraestrutura e CI:** Docker Compose mantém PostgreSQL/pgvector, Redis, MinIO, API e Web. As imagens locais de API e Web foram construídas na revisão final; o frontend possui contexto Docker isolado de artefatos locais. CI backend executa Ruff, mypy e Pytest. CI frontend usa pnpm com lockfile congelado, typecheck e build.
* **Governança documental:** Foundation Pack v1.0 formaliza como múltiplas IAs colaboram no repositório.
* **Security Gate 2026-07-30:** riscos críticos R-001 a R-004 mitigados. A PR [#4](https://github.com/VenancioMarcos/vena-ia-platform/pull/4) foi integrada por squash e a release [v0.4.1](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v0.4.1) foi publicada. A matriz oficial está em `docs/AUTHORIZATION_MATRIX.md`; decisão em `docs/adr/ADR-0009-security-gate-authentication.md`.
* **RAG Foundation 2026-07-30:** modelo `DocumentChunk`, extração textual de PDF, chunking configurável, contratos e endpoints mínimos implementados no branch `feature/v0.5-rag-foundation`, conforme `docs/adr/ADR-0010-rag-foundation.md`.
* **Limites operacionais permanentes:** o controle oficial está ativo em `docs/PERMANENT_OPERATIONAL_LIMITS.md`.

```text
PERMANENT_OPERATIONAL_LIMITS_SOURCE=docs/PERMANENT_OPERATIONAL_LIMITS.md
PERMANENT_OPERATIONAL_LIMITS_ACTIVE=true
```

---

## 4. O que NÃO está implementado ainda

* Revogação imediata de JWT e fluxo administrativo de recuperação/definição de senha para usuários legados.
* OCR para PDFs sem camada textual e processamento assíncrono por fila/worker.
* Embeddings, pgvector, indexação vetorial, busca semântica e recuperação de contexto.
* Acoplamento automático entre respostas da AI Layer e o histórico persistido por projeto; a v0.3.0 entrega a camada técnica e os endpoints, sem ampliar o fluxo funcional existente.
* RAG e busca semântica.
* Qualquer módulo de CAD, CAM, CNC ou simulação.
* Deploy/CD automatizado; os workflows atuais cobrem CI de backend e frontend, sem publicação automática.
* `packages/database` como pacote real (os modelos vivem em `apps/api` por decisão deliberada — `DEC-011`).

Nenhuma IA deve assumir que essas funcionalidades existem só porque estão documentadas no roadmap.

---

## 5. Como este documento deve ser usado por agentes de IA

1. Ler `CONTEXT.md` antes de propor ou executar qualquer tarefa.
2. Verificar se a tarefa está alinhada com a fase atual (`ROADMAP.md`).
3. Verificar se existe decisão registrada em `DECISIONS.md` ou ADR que restrinja a abordagem.
4. Ao concluir uma tarefa relevante, propor a atualização deste documento (Seção 3) como parte da entrega.

---

## 6. Fonte de verdade

Em caso de conflito entre este documento e qualquer conversa, memória de sessão ou instrução informal, prevalece o conteúdo versionado no repositório. Ver `GOVERNANCE.md`, Seção 2.
