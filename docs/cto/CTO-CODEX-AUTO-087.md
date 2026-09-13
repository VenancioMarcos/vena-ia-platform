# CTO-CODEX-AUTO-087 — Gateway de planejamento CAM E2E

**Status:** `CAM_ROTA_4_E2E_GATEWAY_IN_PROGRESS`
**Data:** 2026-09-13
**Branch:** `codex/v4.3-cam-e2e-planning-gateway`
**Baseline:** `ad231f8a044e47e51fd4c1335a5fc0ad84fa4de0`

## Objetivo

Conectar o perfil RZ revisável produzido pelo pipeline CAD ao motor analítico de
estratégias de torneamento por uma fronteira HTTP autenticada, sem emitir instruções
executáveis ou conceder autoridade física.

## Escopo entregue

- Endpoint autenticado `POST /api/v1/cam/turning/plan` sob o router CAM v1.
- Consulta de `cad_job_id` limitada ao proprietário autenticado.
- Rejeição 404 para job inexistente ou de outro usuário e 422 para job sem perfil
  revisável, contrato interno inconsistente ou geometria recusada pelo motor CAM.
- Conversão explícita de pontos e bounding box CAD para os contratos CAM estritos.
- Seleção das estratégias `FACING`, `ROUGH_TURNING`, `FINISHING` e `GROOVING`.
- `plan_id` determinístico vinculado ao usuário, job, perfil e parâmetros do plano.
- Propagação sem duplicatas de warnings CAD e CAM.
- Resposta fixa em `PLANNED_REQUIRES_REVIEW`, com `executable_output=false`,
  `physical_use_authorized=false`, G9 pendente e perfil de controlador não resolvido.

## Arquivos criados ou modificados

- `apps/api/app/modules/cam/router.py`
- `apps/api/app/modules/cam/schemas.py`
- `apps/api/app/main.py`
- `apps/api/tests/integration/cam/test_cam_planning_router.py`
- `docs/cto/CTO-CODEX-AUTO-087.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `CONTEXT.md`

## Validação

- Gateway e CAM focal: 18 testes aprovados.
- Regressão Python integral: 758 aprovados, 9 ignorados.
- Regressão `apps/api/tests`: 689 aprovados, 2 ignorados.
- Regressão Web: 64 testes aprovados.
- Ruff: aprovado.
- mypy: 203 arquivos sem problemas.
- TypeScript: aprovado com `--noEmit --incremental false`.
- Next lint: aprovado sem erros ou avisos.
- `git diff --check`: aprovado.

## Critérios de aceitação

- [x] Usuário autenticado planeja a partir de seu job CAD concluído e revisável.
- [x] Job sem perfil revisável falha fechado com HTTP 422.
- [x] Perfil degenerado ou inconsistente falha fechado com HTTP 422.
- [x] Requisição sem autenticação retorna HTTP 401.
- [x] Resposta inclui `plan_id`, passes RZ, warnings e estado revisável.
- [x] Toda resposta mantém saída executável e autoridade física desativadas.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Não foram implementados gerador ISO G-code, pós-processador, comunicação com CNC,
transferência DNC/NC, cycle start ou controle físico.

## Próximos passos

Enviar o VTP-AUTO-087 ao CTO e aguardar a próxima ordem sem encerrar a execução.
