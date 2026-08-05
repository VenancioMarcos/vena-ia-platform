# ADR-0025 — Reconciliação durável e gate de OCR

**Status:** Aprovada
**Data:** 2026-08-05
**Decisão relacionada:** DEC-026
**Riscos relacionados:** R-016, R-017, R-033, R-038

## Contexto

O Package 1 recuperava o lease no Redis, mas um job persistido como `RUNNING`
recusava novo `start` e podia ficar preso. A perda do estado efêmero do Redis
também não era reconstruída automaticamente. OCR continuava sem avaliação formal.

## Decisão

Reconciliar automaticamente o transporte a partir do PostgreSQL no ciclo seguro do
worker, reutilizando a mesma fila, estados e processo do Modular Monolith. Proteger
concorrência com compare-and-set no banco e scripts Lua no Redis. Não criar comando
administrativo, microserviço ou novo tipo de job porque a lacuna é coberta pelo
mecanismo normal de consumo.

Classificar OCR como **B — ADIADO POR RISCO OU AUSÊNCIA DE EVIDÊNCIA**. Um protótipo
futuro exige processo/container descartável sem rede, limites preemptivos de CPU,
memória e tempo, corpus autorizado e revisão humana de qualidade/licença/custo.

## Consequências

Reinício do worker/API/Redis não perde a identidade lógica do job; estados
terminais não regridem e cancelamento sobrevive. Falhas parciais deixam documento
`FAILED` ou `PROCESSING`, nunca `READY`/job `SUCCEEDED` antes da indexação completa.
Timeout dentro de biblioteca síncrona permanece cooperativo (R-038). Nenhum OCR,
GPU, SaaS, dado externo ou dependência de runtime foi adicionado; R-017 permanece
aberto.
