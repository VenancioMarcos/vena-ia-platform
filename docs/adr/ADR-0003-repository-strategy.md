# ADR-0003 — Estratégia de Repositório como Fonte Única de Verdade

**Status:** Aprovado
**Data:** 2026-07-10
**Responsável:** Documentation Engineer / Repository Architect

---

## Contexto

Decisões técnicas e de produto do Vena_IA vinham sendo discutidas em múltiplas conversas com diferentes IAs, sem um local único e versionado que consolidasse o estado real do projeto.

## Problema

Sem uma fonte única de verdade, decisões se perdem, se contradizem entre sessões, e novos agentes (ou o próprio responsável humano) não conseguem reconstruir com confiança "o que já foi decidido" versus "o que foi apenas discutido".

## Alternativas Consideradas

1. **Manter decisões em conversas/chats** — rejeitada: não é pesquisável, não é versionado, depende de memória de plataformas de terceiros.
2. **Documento único gigante** — rejeitada: dificulta colaboração paralela e revisão granular via Pull Request.
3. **Repositório Git como fonte única de verdade, com documentação estruturada (ADRs, DECISIONS.md, CONTEXT.md)** — **Escolhida.**

## Decisão

O repositório Git (`github.com/VenancioMarcos/vena-ia-platform`) é declarado a única fonte oficial da verdade do projeto. Nenhuma decisão relevante é válida enquanto não estiver versionada.

## Consequências

* Toda decisão relevante deve gerar um commit (ADR, entrada em `DECISIONS.md`, ou atualização de `CONTEXT.md`).
* Conversas com IAs passam a ser consideradas rascunho até serem formalizadas no repositório.
* Aumenta a disciplina exigida de humanos e agentes, mas reduz drasticamente o risco de perda de conhecimento entre sessões.
