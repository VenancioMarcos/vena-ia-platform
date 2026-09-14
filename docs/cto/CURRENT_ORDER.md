# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-289 a AUTO-293
**Estado:** CNC_POWER_TORQUE_ENVELOPE_CONTRACT_V2_SCAFFOLDED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v8.3-cnc-power-torque-envelope-auditor`
**Baseline da branch:** `35b867f4833574fa4355aad08b2ade17f56c1043`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O CTO aprovou explicitamente o `VTP-AUTO-288-BATCH`. O PR #69 publicou a Rota 21,
teve Backend e Frontend CI aprovados e foi integrado por squash em `35b867f`; sua
branch remota foi removida e `main=origin/main`. A Rota 22 iniciou o contrato
Pydantic v2 para conferir curvas declaradas de torque/potência por RPM. Pontos de
curva e operação revalidam a identidade entre potência, torque e rotação, margens,
interpolação, faixa e vínculo ao snapshot Kienzle, sempre fail-closed.

## Continuidade

Emitir `VTP-AUTO-293-BATCH` ao CTO e aguardar parecer e próxima ordem. A branch
permanece local e não deve receber push nesta etapa.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
