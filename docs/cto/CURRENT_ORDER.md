# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-111 a AUTO-115
**Estado:** SIM_ROTA_1_TOOLPATH_VISUALIZER_FOUNDATION_COMPLETED_LOCAL
**Data:** 2026-09-13
**Branch:** `codex/v6.0-sim-toolpath-visualizer-foundation`
**Baseline da branch:** `d60cb88e53a1064d123fca4adcdd3e66ebadc956`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

O endpoint autenticado de simulação aceita um programa ISO limitado ou um plano
CAM pertencente ao usuário. O parser valida primeiro o envelope e transforma G0/G1
em segmentos X/Z com movimento, avanço e ferramenta para renderização 2D segura.

## Continuidade

A Rota 4 foi integrada pelo PR #46 em `d60cb88`, fechando o Épico CNC. A Rota SIM
1 está consolidada localmente, sem push, e aguarda parecer do CTO.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
