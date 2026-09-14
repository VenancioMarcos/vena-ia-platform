# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-259 a AUTO-268
**Estado:** CNC_OPERATIONAL_PROCESS_ROUTING_SHEET_COMPLETED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v8.0-cnc-process-routing-sheet`
**Baseline da branch:** `b2d897e87248e4d87c6341635826c0c8b8b014a4`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O CTO aprovou explicitamente o `VTP-AUTO-258-BATCH`. O PR #66 publicou a Rota 18,
teve Backend e Frontend CI aprovados e foi integrado por squash em `b2d897e`; sua
branch remota foi removida e `main=origin/main`. A Rota 19 compila uma Folha de
Processo teórica com setup, sequência CAM, ferramenta/inserto, Vc/f/ap, rpm, avanço,
tempos, fixação e balanço. O contrato revalida ordem e snapshots e o relatório JSON,
TEXT e Web mantém revisão humana obrigatória.

## Continuidade

Emitir `VTP-AUTO-268-BATCH` ao CTO e aguardar parecer e próxima ordem. A branch
permanece local e não deve receber push nesta etapa.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
