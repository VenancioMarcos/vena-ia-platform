# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-048
**Estado:** ROTA_2_STAGE_2_ASYNC_DISPATCH_IN_PROGRESS
**Data:** 2026-09-12
**Branch:** `codex/v3.2-step-async-dispatch`
**Baseline:** `2d3da5d3b147939eb66572a79d901e2ae4f185a6` (merge do PR #32)
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

A Etapa 1 da Rota 2 foi integrada pelo proprietário no merge `2d3da5d`. A Etapa 2
implementa somente o serviço cliente tipado para despacho assíncrono STEP, com
timeout, tratamento defensivo e transporte injetável. Nenhum endpoint de backend,
interface, geração NC ou autoridade física integra esta missão.

## Continuidade

Validar as suítes web e Python, TypeScript, lint, Ruff e diff; criar o commit local
autorizado, enviar VTP-AUTO-048 ao CTO e aguardar a próxima ordem sem encerrar o
fluxo. Não realizar push.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.
