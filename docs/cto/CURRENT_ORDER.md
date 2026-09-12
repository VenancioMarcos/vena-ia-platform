# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-049
**Estado:** ROTA_2_UI_ASYNC_DISPATCH_INTEGRATION_IN_PROGRESS
**Data:** 2026-09-12
**Branch:** `codex/v3.2-step-async-dispatch`
**Baseline:** `2d3da5d3b147939eb66572a79d901e2ae4f185a6` (merge do PR #32)
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

A Etapa 2 integra o serviço cliente tipado ao card STEP e à rota `/cam/turning`,
com estados visuais, polling limitado e cancelamento explícito. Nenhum endpoint de
backend, geração NC ou autoridade física integra esta missão.

## Continuidade

Validar as suítes web e Python, TypeScript, lint, Ruff e diff; criar o commit local
autorizado, enviar VTP-AUTO-049 ao CTO e aguardar a próxima ordem sem encerrar o
fluxo. Não realizar push.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.
