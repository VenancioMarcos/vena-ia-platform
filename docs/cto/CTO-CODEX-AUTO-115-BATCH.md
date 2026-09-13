# CTO-CODEX-AUTO-111 a AUTO-115 — Fechamento CNC e fundação do simulador 2D

**Status:** `SIM_ROTA_1_TOOLPATH_VISUALIZER_FOUNDATION_COMPLETED_LOCAL`
**Data:** 2026-09-13
**Branch:** `codex/v6.0-sim-toolpath-visualizer-foundation`
**Baseline:** `d60cb88e53a1064d123fca4adcdd3e66ebadc956`

## Objetivo

Integrar a barreira cinemática que encerra o Épico CNC e criar a fundação segura
do visualizador 2D, convertendo programas ISO auditáveis em segmentos gráficos
sem emitir, transmitir ou executar instruções de máquina.

## Execução do lote

| Ordem | Resultado |
| --- | --- |
| AUTO-111 | Branch Rota 4 publicada e Draft PR #46 aberto. |
| AUTO-112 | Backend CI aprovado em 3m38s; PR promovido a Ready, `MERGEABLE` e `CLEAN`. |
| AUTO-113 | PR #46 integrado por squash em `d60cb88`; branch remota removida e `main` sincronizada. |
| AUTO-114 | Branch Rota SIM 1 criada da main e parser de trajetórias/contratos implementados. |
| AUTO-115 | Endpoint autenticado, testes, regressão e governança consolidados localmente, sem push. |

## Escopo técnico

- O parser aceita blocos G0/G00/G1/G01, coordenadas modais X-diâmetro/Z, avanço F
  positivo e seleção de ferramenta Fanuc/Haas ou Siemens.
- O primeiro ponto completo estabelece a posição conhecida; cada movimento seguinte
  gera um segmento imutável com início, fim, tipo, avanço e ferramenta ativa.
- A validação do envelope cinemático ocorre antes da decomposição, preservando os
  limites de curso e a zona de exclusão da placa já homologados na Rota CNC 4.
- `ToolpathSimulationPayload` reúne os segmentos, envelope, dimensões da peça bruta,
  convenção de coordenadas e flags permanentes de segurança.
- O endpoint `POST /api/v1/cnc/turning/simulate-toolpath` exige autenticação. Pode
  analisar um programa ISO limitado a 1 MB ou gerar o candidato de um plano CAM
  pertencente ao usuário, mantendo isolamento e falhas 401/404/422.

## Arquivos criados

- `apps/api/app/modules/cnc/services/simulation_parser.py`
- `apps/api/tests/unit/cnc/test_simulation_parser.py`
- `docs/cto/CTO-CODEX-AUTO-115-BATCH.md`

## Arquivos modificados

- `apps/api/app/modules/cnc/router.py`
- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/__init__.py`
- `apps/api/tests/integration/cnc/test_cnc_generation_router.py`
- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Validação

- Testes focados de parser e gateway CNC: 16 aprovados.
- Regressão Python completa: 789 aprovados, 9 ignorados.
- O teste concorrente CAD conhecido oscilou na primeira passagem e foi aprovado
  isoladamente; a repetição integral terminou com 789 aprovados e zero falhas.
- Web: 64 testes `node:test` aprovados.
- TypeScript e Next lint: aprovados, sem erros ou avisos.
- Ruff: aprovado.
- mypy: 210 arquivos sem problemas.
- `git diff --check`: aprovado.

## Critérios de aceitação

- Fanuc 0i, Siemens 840D e Haas produzem segmentos 2D determinísticos.
- Metadados de envelope, stock, avanço, ferramenta e segurança permanecem tipados.
- Programa direto exige autenticação; plano CAM também exige propriedade do usuário.
- Nenhuma dependência foi instalada e a branch Rota SIM 1 não foi publicada.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

## Próxima etapa

Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
