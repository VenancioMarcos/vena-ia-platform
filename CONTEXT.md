# CONTEXT.md — Contexto Operacional do Projeto Vena_IA Platform

**Status:** Documento Oficial
**Versão:** 1.8
**Última atualização:** 2026-07-29
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

* **Fase:** v0.1 — Foundation ✅ → v0.2 — Core ✅ → v0.3 — IA Base ✅ → v0.4.0 — Upload ✅ → v0.4.1 — Security Gate implementada e preparada para revisão do CTO. A v0.5 RAG permanece bloqueada até integração.
* **Repositório:** público, em `github.com/VenancioMarcos/vena-ia-platform`.
* **Arquitetura:** Modular Monolith (`docs/adr/ADR-001.md`), com organização em `apps/`, `packages/`, `services/`.
* **Backend:** `apps/api` v0.4.1 com persistência SQLAlchemy, senha PBKDF2, JWT HS256 assinado, cookie HttpOnly/Bearer, expiração e autorização centralizada. `X-User-ID` não autentica. Cadastro força `member`; identidade e propriedade vêm do token validado. Alembic possui as migrations `2aea3ea35160`, `4c3d8f1a2b7e` e `8a1c4e2f9b30`.
* **AI Layer:** `packages/ai` fornece contratos tipados, factory, service e provider OpenAI. Os endpoints de chat, embeddings e completion exigem usuário autenticado.
* **Documents:** upload e catálogo no MinIO protegidos por proprietário/papel. A v0.4.1 aceita somente PDF e valida tamanho, nome, extensão, MIME e assinatura `%PDF-`. O pipeline controla apenas estados; não há parser, chunking, indexação, embeddings, RAG, OCR ou busca.
* **Frontend:** `apps/web` possui cadastro/login, sessão por cookie HttpOnly, logout, tratamento de 401/403 e dashboard que cria projetos usando exclusivamente a identidade autenticada. Typecheck e build de produção foram aprovados.
* **Testes:** suíte `pytest` com 95 testes aprovados cobrindo autenticação, token ausente/inválido/expirado, rejeição de `X-User-ID`, papéis, propriedade, rotas protegidas, upload por magic bytes e regressões existentes. Ruff, mypy integral em 60 arquivos, compile/import, ciclo Alembic e frontend typecheck/build também foram aprovados. Persistência de testes usa SQLite em memória (`DEC-011`); PostgreSQL continua oficial (`DEC-005`).
* **Infraestrutura e CI:** Docker Compose mantém PostgreSQL/pgvector, Redis, MinIO, API e Web. As imagens locais de API e Web foram construídas na revisão final; o frontend possui contexto Docker isolado de artefatos locais. CI backend executa Ruff, mypy e Pytest. CI frontend usa pnpm com lockfile congelado, typecheck e build.
* **Governança documental:** Foundation Pack v1.0 formaliza como múltiplas IAs colaboram no repositório.
* **Security Gate 2026-07-29:** riscos críticos R-001 a R-004 mitigados e revisão final validada no branch `security/v0.4.1-authentication-authorization`, já enviado ao `origin`. A matriz oficial está em `docs/AUTHORIZATION_MATRIX.md`; decisão em `docs/adr/ADR-0009-security-gate-authentication.md`. A criação da Draft PR está em `BLOCKED_REAL`: integração GitHub sem permissão (`403`), autenticação `gh` inválida e navegador GitHub sem sessão.
* **Limites operacionais permanentes:** o controle oficial está ativo em `docs/PERMANENT_OPERATIONAL_LIMITS.md`.

```text
PERMANENT_OPERATIONAL_LIMITS_SOURCE=docs/PERMANENT_OPERATIONAL_LIMITS.md
PERMANENT_OPERATIONAL_LIMITS_ACTIVE=true
```

---

## 4. O que NÃO está implementado ainda

* Revogação imediata de JWT e fluxo administrativo de recuperação/definição de senha para usuários legados.
* Processamento de documentos após o upload, incluindo extração de texto, OCR, parsing, chunking e indexação.
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
