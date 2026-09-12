# CTO-CODEX-AUTO-063 — Publicação e abertura de PR da Rota 5

**Status:** `ROTA_5_CAD_HARDENING_PR_OPEN_AWAITING_CI_AND_REVIEW`
**Data:** 2026-09-12
**Branch:** `codex/v3.5-cad-hardening-resilience`
**Commit funcional:** `db78731b55b0eebb0bcc6d02ea9c6e1be12418c0`

## Objetivo e escopo

Consolidar a entrega AUTO-062, publicar a branch dedicada e abrir Pull Request
contra `main`, coletando o estado inicial do CI. Nenhum merge é autorizado.

## Entrega consolidada

- Hardening fail-closed para degeneração, abertura acima de 0,05 mm,
  auto-interseção vetorial e envelope dimensional conservador.
- Avisos estruturados de tolerância propagados até a UI com revisão obrigatória.
- Validação local aprovada: 738 testes Python, 9 ignorados, 64 testes Web,
  TypeScript, Next lint, Ruff, mypy e `git diff --check`.

## Operações autorizadas

Criar commit exclusivamente documental, publicar a branch, abrir o PR e consultar
as esteiras iniciais. Merge, deploy e alteração de autoridade física permanecem
fora do escopo.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.

## Continuidade

Enviar VTP-AUTO-063 ao CTO, solicitar parecer e aguardar a próxima ordem sem
encerrar a execução.
