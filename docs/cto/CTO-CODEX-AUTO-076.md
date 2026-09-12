# CTO-CODEX-AUTO-076 — Publicação da fundação CAM

**Status:** `CAM_ROTA_1_STRATEGY_FOUNDATION_PR_OPEN_AWAITING_CI_AND_REVIEW`
**Data:** 2026-09-12
**Branch:** `codex/v4.0-cam-turning-strategies-foundation`
**Baseline:** `3f2b19877c528cab0d080fcb1bc0756f4bef7390`
**Commit funcional:** `92d3651`

## Objetivo

Consolidar a governança da fundação CAM aprovada, publicar a branch, abrir Draft
PR contra `main` e coletar o estado inicial do CI. Nenhum merge está autorizado.

## Escopo publicado

- Domínio CAM canônico com enums e contratos Pydantic v2 estritos.
- Planejamento determinístico 2D de `FACING` e `ROUGH_TURNING`.
- Nove testes CAM e regressão homologada com 749 Python, 9 ignorados e 64 Web.
- Falha fechada para `FINISHING`, `GROOVING` e entradas inconsistentes.
- Respostas exclusivamente analíticas com `executable_output=false`.

## Critérios de aceitação

- Branch publicada sem push direto em `main`.
- Draft PR aberto contra `main` com o escopo e as salvaguardas documentados.
- Estado inicial das esteiras de CI coletado e reportado no VTP-AUTO-076.

## Limites

`G9=PENDING_AUTHORITATIVE_REVIEW`; `PHYSICAL_USE_AUTHORIZED=FALSE`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.

## Continuidade

Enviar VTP-AUTO-076 ao CTO e aguardar a próxima ordem sem encerrar a execução.
