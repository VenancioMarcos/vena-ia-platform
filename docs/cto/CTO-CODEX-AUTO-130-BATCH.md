# CTO-CODEX-AUTO-126 a AUTO-130 — Integração SIM Rota 3 e auditoria de proximidade da placa

**Data:** 2026-09-13

**Estado:** `SIM_ROTA_4_CHUCK_PROXIMITY_AUDIT_COMPLETED_LOCAL`

**Branch:** `codex/v6.3-sim-chuck-proximity-audit`

**Baseline:** `59c8a0ed6ef620b8c6c81af16ebc933f43819a0d`

## Objetivo e escopo

Publicar e integrar o workspace SIM Rota 3 e criar, sem push, a Rota 4 de auditoria
da folga entre a trajetória e o contorno da zona de exclusão da placa.

| Ordem | Resultado |
|---|---|
| AUTO-126 | Branch da Rota 3 publicada e Draft PR #49 criado. |
| AUTO-127 | Frontend CI aprovado; PR #49 convertido para Ready e confirmado `CLEAN`. |
| AUTO-128 | PR #49 integrado por squash em `59c8a0e`; `main` local sincronizada. |
| AUTO-129 | Cálculo euclidiano determinístico, metadados da API e alertas Canvas/HUD implementados. |
| AUTO-130 | Regressão completa, governança e commit local consolidados. |

## Implementação e critérios de aceitação

- Cada segmento é comparado às quatro arestas da zona retangular da placa; o menor
  valor global registra folga, índice do segmento e limiar de 5,0 mm.
- Uma folga estritamente menor que 5,0 mm produz `WARNING_PROXIMITY_CHUCK`; 5,0 mm
  exatos permanecem sem aviso. Invasões continuam bloqueadas pelo validador de envelope.
- `POST /api/v1/cnc/turning/simulate-toolpath` inclui `chuck_proximity` no contrato
  estrito e mantém todas as flags de segurança.
- O HUD exibe badge crítico com a folga medida, e o Canvas realça e pulsa a zona da
  placa quando o alerta está ativo.

## Arquivos criados/modificados

- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/simulation_parser.py`
- `apps/api/tests/unit/cnc/test_simulation_parser.py`
- `apps/api/tests/integration/cnc/test_cnc_generation_router.py`
- `apps/web/src/components/cnc/ToolpathCanvasViewer.tsx`
- `apps/web/src/components/cnc/SimulationWorkspace.tsx`
- `apps/web/app/cnc/simulation/page.tsx`
- `apps/web/tests/toolpath-canvas-viewer.test.ts`
- `apps/web/tests/simulation-workspace.test.ts`
- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Validação

- `pytest`: 791 aprovados, 9 ignorados.
- Web `node:test`: 73 aprovados.
- TypeScript `tsc --noEmit --incremental false`: aprovado.
- Next lint: zero erros e zero avisos.
- Ruff: aprovado.
- mypy: 210 arquivos aprovados.
- `git diff --check`: aprovado.

## Limites e continuidade

Nenhum push da Rota 4, dependência externa, comunicação com controlador, transferência
NC/DNC ou ciclo físico foi realizado. O resultado permanece não executável e sujeito
a revisão humana autoritativa. Próxima ação: solicitar parecer do CTO e aguardar a
próxima ordem sem encerrar a execução.
