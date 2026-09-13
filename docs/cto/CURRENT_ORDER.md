# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-106 a AUTO-110
**Estado:** CNC_ROTA_4_KINEMATIC_ENVELOPE_VALIDATOR_COMPLETED_LOCAL
**Data:** 2026-09-13
**Branch:** `codex/v5.3-cnc-kinematic-envelope-validator`
**Baseline da branch:** `27c48affd7091dd05d4e6cdd67b7b7ab098c8d00`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

O formatador exige um envelope X-diâmetro/Z explícito e valida todos os pontos e
segmentos G0/G1 contra os cursos configurados e a zona retangular da placa.
Movimentos incompletos, fora do curso ou em colisão falham fechados antes da resposta.

## Continuidade

A Rota 3 foi integrada pelo PR #45 em `27c48af`. A Rota 4 está consolidada
localmente, sem push, e aguarda parecer do CTO.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
