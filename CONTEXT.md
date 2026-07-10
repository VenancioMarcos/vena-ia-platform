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

* **Fase:** v0.1 — Foundation (concluída) → transição para v0.2 — Core.
* **Repositório:** público, em `github.com/VenancioMarcos/vena-ia-platform`.
* **Arquitetura:** Modular Monolith (`docs/adr/ADR-001.md`), com organização em `apps/`, `packages/`, `services/`.
* **Backend:** scaffold FastAPI criado (`apps/api`), sem persistência real implementada.
* **Frontend:** scaffold Next.js criado (`apps/web`), sem telas funcionais além do console técnico inicial.
* **Infraestrutura:** `docker-compose.yml` validado (postgres+pgvector, redis, minio); ambiente ainda não foi executado ponta a ponta.
* **Governança documental:** Foundation Pack v1.0 (este conjunto de documentos) formaliza como múltiplas IAs colaboram no repositório.

---

## 4. O que NÃO está implementado ainda

* Autenticação e autorização.
* Persistência real (migrations, modelos de banco).
* Upload de arquivos.
* Chat com IA / integração OpenAI.
* RAG e busca semântica.
* Qualquer módulo de CAD, CAM, CNC ou simulação.
* CI/CD funcional além dos workflows placeholder.

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
