# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-294 a AUTO-303
**Estado:** CNC_THERMAL_EXPANSION_DRIFT_CONTRACT_V2_SCAFFOLDED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v8.4-cnc-thermal-expansion-drift-auditor`
**Baseline da branch:** `eae463ee990b66c70c874e21a4cba9f7c36c01e9`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O CTO aprovou explicitamente o `VTP-AUTO-293-BATCH`. O PR #70 publicou a Rota 22,
teve os dois CIs aprovados e foi integrado por squash em `eae463e`; a branch remota
foi removida e a main foi sincronizada. A Rota 23 iniciou o contrato Pydantic v2 de
expansão térmica do tarugo e deriva do fuso nos eixos X/Z, com coeficientes tabulados,
valores derivados revalidados e warning por tolerância.

## Continuidade

Emitir `VTP-AUTO-303-BATCH` ao CTO e aguardar parecer e próxima ordem. A branch da
Rota 23 permanece local e não deve receber push nesta etapa.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
