# CONTEXT.md — Contexto Operacional do Projeto Vena_IA Platform

**Status:** Documento Oficial
**Versão:** 1.0
**Última atualização:** 2026-07-10
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

* **Fase:** v0.1 — Foundation ✅ concluída → v0.2 — Core ✅ implementada e validada localmente (Docker/Postgres real ainda pendente de confirmação humana).
* **Repositório:** público, em `github.com/VenancioMarcos/vena-ia-platform`.
* **Arquitetura:** Modular Monolith (`docs/adr/ADR-001.md`), com organização em `apps/`, `packages/`, `services/`.
* **Backend:** `apps/api` com persistência real via SQLAlchemy — modelos `User`, `Project`, `FileAsset`, `Chat`, `Message` (um por módulo, `DEC-011`). Alembic configurado com a migration inicial (`2aea3ea35160`). Rotas de `users`, `projects`, `files` e `chat/{project_id}/messages` fazem CRUD real, com validação de relação (ex.: projeto exige usuário existente).
* **Frontend:** `apps/web` com dashboard mínimo em `/dashboard`, consumindo a API real para listar e criar projetos. Autenticação real ainda não existe — o formulário cria/reaproveita um usuário simples (limitação conhecida, ver `DEC-011` e `SECURITY.md`).
* **Testes:** suíte `pytest` com 12 testes cobrindo users/projects/files/chats/health, usando SQLite em memória (`DEC-011`) — PostgreSQL continua sendo o banco oficial (`DEC-005`).
* **Infraestrutura:** `docker-compose.yml` validado (postgres+pgvector, redis, minio). Validação de ponta a ponta feita com SQLite como proxy (sem Docker disponível no ambiente de IA); validação final com PostgreSQL real via Docker ainda pendente do lado do responsável humano.
* **Governança documental:** Foundation Pack v1.0 formaliza como múltiplas IAs colaboram no repositório.

---

## 4. O que NÃO está implementado ainda

* Autenticação e autorização reais (o dashboard usa um substituto temporário — criação de usuário por formulário, sem login/senha/token).
* Upload de arquivos para MinIO (a tabela `files` guarda metadados; o binário ainda não é armazenado — planejado para v0.4).
* Chat com IA / integração OpenAI (mensagens são persistidas, mas não há resposta gerada por IA — planejado para v0.3).
* RAG e busca semântica.
* Qualquer módulo de CAD, CAM, CNC ou simulação.
* CI/CD funcional além dos workflows placeholder.
* `packages/database` como pacote real (os modelos vivem em `apps/api` por decisão deliberada — `DEC-011`).
* Validação com PostgreSQL real (via Docker) e Python 3.13 exato — feita até agora com SQLite e Python 3.12 no ambiente de IA.

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
