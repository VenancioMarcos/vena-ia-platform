# CONTEXT_TEMPLATE.md — Template de Passagem de Contexto Entre Agentes

**Status:** Especificação Oficial
**Versão:** 1.0
**Documento relacionado:** `.ai/ACP.md`, `CONTEXT.md`

---

## 1. Objetivo

Padronizar como um agente de IA resume o trabalho concluído para o próximo agente (humano ou IA) que continuar o projeto, evitando perda de contexto entre sessões.

Este template complementa — e não substitui — a atualização de `CONTEXT.md`.

---

## 2. Template

```markdown
# HANDOFF — [Nome curto da sessão/tarefa]

## Data
AAAA-MM-DD

## Agente
[Nome do modelo/agente que executou a tarefa]

## O que foi feito
[Resumo objetivo]

## Onde parou
[Estado exato ao final da sessão — o que está pronto e o que está pendente]

## Decisões tomadas nesta sessão
[Referência a ADRs ou entradas em docs/DECISIONS.md criadas]

## Riscos ou pendências conhecidas
[Qualquer limitação, débito técnico ou dependência externa não resolvida]

## Próximo passo recomendado
[O que a próxima sessão/agente deveria fazer primeiro]
```

---

## 3. Quando Usar

* Ao final de qualquer sessão que envolva múltiplas tarefas ou decisões relevantes.
* Sempre que uma tarefa for interrompida antes da conclusão.
* Sempre que houver troca de agente responsável (ex.: de ChatGPT para Claude, de Claude para Codex).

---

## 4. Onde Registrar

O handoff pode ser incluído no corpo do Pull Request correspondente ou, para mudanças de estado geral do projeto, refletido diretamente em `CONTEXT.md`.
