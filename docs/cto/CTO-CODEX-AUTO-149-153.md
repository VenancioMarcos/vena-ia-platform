# CTO-CODEX-AUTO-149 a AUTO-153 — Estimativa teórica de ciclo CNC

## Objetivo

Adicionar estimativa analítica e determinística de tempo e percurso à simulação CNC,
sem produzir instruções executáveis nem inferir tempo físico homologado.

## Escopo

- Distâncias 2D de movimentos rápidos e lineares, tempo teórico por avanço efetivo
  e decomposição por ferramenta.
- Metadados no payload de simulação e card informativo no HUD do workspace.

## Arquivos Criados

- `apps/api/app/modules/cnc/services/cycle_time_estimator.py`
- `apps/api/tests/unit/cnc/test_cycle_time_estimator.py`
- Este registro de missão.

## Arquivos Modificados

- Contratos e parser de simulação CNC.
- Tipos, HUD e testes do workspace web.
- Registros de estado do CTO e `CONTEXT.md`.

## Testes Realizados

- Testes CNC focados: 19 aprovados.
- Backend completo: 798 aprovados, 9 ignorados.
- TypeScript, Next lint, Ruff, mypy e `git diff --check` aprovados.

## Critérios de Aceitação

A estimativa é exclusivamente teórica e exibe aviso explícito de não homologação
física. Avanço linear não resolvido falha fechado. Permanecem inalterados
`PHYSICAL_USE_AUTHORIZED=FALSE`, `G9=PENDING_AUTHORITATIVE_REVIEW`,
`MACHINE_SEND=FALSE`, `DNC=FALSE`, `NC_TRANSFER=FALSE`, `CYCLE_START=FALSE`,
`emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximos Passos

Publicar a branch, abrir o Draft PR #54, acompanhar o CI e promover para revisão
somente se os checks forem aprovados; o merge permanece fora deste lote.
