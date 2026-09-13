# CTO-CODEX-AUTO-106 a AUTO-110 — Integração CNC Rota 3 e envelope cinemático Rota 4

**Status:** `CNC_ROTA_4_KINEMATIC_ENVELOPE_VALIDATOR_COMPLETED_LOCAL`
**Data:** 2026-09-13
**Branch:** `codex/v5.3-cnc-kinematic-envelope-validator`
**Baseline:** `27c48affd7091dd05d4e6cdd67b7b7ab098c8d00`

## Objetivo

Publicar e integrar os dialetos da Rota 3 e inserir uma barreira analítica obrigatória
que impeça candidatos com movimentos fora dos cursos X/Z ou em interseção com a
zona de exclusão da placa, sem conceder autoridade de execução física.

## Execução do lote

| Ordem | Resultado |
| --- | --- |
| AUTO-106 | Branch Rota 3 publicada e Draft PR #45 aberto. |
| AUTO-107 | Backend CI aprovado em 3m17s; PR promovido a Ready, `MERGEABLE` e `CLEAN`. |
| AUTO-108 | PR #45 integrado por squash em `27c48af`; branch remota removida e `main` sincronizada. |
| AUTO-109 | Branch Rota 4 criada da main e validador de envelope integrado ao formatador. |
| AUTO-110 | Testes, regressão e governança consolidados localmente, sem push. |

## Escopo técnico

- Contratos estritos representam o envelope da máquina em X-diâmetro/Z e uma zona
  retangular proibida para placa/castanhas; limites invertidos são rejeitados.
- O analisador aceita exclusivamente coordenadas numéricas em blocos G0/G00/G1/G01,
  preserva coordenadas modais após o primeiro ponto completo e rejeita blocos
  incompletos, malformados ou duplicados.
- Cada ponto é validado contra os cursos inclusivos de X e Z.
- Cada segmento é testado analiticamente contra o retângulo fechado da placa;
  tocar a fronteira também é uma violação.
- O formatador executa essa validação antes de construir a resposta. O gateway
  converte `KinematicBoundaryViolation` em HTTP 422.
- O envelope é obrigatório na API, evitando validar com limites implícitos ou
  presumidos enquanto o perfil de controlador permanece sem resolução autoritativa.

## Arquivos criados

- `apps/api/app/modules/cnc/services/envelope_validator.py`
- `apps/api/tests/unit/cnc/test_envelope_validator.py`
- `docs/cto/CTO-CODEX-AUTO-110-BATCH.md`

## Arquivos modificados

- `apps/api/app/modules/cnc/router.py`
- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/__init__.py`
- `apps/api/app/modules/cnc/services/gcode_formatter.py`
- `apps/api/tests/unit/cnc/test_gcode_formatter.py`
- `apps/api/tests/integration/cnc/test_cnc_generation_router.py`
- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Validação

- Testes focados CNC e gateway: 25 aprovados.
- Regressão Python completa: 783 aprovados, 9 ignorados.
- Web: 64 testes `node:test` aprovados.
- Ruff: aprovado.
- mypy: 209 arquivos sem problemas.
- `git diff --check`: aprovado.

## Critérios de aceitação

- Trajetórias seguras dentro do envelope são aceitas deterministicamente.
- Interseção com a zona da placa e estouro dos cursos X/Z são interrompidos.
- A barreira é obrigatória no formatador e a API falha de forma controlada em 422.
- Nenhuma dependência foi instalada e a branch Rota 4 não foi publicada.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

## Próxima etapa

Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
