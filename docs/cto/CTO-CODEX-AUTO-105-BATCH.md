# CTO-CODEX-AUTO-101 a AUTO-105 — Integração CNC Rota 2 e dialetos Rota 3

**Status:** `CNC_ROTA_3_CONTROLLER_DIALECTS_COMPLETED_LOCAL`
**Data:** 2026-09-13
**Branch:** `codex/v5.2-cnc-controller-dialects`
**Baseline:** `9036a48053981f592526eeec2263939155237c92`

## Objetivo

Publicar e integrar o gateway CNC da Rota 2 e implementar candidatos de programa
determinísticos, revisáveis e não executáveis para controladores Fanuc 0i, Siemens
840D e Haas, mantendo as travas de emissão e uso físico.

## Execução do lote

| Ordem | Resultado |
| --- | --- |
| AUTO-101 | Branch Rota 2 publicada e Draft PR #44 aberto. |
| AUTO-102 | Backend CI aprovado em 3m23s; PR promovido a Ready, `MERGEABLE` e `CLEAN`. |
| AUTO-103 | PR #44 integrado por squash em `9036a48`; branch remota removida e `main` sincronizada. |
| AUTO-104 | Branch Rota 3 criada da main integrada e três dialetos implementados. |
| AUTO-105 | Limites, testes, regressão e governança consolidados localmente, sem push. |

## Escopo técnico

- `FANUC_0I`: programa `O<number>`, seleção `T<tt><cc>`, movimentos G00/G01,
  G96/G97 e limite CSS `G50 S<max>`.
- `SIEMENS_840D`: programa MPF, seleção `T="FERRAMENTA" D1`, movimentos G0/G1,
  G96/G97 e limite CSS `LIMS=<max>`.
- `HAAS`: formato compatível com a família Fanuc, seleção de ferramenta e
  encerramento limpo M05/M30.
- O contrato recebe limite máximo de rotação, limite efetivo de avanço e dados de
  ferramenta. G97 acima da rotação configurada e avanço efetivo acima do limite
  retornam falhas estáveis e fechadas.
- O gateway autenticado propaga esses parâmetros ao formatador owner-scoped.
- Todos os dialetos incorporam integralmente os cabeçalhos de governança e
  continuam com `PLANNED_REQUIRES_REVIEW` e `executable_output=false`.

## Arquivos criados

- `docs/cto/CTO-CODEX-AUTO-105-BATCH.md`

## Arquivos modificados

- `apps/api/app/modules/cnc/router.py`
- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/gcode_formatter.py`
- `apps/api/tests/unit/cnc/test_gcode_formatter.py`
- `apps/api/tests/integration/cnc/test_cnc_generation_router.py`
- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Validação

- Testes focados CNC: 19 aprovados.
- Regressão Python completa: 777 aprovados, 9 ignorados.
- Web: 64 testes `node:test` aprovados.
- Ruff: aprovado.
- mypy: 208 arquivos sem problemas.
- `git diff --check`: aprovado.

## Critérios de aceitação

- Cada perfil produz somente sua sintaxe allowlisted e o mesmo pedido é
  determinístico.
- Limites inválidos ou incompatíveis são rejeitados antes de formar o candidato.
- O endpoint continua autenticado, owner-scoped e sem operações de envio à máquina.
- Nenhuma dependência foi instalada e a branch Rota 3 não foi publicada.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

## Próxima etapa

Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
