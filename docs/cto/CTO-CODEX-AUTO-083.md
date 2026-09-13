# CTO-CODEX-AUTO-083 — Estratégia analítica de canais

**Status:** `CAM_ROTA_3_GROOVING_STRATEGY_PR_OPEN_AWAITING_CI_AND_REVIEW`
**Data:** 2026-09-12
**Branch:** `codex/v4.2-cam-grooving-strategy`
**Baseline:** `2703e37741f276b4aac6b68595513810848eab8b`

## Objetivo

Estender o motor CAM analítico com planejamento determinístico de canais por
mergulho radial e passes laterais em Z, sem produzir instruções executáveis.

## Escopo

- Campo estrito opcional `insert_width_mm` no contrato de ferramenta, obrigatório
  para operações `GROOVING`.
- Identificação conservadora de pisos axiais delimitados por dois ombros externos.
- Mergulho radial dividido por `depth_of_cut_mm`, seguido de recuo completo de alívio.
- Passe único quando a largura do canal coincide com a pastilha.
- Passes laterais escalonados para canais largos, com sobreposição mínima igual a
  duas vezes o raio de canto (`tip_radius_mm`).
- Rejeição fail-closed de canal estreito, raio de canto incompatível, geometria sem
  canal e mergulho fora do envelope de estoque.
- Volume removido calculado sem duplicar as regiões de sobreposição axial.

## Arquivos modificados

- `apps/api/app/modules/cam/schemas.py`
- `apps/api/app/modules/cam/services/strategy_engine.py`
- `apps/api/tests/unit/cam/test_turning_strategy_engine.py`
- `docs/cto/CTO-CODEX-AUTO-083.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`

## Validação

- CAM focal: 14 testes aprovados.
- Regressão Python integral: 754 aprovados, 9 ignorados.
- Regressão Web preservada: 64 testes aprovados.
- Ruff: aprovado.
- mypy: aprovado em 202 arquivos.
- TypeScript e Next lint: aprovados, sem avisos.
- `git diff --check`: aprovado.

## Critérios de aceitação

- Canal com largura igual à pastilha gera um mergulho único com recuo.
- Canal largo gera centros em Z determinísticos com sobreposição segura.
- Canal mais estreito que a pastilha falha fechado.
- A resposta mantém `executable_output=false` e todas as salvaguardas permanentes.

## Limites permanentes

`G9=PENDING_AUTHORITATIVE_REVIEW`; `PHYSICAL_USE_AUTHORIZED=FALSE`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

## Continuidade

Publicar a branch, abrir Draft PR contra `main`, coletar o CI inicial e enviar
VTP-AUTO-084 ao CTO sem executar merge.
