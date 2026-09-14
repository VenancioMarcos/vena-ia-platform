# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-294 a AUTO-303
**Estado:** CNC_SPINDLE_POWER_TORQUE_ENVELOPE_AUDITOR_COMPLETED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v8.3-cnc-power-torque-envelope-auditor`
**Baseline da branch:** `35b867f4833574fa4355aad08b2ade17f56c1043`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O CTO aprovou explicitamente o `VTP-AUTO-293-BATCH`. A Rota 22 implementa o serviço
determinístico de curva do fuso, integra o contrato v2 ao manifesto e laudo textual
e apresenta RPM, potência, torque e margem de reserva no viewer Web. Curva, fontes,
interpolação, margens e status são revalidados fail-closed, sem autoridade física.

## Continuidade

Publicar a branch, abrir o PR #70, acompanhar CI, promover para review e integrar por
squash. Depois iniciar a Rota 23 e emitir `VTP-AUTO-303-BATCH` sem push.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
