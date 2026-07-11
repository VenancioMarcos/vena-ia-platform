# Vena_IA Platform — Guia Completo de Navegação para Todas as IAs

**Última atualização:** 2026-07-11  
**Status:** Documento de referência central  
**Público:** Qualquer agente de IA trabalhando neste projeto

---

## 📍 COMECE AQUI — Leitura Obrigatória (Antes de Qualquer Coisa)

Todo agente de IA que começa a trabalhar neste projeto **deve ler nesta ordem**:

| # | Documento | Objetivo | Tempo |
|---|---|---|---|
| 1 | [`CONTEXT.md`](CONTEXT.md) | Entender o estado **real** do projeto agora | 5 min |
| 2 | [`PROJECT.md`](PROJECT.md) | Documento mestre — a visão completa | 10 min |
| 3 | [`GOVERNANCE.md`](GOVERNANCE.md) | Regras, limites, como trabalhar | 8 min |
| 4 | [`AGENTS.md`](AGENTS.md) | Papéis, responsabilidades, regras obrigatórias | 8 min |
| 5 | [`.ai/ACP.md`](.ai/ACP.md) | Protocolo técnico de trabalho entre IAs | 5 min |

**Total:** ~36 minutos. Vale a pena fazer uma única vez para economizar retrabalho depois.

---

## 🗺️ MAPA DO PROJETO — Visão Geral

```
Vena_IA Platform
├── v0.1 Foundation ✅ (concluído)
├── v0.2 Core ✅ (concluído — em validação)
├── v0.3 IA Base ⏳ (próximo)
├── v0.4 Upload e Base de Conhecimento
├── v0.5 RAG
├── v0.6 CAD Inicial
├── v0.7 Engenharia e CAM Inicial
├── v0.8 CNC Inicial
├── v0.9 Pesquisa Científica
└── v1.0 MVP Vena_IA (final deste estágio)
```

**Estado atual:** v0.2 concluída localmente, publicada no GitHub. v0.3 pronta para começar.

---

## 📚 DOCUMENTAÇÃO OFICIAL (Fonte de Verdade)

Estes documentos **nunca mudam de lugar** — qualquer IA pode contar com eles estar aqui:

### Documentação Fundacional
- **[`PROJECT.md`](PROJECT.md)** — Mestre absoluto. Identidade, missão, objetivos, stack, módulos, roadmap, padrões de desenvolvimento.
- **[`CONTEXT.md`](CONTEXT.md)** — Estado atual (o que existe de verdade vs. planejado). **Leia antes de qualquer implementação.**
- **[`ARCHITECTURE.md`](ARCHITECTURE.md)** — Arquitetura técnica, fluxos, stack detalhado, organização do repositório.

### Governança e Colaboração
- **[`GOVERNANCE.md`](GOVERNANCE.md)** — Regras: segurança, IP, processo de decisão, versionamento, padrão de commits.
- **[`AGENTS.md`](AGENTS.md)** — Papéis de IAs, responsabilidades, limites de autonomia, fluxo de trabalho.
- **[`.ai/ACP.md`](.ai/ACP.md)** — Protocolo técnico: ciclo de trabalho, formato de entrega, resolução de conflitos.
- **[`.ai/ROLES.md`](.ai/ROLES.md)** — Matriz: tipo de tarefa → papel responsável.
- **[`.ai/PROMPT_TEMPLATE.md`](.ai/PROMPT_TEMPLATE.md)** — Como estruturar uma missão para IA.
- **[`.ai/CONTEXT_TEMPLATE.md`](.ai/CONTEXT_TEMPLATE.md)** — Como passar contexto de uma IA para outra.

### Decisões e Histórico
- **[`docs/DECISIONS.md`](docs/DECISIONS.md)** — Registro vivo: decisões operacionais pequenas, status (`Proposta`, `Aprovada`, `Em revisão`).
- **[`docs/adr/`](docs/adr/)** — Architecture Decision Records: decisões grandes, arquiteturais, de longo prazo. **[Índice de ADRs](docs/adr/README.md)**.
- **[`CHANGELOG.md`](CHANGELOG.md)** — Histórico de versões (o que mudou em cada release).

### Planos e Roadmap
- **[`ROADMAP.md`](ROADMAP.md)** — Resumo executivo (na raiz).
- **[`docs/ROADMAP.md`](docs/ROADMAP.md)** — Roadmap completo: versões, fases operacionais, marcos, riscos.

### Qualidade e Contribuição
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — Como contribuir: branches, commits, code review, checklist de PR.
- **[`SECURITY.md`](SECURITY.md)** — O que **nunca** publicar (segredos, credenciais, dados sensíveis).

---

## 🎯 GUIAS POR FASE/VERSÃO

Leia o escopo de cada versão **antes de começar a implementar**:

