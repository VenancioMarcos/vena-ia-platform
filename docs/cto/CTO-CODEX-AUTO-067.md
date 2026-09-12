# CTO-CODEX-AUTO-067 — Publicação da Rota 5 Etapa 2

**Status:** `ROTA_5_STAGE_2_STRESS_PR_OPEN_AWAITING_CI_AND_REVIEW`
**Data:** 2026-09-12
**Branch:** `codex/v3.5-cad-e2e-stress-tests`
**Commit de testes:** `c955aa7175ff4e64265324d727df1bb25f6736ae`

## Objetivo

Consolidar a AUTO-066, publicar a branch dedicada, abrir o PR contra `main` e
coletar o CI. Nenhum merge está autorizado nesta missão.

## Entrega consolidada

- Quatro uploads STEP concorrentes com proprietários distintos, `job_id` únicos,
  extração completa, isolamento de leitura e limpeza determinística.
- Upload exato de 15 MiB com blocos adicionais de entidades STEP, contrato
  revisável e sandbox limpo.
- 740 testes Python, 9 ignorados, 64 Web, TypeScript, lint, Ruff, mypy e diff
  aprovados.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.

## Continuidade

Enviar VTP-AUTO-067 ao CTO, solicitar parecer e aguardar a próxima ordem sem
encerrar a execução.
