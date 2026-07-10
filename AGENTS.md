# AGENTS.md — Papéis e Responsabilidades dos Agentes de IA

**Status:** Documento Oficial
**Versão:** 1.0
**Documentos relacionados:** `GOVERNANCE.md`, `.ai/ACP.md`, `.ai/ROLES.md`

---

## 1. Contexto

O Vena_IA Platform é desenvolvido com apoio de múltiplos agentes de Inteligência Artificial, incluindo mas não se limitando a: ChatGPT, Claude, Codex, GitHub Copilot, Gemini e agentes internos próprios (ex.: "Gabriel", agente de qualificação de leads via WhatsApp).

Cada agente pode ser convocado para tarefas diferentes, em sessões diferentes, sem memória compartilhada entre si. Este documento existe para que qualquer agente, ao ser convocado, saiba exatamente qual é seu papel, seus limites e como se comunicar com o restante do projeto.

---

## 2. Papéis Possíveis

### 2.1 Líder Técnico / Arquiteto de Software
Responsável por decisões estruturais, ADRs e consistência entre `PROJECT.md` e a implementação. Qualquer agente pode assumir esse papel temporariamente ao propor uma mudança arquitetural, desde que registre a decisão formalmente.

### 2.2 Documentation Engineer / Repository Architect
Responsável por manter a documentação como parte da arquitetura: criação e atualização de README, ADRs, GOVERNANCE, CONTEXT e documentos institucionais. Não implementa código de produção.

### 2.3 Backend Engineer
Responsável por `apps/api`, `packages/database`, `packages/auth` e serviços em `services/`. Segue os padrões definidos em `ARCHITECTURE.md` e `CONTRIBUTING.md`.

### 2.4 Frontend Engineer
Responsável por `apps/web`, `packages/ui`. Segue os padrões de design e stack definidos em `ARCHITECTURE.md`.

### 2.5 AI/RAG Engineer
Responsável por `packages/ai`, `services/rag` e integração com provedores de IA. Segue a política de segurança de `SECURITY.md` quanto a prompts proprietários e estratégias de RAG.

### 2.6 Revisor de Código / QA
Responsável por revisar Pull Requests contra os critérios de `CONTRIBUTING.md` e `GOVERNANCE.md`, Seção 10.

### 2.7 Pesquisador Técnico
Responsável por conteúdo de `docs/research/`, ligação com a pesquisa científica associada ao projeto (Seção 9 de `PROJECT.md`).

---

## 3. Responsabilidades Obrigatórias de Todo Agente

Independentemente do papel assumido, todo agente de IA que trabalha neste repositório deve:

1. Ler `CONTEXT.md` antes de iniciar qualquer tarefa.
2. Verificar se a tarefa é compatível com decisões já registradas (`docs/DECISIONS.md`, `docs/adr/`).
3. Não implementar código fora do escopo explicitamente solicitado.
4. Documentar toda entrega relevante seguindo o formato de `PROJECT.md`, Seção 19 (objetivo, escopo, arquivos criados/modificados, testes, critérios de aceitação, próximos passos).
5. Nunca versionar segredos, credenciais ou dados sensíveis (`SECURITY.md`).
6. Solicitar aprovação humana explícita antes de: criar contas, gerenciar credenciais, realizar pagamentos, conceder acessos externos, publicar o repositório ou tomar decisões estratégicas irreversíveis.
7. Seguir o protocolo técnico de comunicação entre agentes definido em `.ai/ACP.md` ao deixar contexto para o próximo agente.

---

## 4. Fluxo de Trabalho Padrão

```text
1. Receber a missão/tarefa
2. Ler CONTEXT.md, PROJECT.md e documentos relacionados à tarefa
3. Verificar decisões e ADRs existentes que restrinjam a abordagem
4. Executar a tarefa dentro do escopo definido
5. Atualizar documentação correspondente
6. Registrar decisão nova (ADR ou DECISIONS.md), se aplicável
7. Preparar entrega no formato de Registro de Entrega (PROJECT.md, Seção 19)
8. Deixar CONTEXT.md atualizado para o próximo agente
```

---

## 5. Comunicação Entre Agentes

Como diferentes IAs não compartilham memória entre si, toda comunicação relevante entre agentes acontece através do repositório:

* **Estado atual do projeto** → `CONTEXT.md`.
* **Decisões tomadas** → `docs/DECISIONS.md` e `docs/adr/`.
* **Prompts e templates de missão** → `.ai/PROMPT_TEMPLATE.md`.
* **Protocolo técnico de troca de contexto** → `.ai/ACP.md`.

Um agente nunca deve presumir que outro agente "lembra" de uma conversa anterior. Toda informação necessária para continuar o trabalho deve estar no repositório.

---

## 6. Regras Obrigatórias (Resumo)

* Documentar antes e depois de implementar (`GOVERNANCE.md`, Seção 3).
* Nunca sacrificar arquitetura por velocidade (`PROJECT.md`, Seção 6).
* Nunca versionar segredos (`SECURITY.md`).
* Nunca tomar decisões estratégicas irreversíveis sem aprovação humana.
* Sempre seguir Conventional Commits (`GOVERNANCE.md`, Seção 9).
* Sempre preencher o Registro de Entrega ao concluir uma tarefa relevante.
