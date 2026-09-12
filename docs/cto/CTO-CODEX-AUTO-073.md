# CTO-CODEX-AUTO-073 — Fechamento oficial do épico CAD

**Status:** `CAD_EPIC_OFFICIALLY_CLOSED_BASELINE_TAGGED`
**Data:** 2026-09-12
**PR:** `#38`
**Merge commit:** `a6babbde437e5547e00ba83038218d7d69178023`
**Tag:** `v0.7.0-cad`
**Tag object remoto:** `63fc7d443e01e3653e7db80f370e51c029d393aa`
**Fechamento local:** `codex/auto-073-cad-baseline-closeout`

## Resultado

O PR #38 foi integrado por squash merge em 2026-09-12T19:30:01Z. A `main`
local e `origin/main` ficaram alinhadas em `a6babbd`. A tag anotada
`v0.7.0-cad` foi publicada e referencia exatamente esse commit.

## Baseline congelada

- Rotas 2 a 5 do épico de ingestão e processamento CAD STEP.
- Cliente, gateway autenticado, sandbox, worker, perfil RZ, SVG e warnings.
- Hardening geométrico, concorrência e payload exato de 15 MiB.
- 740 testes Python, 9 ignorados, 64 Web e checks estáticos homologados.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.

## Continuidade

Enviar VTP-AUTO-073 ao CTO, solicitar parecer e aguardar a próxima ordem sem
encerrar a execução.
