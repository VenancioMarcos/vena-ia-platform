# CONTEXT.md — Contexto Operacional do Projeto Vena_IA Platform

**Status:** Documento Oficial
**Versão:** 1.3
**Última atualização:** 2026-07-17
**Documentos relacionados:** `PROJECT.md`, `AGENTS.md`, `.ai/ACP.md`

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

* **Fase:** v0.1 — Foundation ✅ concluída → v0.2 — Core ✅ concluída → v0.3 — IA Base ✅ publicada → v0.4.0 — Upload & Base de Conhecimento ✅ concluída e preparada para revisão da release.
* **Repositório:** público, em `github.com/VenancioMarcos/vena-ia-platform`.
* **Arquitetura:** Modular Monolith (`docs/adr/ADR-001.md`), com organização em `apps/`, `packages/`, `services/`.
* **Backend:** `apps/api` v0.4.0 com persistência real via SQLAlchemy — modelos `User`, `Project`, `FileAsset`, `Chat`, `Message` e `Document` organizados por módulo. Alembic configurado com as migrations `2aea3ea35160` e `4c3d8f1a2b7e`. Rotas de `users`, `projects`, `files`, `chat/{project_id}/messages` e `documents` fazem operações persistentes com validação de relações.
* **AI Layer:** `packages/ai` fornece contratos tipados, factory e service sem registry global e provider OpenAI para chat, embeddings e completion. `apps/api` expõe `GET /ai/providers` e `POST /ai/{provider}/{chat|embeddings|completion}`, com Dependency Injection e mapeamento explícito de erros HTTP.
* **Documents:** módulo em `apps/api` com relacionamento `Project (1) — (N) Documents`, repository, service, Dependency Injection e armazenamento físico no MinIO. O pipeline controla somente os estados `UPLOADED`, `PROCESSING`, `READY` e `FAILED`. O catálogo administrativo lista documentos por estado e agrega contagens e bytes armazenados, sem ler ou processar conteúdo. Não há parser, chunking, indexação, embeddings, RAG, OCR, busca ou IA.
* **Frontend:** `apps/web` com dashboard mínimo em `/dashboard`, consumindo a API real para listar e criar projetos. Autenticação real ainda não existe — o formulário cria/reaproveita um usuário simples (limitação conhecida, ver `DEC-011` e `SECURITY.md`).
* **Testes:** suíte `pytest` com 76 testes cobrindo users/projects/files/chats/documents/health e a AI Layer, incluindo segurança de upload, rollbacks, autorização por proprietário, catálogo administrativo, estatísticas, storage MinIO mockado e todas as transições do pipeline. Testes de persistência usam SQLite em memória (`DEC-011`) — PostgreSQL continua sendo o banco oficial (`DEC-005`).
* **Infraestrutura e CI:** a AI Layer é um pacote Python instalável (`vena-ia-ai==0.3.0`) consumido pela API e incluído no build Docker. O Docker Compose completo foi construído e validado com PostgreSQL, Redis, MinIO, API e Web; health, catálogo de documentos, documentos por projeto, estatísticas e início do pipeline responderam HTTP 200. O Backend CI em Python 3.13 executa lint do repositório, `mypy packages/ai` e a suíte `pytest`, inclusive quando apenas `packages/ai` é alterado.
* **Governança documental:** Foundation Pack v1.0 formaliza como múltiplas IAs colaboram no repositório.

---

## 4. O que NÃO está implementado ainda

* Autenticação e autorização reais (o dashboard usa um substituto temporário — criação de usuário por formulário, sem login/senha/token).
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
