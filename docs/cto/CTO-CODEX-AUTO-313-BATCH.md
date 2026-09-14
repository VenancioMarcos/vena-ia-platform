# Registro de Entrega — CTO-CODEX-AUTO-304 a AUTO-313

**Data:** 2026-09-14
**Estado:** `CNC_TOOL_WEAR_GEOMETRY_CONTRACT_V2_SCAFFOLDED_LOCAL`
**Branch:** `codex/v8.5-cnc-tool-wear-compensation-geometry-auditor`
**Baseline:** `dd099b0deb29a11dd96deb827ca9a540ae76c50a`
**Publicação da branch atual:** não realizada

## Objetivo e escopo entregue

A Rota 23 implementou o motor determinístico `ΔL=α·L·ΔT`, integrou o contrato
térmico ao manifesto e TEXT e adicionou telemetria Web de temperaturas, deriva X/Z,
impacto e badges. O PR #71 passou Frontend CI em 1m10s e Backend CI em 2m55s, ficou
`MERGEABLE/CLEAN` e foi integrado por squash em `dd099b0`; a branch remota foi
removida e a main sincronizada.

A Rota 24 iniciou `ToolWearGeometryAuditPayload` no schema
`vena-ia.cnc-tool-wear-geometry-audit/v2`. O contrato vincula o consumo Taylor ao
VB estimado, raio de quina efetivo e desvios radial/axial, recalcula status por
tolerância e impede promoção de `compensation_authorized` ou autoridade física.

## Arquivos da Rota 24

- Modificado: `apps/api/app/modules/cnc/schemas.py`.
- Criado: `apps/api/tests/unit/cnc/test_tool_wear_geometry_contract.py`.
- Atualizados: `CONTEXT.md` e registros em `docs/cto/`.

## Testes e critérios de aceitação

- `240 passed` na suíte CNC e `6 passed` focados na Rota 24.
- Ruff, mypy em 210 fontes e `git diff --check` aprovados.
- VB, progresso, raio e desvios adulterados falham fechado.
- Tolerância excedida produz warning; compensação automática permanece proibida.
- Nenhuma dependência externa de rede foi instalada.

## Limites e próximos passos

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Emitir `VTP-AUTO-313-BATCH`, solicitar parecer do CTO e aguardar a próxima ordem.
