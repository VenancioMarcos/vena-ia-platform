# CTO-CODEX-AUTO-121 a AUTO-125 — Integração SIM Rota 2 e workspace E2E Rota 3

**Status:** `SIM_ROTA_3_E2E_WORKSPACE_COMPLETED_LOCAL`
**Data:** 2026-09-13
**Branch:** `codex/v6.2-sim-e2e-workspace-view`
**Baseline:** `a952d433a1f46a65fbfcf830e6e4344168615899`

## Objetivo

Publicar e integrar o visualizador Canvas da Rota SIM 2 e entregar uma superfície
Web unificada para revisão humana de trajetória, telemetria e programa ISO.

## Execução do lote

| Ordem | Resultado |
| --- | --- |
| AUTO-121 | Branch SIM Rota 2 publicada e Draft PR #48 aberto. |
| AUTO-122 | Frontend CI aprovado em 1m55s; PR promovido a Ready, `MERGEABLE` e `CLEAN`. |
| AUTO-123 | PR #48 integrado por squash em `a952d43`; branch remota removida e `main` sincronizada. |
| AUTO-124 | Branch SIM Rota 3 criada da main e workspace integrado implementado. |
| AUTO-125 | Testes, regressão e governança consolidados localmente, sem push. |

## Escopo técnico

- `ToolpathCanvasViewer` admite controle externo do passo visível sem perder seu
  modo autônomo, permitindo que o scrub e a reprodução alimentem outras vistas.
- `SimulationWorkspace` conecta o passo atual ao X-diâmetro, Z, feed, ferramenta
  ativa e bloco ISO correspondente.
- O programa ISO é estritamente somente leitura e destaca o bloco sincronizado.
- A rota `/cnc/simulation` monta uma amostra tipada de auditoria sobre o mesmo
  contrato retornado pelo backend da Rota SIM 1.
- Payload ausente, vazio ou com erro produz fallback explícito, sem controles de
  reprodução ou tentativa de ação operacional.
- O card `ESTADO: AUDITORIA NÃO-EXECUTÁVEL` e o banner
  `AUDIT ONLY - PHYSICAL_USE_AUTHORIZED=FALSE` permanecem obrigatórios.

## Arquivos criados

- `apps/web/app/cnc/simulation/page.tsx`
- `apps/web/src/components/cnc/SimulationWorkspace.tsx`
- `apps/web/tests/simulation-workspace.test.ts`
- `docs/cto/CTO-CODEX-AUTO-125-BATCH.md`

## Arquivos modificados

- `apps/web/src/components/cnc/ToolpathCanvasViewer.tsx`
- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Validação

- Testes focais Canvas/workspace: 7 aprovados.
- Web completo: 71 testes `node:test` aprovados.
- TypeScript e Next lint: aprovados, sem erros ou avisos.
- Python completo: 789 aprovados e 9 ignorados.
- Ruff: aprovado; mypy: 210 arquivos sem problemas.
- `git diff --check`: aprovado.

## Critérios de aceitação

- Canvas, HUD e bloco ISO usam o mesmo índice de scrub de forma determinística.
- Passos fora da faixa são limitados ao domínio do payload.
- Estado indisponível é seguro, explícito e não oferece controles operacionais.
- Nenhuma dependência, backend, contrato ou autoridade física foi alterado.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

## Próxima etapa

Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