### v0.1 — Foundation ✅
**Status:** Concluída  
**O que foi feito:** Documentação, governança, estrutura de repositório, Foundation Pack v1.0  
**Referência:** [`docs/ROADMAP.md` → v0.1](docs/ROADMAP.md) (procure pela seção)  
**Decisões registradas:** [`docs/DECISIONS.md`](docs/DECISIONS.md) (DEC-001 a DEC-009)

---

### v0.2 — Core ✅
**Status:** Concluída, em validação local  
**O que foi feito:**
- Persistência real (SQLAlchemy, Alembic)
- 5 tabelas (users, projects, files, chats, messages)
- Fluxo CRUD completo (criar usuário → criar projeto → criar arquivo → enviar mensagem)
- Dashboard mínimo
- 12 testes automatizados

**Referência:** [`docs/ROADMAP.md` → v0.2](docs/ROADMAP.md)  
**Decisão registrada:** [`docs/DECISIONS.md` → DEC-011](docs/DECISIONS.md)  
**Localização no código:**
- Models: `apps/api/app/modules/*/models.py`
- Migrations: `apps/api/alembic/versions/`
- Dashboard: `apps/web/app/dashboard/page.tsx`

---

### v0.3 — IA Base ⏳ **← PRÓXIMA**
**Status:** Pronto para começar  
**O que precisa ser feito:**
1. Integração com OpenAI API (criar chat técnico)
2. Histórico de conversas persistindo
3. Prompts base documentados
4. Testes automatizados

