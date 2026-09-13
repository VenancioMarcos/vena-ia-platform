# CTO-CODEX-AUTO-091 a AUTO-095 — Fundação CNC de candidatos ISO

**Status:** `CNC_ROTA_1_GCODE_FOUNDATION_COMPLETED_LOCAL`
**Data:** 2026-09-13
**Branch:** `codex/v5.0-cnc-generation-foundation`
**Baseline:** `d3fafcd86eea65aa075e61904a33c2c2ba6888e8`

## Objetivo

Estabelecer a primeira fundação canônica do domínio CNC para transformar passes
analíticos CAM em texto ISO determinístico sujeito a revisão, mantendo bloqueadas
todas as formas de emissão, transferência, partida de ciclo e uso físico.

## Execução do lote

| Ordem | Resultado |
| --- | --- |
| AUTO-091 | PR #42 confirmado como integrado; `main` e `origin/main` alinhadas em `d3fafcd`. |
| AUTO-092 | Branch dedicada criada da baseline e enums CNC canônicos adicionados. |
| AUTO-093 | Contratos estritos e formatador ISO analítico implementados. |
| AUTO-094 | Testes focados e regressões completas aprovados. |
| AUTO-095 | Governança consolidada e pacote preparado para commit local, sem push. |

## Escopo técnico

- Perfis de controlador allowlisted: `FANUC_0I`, `SIEMENS_840D`, `HAAS` e
  `SIMULATED_STUB`.
- Modos G94/G95, G96/G97 e nível `AUDIT_ONLY_NON_EXECUTABLE` representados por
  enums fechados.
- Requisição vinculada ao `plan_id`, plano CAM revisável, programa numérico e
  contexto de revisão autenticado.
- Programa determinístico com cabeçalho declarativo, unidades métricas, plano XZ,
  aproximação G00 e avanço G01. Raios CAM são convertidos explicitamente para a
  convenção X-diâmetro de torno.
- Metadados incluem comprimento de percurso, tempo analítico estimado e contagem de
  blocos de movimento.
- Entradas fora do allowlist, sem autenticação de revisão ou com invariantes CAM
  incompatíveis falham fechadas.

## Arquivos criados

- `apps/api/app/modules/cnc/enums.py`
- `apps/api/app/modules/cnc/services/__init__.py`
- `apps/api/app/modules/cnc/services/gcode_formatter.py`
- `apps/api/tests/unit/cnc/__init__.py`
- `apps/api/tests/unit/cnc/test_gcode_formatter.py`
- `docs/cto/CTO-CODEX-AUTO-095.md`

## Arquivos modificados

- `apps/api/app/modules/cnc/schemas.py`
- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Validação

- Testes CNC focados: 4 aprovados.
- Regressão Python: 762 aprovados, 9 ignorados.
- Web: 64 testes `node:test` aprovados.
- Ruff: aprovado.
- mypy: 206 arquivos sem problemas.
- `git diff --check`: aprovado.

## Critérios de aceitação

- O mesmo plano e configuração produzem texto idêntico.
- Todo candidato contém as salvaguardas permanentes em texto e no contrato tipado.
- Controlador não suportado e ausência de autenticação de revisão são rejeitados.
- Nenhuma dependência, rota HTTP, integração física ou mecanismo de transmissão foi
  adicionado.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

## Próxima etapa

Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
