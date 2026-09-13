# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-116 a AUTO-120
**Estado:** SIM_ROTA_2_CANVAS_TOOLPATH_VIEWER_COMPLETED_LOCAL
**Data:** 2026-09-13
**Branch:** `codex/v6.1-sim-canvas-toolpath-viewer`
**Baseline da branch:** `36c21e7e76639c85b60524233128a85c3cc1a0d6`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

O componente Canvas consome o payload de simulação tipado e desenha stock, zona
de exclusão, eixos e trajetórias G00/G01. Controles locais permitem reprodução,
pausa e scrub mantendo o aviso de auditoria e bloqueio físico sempre visível.

## Continuidade

A Rota SIM 1 foi integrada pelo PR #47 em `36c21e7`. A Rota SIM 2 está consolidada
localmente, sem push, e aguarda parecer do CTO.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
