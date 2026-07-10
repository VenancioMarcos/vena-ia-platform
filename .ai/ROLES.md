# ROLES.md — Matriz de Responsabilidades por Tipo de Tarefa

**Status:** Especificação Oficial
**Versão:** 1.0
**Documento relacionado:** `AGENTS.md`, `.ai/ACP.md`

---

## 1. Objetivo

Mapear tipos de tarefa para papéis esperados, evitando que um agente assuma responsabilidade fora do seu escopo (ex.: um agente de documentação implementando backend, ou um agente de backend redefinindo arquitetura sem ADR).

---

## 2. Matriz

| Tipo de Tarefa | Papel Responsável | Documento Base | Pode implementar código? |
|---|---|---|---|
| Documentação institucional (README, GOVERNANCE, AGENTS) | Documentation Engineer | `GOVERNANCE.md` | Não |
| Registro de decisão arquitetural | Líder Técnico / Arquiteto | `docs/adr/` | Não |
| Estrutura de repositório | Repository Architect | `ARCHITECTURE.md` | Apenas estrutura, sem lógica |
| Endpoints e regras de negócio (`apps/api`) | Backend Engineer | `ARCHITECTURE.md` | Sim |
| Telas e componentes (`apps/web`) | Frontend Engineer | `ARCHITECTURE.md` | Sim |
| Pipeline de IA / RAG (`packages/ai`, `services/rag`) | AI/RAG Engineer | `ARCHITECTURE.md`, `SECURITY.md` | Sim |
| Parsers de arquivos técnicos (`services/parser-*`) | Backend Engineer / Pesquisador Técnico | `docs/ROADMAP.md` (v0.6+) | Sim |
| Infraestrutura local (`docker-compose.yml`) | Backend Engineer | `docker-compose.yml` | Sim (config, não app) |
| Revisão de Pull Request | Revisor de Código / QA | `CONTRIBUTING.md` | Não (apenas revisão) |
| Pesquisa científica e metodologia | Pesquisador Técnico | `docs/research/` | Não |
| Automação de negócio (leads, WhatsApp, n8n) | Automation Engineer | Fora deste repositório (ecossistema Vena_IA) | Sim, em repositório próprio |

---

## 3. Regra de Escalada

Se uma tarefa não se encaixa claramente em uma linha desta matriz, o agente deve:

1. Tratar a tarefa como fora de escopo padrão.
2. Propor explicitamente ao responsável humano qual papel deveria assumi-la, antes de executar.

## 4. Atualização desta Matriz

Alterações nesta matriz não exigem ADR, mas devem ser registradas em `docs/DECISIONS.md` como decisão do tipo `Operação`.