**Referência:** [`docs/ROADMAP.md` → v0.3](docs/ROADMAP.md)  
**Stack:** Python 3.13+, FastAPI, OpenAI API  
**Decisões relevantes:**
- [`docs/DECISIONS.md` → DEC-005`](docs/DECISIONS.md) (stack oficial)
- [`docs/adr/ADR-0006`](docs/adr/ADR-0006-ai-first-development.md) (desenvolvimento AI-first)

**Como receber essa tarefa:**
Use [`.ai/PROMPT_TEMPLATE.md`](.ai/PROMPT_TEMPLATE.md) para estruturar a missão. Exemplo:

```markdown
# MISSÃO DE IMPLEMENTAÇÃO

## Projeto
Vena_IA Platform

## Papel
AI/RAG Engineer (conforme AGENTS.md → Seção 2.5)

## Contexto
- Leia: CONTEXT.md → Seção 3 (Estado Atual)
- Leia: docs/ROADMAP.md → v0.3 — IA Base
- Leia: GOVERNANCE.md → Seção 8 (Padrão de Commits)
- Leia: docs/DECISIONS.md → DEC-005 (stack oficial)

## Objetivo
Implementar v0.3 — IA Base

## Escopo
[copiar de docs/ROADMAP.md → v0.3]

## Tarefas
1. Criar integração com OpenAI API
2. Implementar chat técnico com histórico persistente
3. Documentar prompts base
4. Criar testes automatizados
5. Registrar decisões novas em docs/DECISIONS.md (se houver)

## Regras Obrigatórias
- Seguir Conventional Commits (GOVERNANCE.md → Seção 9)
- Toda decisão nova → DEC-0XX em DECISIONS.md
- Código novo → testes automatizados (PROJECT.md → Seção 16)
- Sem API keys ou segredos versionados (SECURITY.md)
```

---

### v0.4 a v1.0 — Próximas Fases
**Referência:** [`docs/ROADMAP.md`](docs/ROADMAP.md) (procure pelas seções correspondentes)

Cada fase terá seu próprio escopo detalhado quando for hora de começar.

---

## 🔍 COMO UMA IA DESCOBRE "ONDE PAROU"

**Situação:** Uma IA está pronta para continuar, mas não sabe exatamente em que ponto está o projeto.

**Solução:** Siga este protocolo (`.ai/ACP.md` → Ciclo de Trabalho):

1. **Abra `CONTEXT.md`** → Seção 3 ("Estado Atual")
   - Ali está escrito: o que foi implementado, o que está em testes, o que ainda é só planejamento.
   - Exemplo: "v0.2 concluída, em validação com Docker. v0.3 pronta para começar."

2. **Leia o escopo da fase que vai fazer** (ex.: v0.3)
   - Arquivo: `docs/ROADMAP.md` → procure `## v0.3 — IA Base`
   - Lá tem: Objetivo, Entregas, Critério de Conclusão.

3. **Procure decisões já tomadas** que afetem sua tarefa
   - Arquivo: `docs/DECISIONS.md`
   - Exemplo: se você vai mexer com OpenAI, veja `DEC-005` (stack oficial) e `DEC-009` (segurança).

4. **Execute sua tarefa** respeitando as regras de `GOVERNANCE.md` e `AGENTS.md`

5. **Ao terminar**, atualize `CONTEXT.md` com o novo estado e registre sua decisão em `docs/DECISIONS.md`

---

## 📋 CHECKLIST — O Que Fazer Agora

**Se você é o Marcos (humano):**
- [ ] Leia `CONTEXT.md` para saber o estado real
- [ ] Leia `docs/ROADMAP.md` → v0.3 para ver o escopo exato
- [ ] Escolha qual IA vai fazer a v0.3 (Claude, ChatGPT, Codex etc.)
- [ ] Use [`.ai/PROMPT_TEMPLATE.md`](.ai/PROMPT_TEMPLATE.md) para estruturar a missão
- [ ] Cole a missão na IA escolhida, apontando para este arquivo (`PROJECT_ROADMAP_FULL.md`)

**Se você é uma IA recebendo uma tarefa (v0.3 ou qualquer outra):**
- [ ] Leia `CONTEXT.md` (estado atual)
- [ ] Leia `PROJECT.md` (visão geral)
- [ ] Leia `GOVERNANCE.md` (regras)
- [ ] Leia `AGENTS.md` (papéis e limites)
- [ ] Leia [`.ai/ACP.md`](.ai/ACP.md) (protocolo de trabalho)
- [ ] Leia o escopo da versão que vai implementar (em `docs/ROADMAP.md`)
- [ ] Leia `docs/DECISIONS.md` (decisões já tomadas)
- [ ] Implemente seguindo `CONTRIBUTING.md` (commits, PRs, documentação)
- [ ] Atualize `CONTEXT.md` e registre decisões novas quando terminar

---

## 🔗 LINKS RÁPIDOS

### Ler Agora (Qualquer IA)
- [`CONTEXT.md`](CONTEXT.md) — Estado atual do projeto
- [`PROJECT.md`](PROJECT.md) — Mestre, identidade e visão
- [`GOVERNANCE.md`](GOVERNANCE.md) — Regras e limites

### Executar Agora (v0.3)
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — Procure v0.3 — IA Base
- [`.ai/PROMPT_TEMPLATE.md`](.ai/PROMPT_TEMPLATE.md) — Como estruturar a missão

### Referência Constante
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — Padrão de commits, PRs, código
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — Todas as decisões tomadas
- [`docs/adr/README.md`](docs/adr/README.md) — Índice de ADRs

### Navegação
- [`ROADMAP.md`](ROADMAP.md) — Resumo das versões
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — Versão completa, detalhada
- [`CHANGELOG.md`](CHANGELOG.md) — Histórico de releases

---

## 📞 Perguntas Frequentes de IAs

**P: "Onde está o código da v0.2?"**  
R: Em `apps/api/app/modules/*/` (models, schemas, rotas) e `apps/api/alembic/` (migrations).

**P: "Qual é exatamente o escopo da v0.3?"**  
R: `docs/ROADMAP.md` → procure `## v0.3 — IA Base`.

**P: "Posso mexer em autenticação?"**  
R: Não. Fase 6. Ver `docs/ROADMAP.md` → Fase 3.

**P: "Encontrei um bug. Posso consertar?"**  
R: Sim. Registre em `docs/DECISIONS.md` como `DEC-00X`, tipo `Backend / Qualidade`, status `Aprovada`.

**P: "Preciso mudar a stack de banco de dados?"**  
R: Não sem ADR. Registre em `docs/adr/ADR-00XX.md` antes de executar. Ver `GOVERNANCE.md` → Seção 6.

**P: "Como deixo contexto para a próxima IA?"**  
R: Use [`.ai/CONTEXT_TEMPLATE.md`](.ai/CONTEXT_TEMPLATE.md) e atualize `CONTEXT.md`.

---

## 🎯 Próximo Passo (Resumido)

1. **Marcos (humano):** Leia `CONTEXT.md` e `docs/ROADMAP.md` → v0.3.
2. **Marcos:** Use [`.ai/PROMPT_TEMPLATE.md`](.ai/PROMPT_TEMPLATE.md) para estruturar a missão da v0.3.
3. **Marcos:** Cole a missão no Claude, ChatGPT, ou qualquer IA escolhida.
4. **IA recebida:** Leia os 5 documentos obrigatórios (CONTEXT → PROJECT → GOVERNANCE → AGENTS → ACP).
5. **IA:** Implemente v0.3, seguindo CONTRIBUTING.md.
6. **IA:** Ao terminar, atualize CONTEXT.md e registre decisões em docs/DECISIONS.md.
7. **Marcos:** Aplique o código no seu repositório local.
8. **Marcos:** Começa v0.4 (repita o ciclo).

---

**Versão:** 1.0  
**Criado:** 2026-07-11  
**Responsável:** Claude (Documentation Engineer)  
**Próxima revisão:** Após v0.3 concluída

