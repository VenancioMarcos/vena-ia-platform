# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-096 a AUTO-100
**Estado:** CNC_ROTA_2_E2E_GATEWAY_COMPLETED_LOCAL
**Data:** 2026-09-13
**Branch:** `codex/v5.1-cnc-e2e-gateway`
**Baseline da branch:** `136941809c1acf481f7f7c476664a15009476553`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

O endpoint autenticado `POST /api/v1/cnc/turning/generate` recupera somente planos
CAM pertencentes ao usuário, normaliza o contrato revisável e invoca o formatador
ISO determinístico. A resposta permanece `PLANNED_REQUIRES_REVIEW`, auditável e
não executável.

## Continuidade

O gateway está consolidado localmente e aguarda parecer do CTO. A Rota 1 foi
integrada pelo PR #43 em `1369418`; a branch da Rota 2 não foi publicada.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
