# CTO-CODEX-AUTO-079 — Acabamento contínuo e compensação de raio

**Status:** `CAM_ROTA_2_FINISHING_STRATEGY_IN_PROGRESS`
**Data:** 2026-09-12
**Branch:** `codex/v4.1-cam-finishing-strategy`
**Baseline:** `4ba57db11809de4317b21e71e3029a98f9b6ed52`

## Objetivo

Estender o motor CAM analítico com uma estratégia determinística de acabamento
contínuo em perfis RZ, compensada pelo raio de ponta, sem gerar comandos de máquina.

## Escopo

- Campo estrito `finish_allowance_mm` no contrato de planejamento.
- Extração conservadora do contorno externo entre os limites frontal e traseiro.
- Um passe contínuo de `FINISHING` sobre linhas e curvas discretizadas em pontos RZ.
- Offset vetorial normal com raio de ponta mais sobremetal residual.
- Alcance efetivo limitado pela projeção do comprimento e ângulo da aresta de corte.
- Rejeição fail-closed de retorno em Z, degeneração, interferência de offset e raio
  de ponta maior que a curvatura côncava local.
- `GROOVING` permanece não implementado e bloqueado.

## Arquivos modificados

- `apps/api/app/modules/cam/schemas.py`
- `apps/api/app/modules/cam/services/strategy_engine.py`
- `apps/api/tests/unit/cam/test_turning_strategy_engine.py`
- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Validação

- CAM focal: 12 testes aprovados.
- Regressão Python integral: 752 aprovados, 9 ignorados.
- Regressão Web preservada: 64 testes aprovados.
- Ruff: aprovado.
- mypy: aprovado.
- `git diff --check`: aprovado.

## Critérios de aceitação

- Perfis lineares e curvos discretizados geram um passe contínuo determinístico.
- Raio de ponta, sobremetal e ângulo/comprimento da aresta influenciam o offset e
  sua viabilidade geométrica.
- Concavidade menor que o raio da ferramenta falha fechado.
- `GROOVING` continua rejeitado e a resposta preserva `executable_output=false`.

## Limites permanentes

`G9=PENDING_AUTHORITATIVE_REVIEW`; `PHYSICAL_USE_AUTHORIZED=FALSE`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

## Continuidade

Enviar VTP-AUTO-079 ao CTO e aguardar a próxima ordem sem encerrar a execução.
