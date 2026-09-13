# CTO-CODEX-AUTO-116 a AUTO-120 — Integração SIM Rota 1 e visualizador Canvas Rota 2

**Status:** `SIM_ROTA_2_CANVAS_TOOLPATH_VIEWER_COMPLETED_LOCAL`
**Data:** 2026-09-13
**Branch:** `codex/v6.1-sim-canvas-toolpath-viewer`
**Baseline:** `36c21e7e76639c85b60524233128a85c3cc1a0d6`

## Objetivo

Publicar e integrar a fundação backend do simulador e entregar um componente Web
tipado que apresente a trajetória 2D de forma interativa e exclusivamente auditável.

## Execução do lote

| Ordem | Resultado |
| --- | --- |
| AUTO-116 | Branch SIM Rota 1 publicada e Draft PR #47 aberto. |
| AUTO-117 | Backend CI aprovado em 3m09s; PR promovido a Ready, `MERGEABLE` e `CLEAN`. |
| AUTO-118 | PR #47 integrado por squash em `36c21e7`; branch remota removida e `main` sincronizada. |
| AUTO-119 | Branch SIM Rota 2 criada da main e visualizador Canvas implementado. |
| AUTO-120 | Testes, regressão e governança consolidados localmente, sem push. |

## Escopo técnico

- Tipos TypeScript reproduzem estritamente o `ToolpathSimulationPayload`, incluindo
  segmentos, envelope, stock, controlador e flags de segurança.
- O Canvas projeta Z no eixo horizontal e X-diâmetro no vertical, preservando a
  escala do envelope e mostrando as linhas centrais quando pertencem ao domínio.
- O stock aparece como caixa delimitadora; a zona proibida da placa/castanhas usa
  preenchimento e contorno vermelhos de advertência.
- G00 é exibido em linha laranja tracejada e G01 em linha ciano contínua.
- Play, Pause e scrub controlam quantos segmentos são desenhados, sem dependência
  externa e sem qualquer chamada de rede ou ação física.
- O banner `AUDIT ONLY - PHYSICAL_USE_AUTHORIZED=FALSE` aparece inclusive no
  estado vazio, que não tenta desenhar um payload sem segmentos.

## Arquivos criados

- `apps/web/src/components/cnc/ToolpathCanvasViewer.tsx`
- `apps/web/tests/toolpath-canvas-viewer.test.ts`
- `docs/cto/CTO-CODEX-AUTO-120-BATCH.md`

## Arquivos modificados

- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Validação

- Testes focados do componente: 3 aprovados.
- Web completo: 67 testes `node:test` aprovados.
- TypeScript e Next lint: aprovados, sem erros ou avisos.
- Backend no mesmo baseline funcional: 789 testes Python aprovados e 9 ignorados.
- Na execução deste lote, o teste concorrente CAD conhecido oscilou e passou na
  repetição focal; nenhum arquivo Python foi alterado pela Rota SIM 2.
- Ruff: aprovado.
- mypy: 210 arquivos sem problemas.
- `git diff --check`: aprovado.

## Critérios de aceitação

- Payload válido produz Canvas, legenda e controles sem mutação dos dados.
- Payload vazio produz estado seguro e previsível, sem Canvas parcial.
- O aviso de governança permanece presente em todas as renderizações.
- Nenhuma dependência foi instalada e a branch Rota SIM 2 não foi publicada.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

## Próxima etapa

Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
