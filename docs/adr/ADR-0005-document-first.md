# ADR-0005 — Adoção do Princípio Document-First

**Status:** Aprovado
**Data:** 2026-07-10
**Responsável:** Documentation Engineer / Repository Architect

---

## Contexto

O projeto tem escopo amplo (software, IA, engenharia mecânica, pesquisa científica) e é construído por múltiplos agentes que não compartilham memória entre si.

## Problema

Implementar código antes de documentar decisões gera dois riscos: (1) agentes futuros reconstroem a lógica por engenharia reversa do código, perdendo o "porquê"; (2) decisões implícitas no código nunca são revisadas ou contestadas formalmente.

## Alternativas Consideradas

1. **Code-first, documentar depois "quando der tempo"** — rejeitada: na prática, a documentação nunca alcança o código, especialmente em projeto multi-IA.
2. **Documentar em paralelo, sem ordem definida** — rejeitada: permite implementações que contradizem decisões ainda não escritas.
3. **Document-first: decisões relevantes são documentadas antes ou junto da implementação, nunca depois** — **Escolhida**, já praticado desde `PROJECT.md`, Seção 19 e 20.

## Decisão

Nenhuma implementação de código relevante deve ocorrer sem que a decisão correspondente esteja documentada (ADR, `DECISIONS.md`, ou especificação de feature). Documentação é tratada como parte da arquitetura, não como tarefa acessória.

## Consequências

* Aumenta o tempo até a primeira linha de código de uma feature, mas reduz retrabalho e perda de contexto.
* Facilita auditoria e revisão por humanos e por outras IAs.
* Exige disciplina de todo agente para não pular a etapa documental sob pressão de entrega rápida.
