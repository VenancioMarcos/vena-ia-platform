# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-334 a AUTO-338
**Estado:** CNC_COOLANT_PRESSURE_FLOW_WEB_HUD_COMPLETED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v8.8-cnc-coolant-web-hud`
**Baseline da branch:** `979ed4e913495d0e0173027f35d6e29735050a01`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O PR #74 publicou o contrato da Rota 26, recebeu Backend CI verde em 3m42s e foi
integrado por squash em `979ed4e`, com remoção da branch remota e sincronização
da main. A integração JSON/TEXT/Web agora mostra o modo Flood/MQL, vazão,
pressão, margens e requisitos por zona, com estados visuais adequado/insuficiente
e sem qualquer controle de bomba, válvula ou máquina.

## Continuidade

Emitir `VTP-AUTO-338-BATCH` e aguardar parecer. A branch permanece local sem
push.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
