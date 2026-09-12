# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-053
**Estado:** ROTA_3_BACKEND_GATEWAY_IN_PROGRESS
**Data:** 2026-09-12
**Branch:** `codex/v3.3-cad-backend-gateway`
**Baseline:** `75b96080ee9bf1201c2ffda2f70bf9b3e172963c` (merge do PR #33)
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

A Rota 3 abre um gateway autenticado de ingestão STEP em
`POST /api/v1/cad/step/dispatch`. O serviço valida extensão, assinatura e limite
de 15 MB antes de persistir em sandbox temporário, cria um job `QUEUED` isolado
por proprietário e expõe consulta de status. Nenhum processamento geométrico,
geração NC ou autoridade física integra esta etapa.

## Continuidade

Concluir as validações local e regressiva, criar o commit local autorizado,
enviar VTP-AUTO-053 ao CTO e aguardar a próxima ordem sem encerrar o fluxo.
Nenhum push foi autorizado.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.
