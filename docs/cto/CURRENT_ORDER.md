# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-146 a AUTO-150
**Estado:** CNC_ROUTE_5_PR_OPEN_AWAITING_CI_AND_REVIEW
**Data:** 2026-09-13
**Branch:** `codex/v6.6-cnc-gcode-syntax-linter`
**Baseline da branch:** `dd950938bf3e7bdb2a7447647964c8542b69b26c`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

O PR #52 integrou o hardening CAD em `dd950938` após Backend CI aprovado. A Rota 5
CNC acrescenta auditor estático de sintaxe por dialeto, sem executar, transmitir ou
liberar programas para máquina. A entrega será publicada como Draft PR #53 e só
seguirá para revisão após CI remoto aprovado.

## Continuidade

A rota está pronta para publicação upstream; nenhum merge é autorizado antes da
confirmação explícita dos checks remotos.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
