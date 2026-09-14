# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-324 a AUTO-333
**Estado:** CNC_COOLANT_PRESSURE_FLOW_CONTRACT_V2_SCAFFOLDED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v8.7-cnc-coolant-pressure-flow-auditor`
**Baseline da branch:** `abbbcad44964553aa474760910b7afc551e1da88`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O PR #73 publicou a Rota 25, recebeu CI integral verde e foi integrado por
squash em `abbbcad`, com remoção da branch remota e sincronização da main.
A Rota 26 iniciou o contrato v2 de demanda de fluido Flood/MQL, vazão e pressão
mínimas por zona e alerta de dissipação térmica insuficiente.

## Continuidade

Emitir `VTP-AUTO-333-BATCH` e aguardar parecer. A branch permanece local sem
push.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
