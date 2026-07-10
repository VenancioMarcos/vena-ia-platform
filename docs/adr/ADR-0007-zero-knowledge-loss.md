# ADR-0007 — Política de Zero Perda de Conhecimento

**Status:** Aprovado
**Data:** 2026-07-10
**Responsável:** Documentation Engineer / Repository Architect

---

## Contexto

Sessões de trabalho com agentes de IA são, por natureza, efêmeras: o contexto de uma conversa não persiste automaticamente para a próxima sessão, nem entre diferentes modelos.

## Problema

Sem um mecanismo ativo de preservação de conhecimento, decisões, justificativas e trade-offs discutidos em uma sessão podem se perder completamente ao final dela, forçando retrabalho ou, pior, decisões inconsistentes ao longo do tempo.

## Alternativas Consideradas

1. **Confiar na memória de longo prazo de cada ferramenta de IA** — rejeitada: memória de produto (quando existe) é específica de cada ferramenta, não é portável entre ChatGPT, Claude, Codex, Gemini etc., e não é uma fonte auditável.
2. **Resumos manuais esporádicos** — rejeitada: depende de disciplina humana constante e tende a ficar desatualizada.
3. **Política formal de Zero Knowledge Loss**: toda sessão relevante termina com atualização de `CONTEXT.md` e, quando aplicável, um handoff via `.ai/CONTEXT_TEMPLATE.md` — **Escolhida**.

## Decisão

Estabelecer como princípio de engenharia que nenhuma decisão, justificativa ou estado relevante do projeto pode existir *apenas* na memória de uma sessão de IA. Todo agente é responsável por externalizar esse conhecimento para o repositório antes de encerrar seu trabalho.

## Consequências

* Reduz a zero (ou próximo disso) a dependência de memória de sessão de qualquer ferramenta específica.
* Adiciona uma etapa final obrigatória a cada sessão relevante de trabalho.
* Torna o projeto resiliente a troca de ferramenta de IA (migrar de um assistente para outro não implica perda de contexto).
