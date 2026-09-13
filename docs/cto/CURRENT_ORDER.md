# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-101 a AUTO-105
**Estado:** CNC_ROTA_3_CONTROLLER_DIALECTS_COMPLETED_LOCAL
**Data:** 2026-09-13
**Branch:** `codex/v5.2-cnc-controller-dialects`
**Baseline da branch:** `9036a48053981f592526eeec2263939155237c92`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

O pós-processador revisável seleciona dialetos determinísticos para `FANUC_0I`,
`SIEMENS_840D` e `HAAS`. Limites configurados de rotação e avanço falham fechados;
o gateway autenticado propaga ferramenta e limites sem conceder autoridade física.

## Continuidade

A Rota 2 foi integrada pelo PR #44 em `9036a48`. A Rota 3 está consolidada
localmente, sem push, e aguarda parecer do CTO.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
