# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-269 a AUTO-278
**Estado:** CNC_RESIDUAL_STOCK_AUDITOR_COMPLETED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v8.1-cnc-residual-stock-auditor`
**Baseline da branch:** `70515987d1b19758d549e8a6ff188dfa81116188`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O CTO aprovou explicitamente o `VTP-AUTO-268-BATCH`. O PR #67 publicou a Rota 19,
teve Backend e Frontend CI aprovados e foi integrado por squash em `7051598`; sua
branch remota foi removida e `main=origin/main`. A Rota 20 preserva e vincula o
perfil BRep nominal, calcula sobremetal residual por seção axial, acusa gouging,
excesso de material e degraus incompatíveis com a ferramenta. O contrato, o laudo
TEXT e o painel Web revalidam as fontes e mantêm revisão física CMM obrigatória.

## Continuidade

Emitir `VTP-AUTO-278-BATCH` ao CTO e aguardar parecer e próxima ordem. A branch
permanece local e não deve receber push nesta etapa.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
