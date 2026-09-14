# Registro de Entrega — CTO-CODEX-AUTO-259 a AUTO-268

**Data:** 2026-09-14
**Estado:** `CNC_OPERATIONAL_PROCESS_ROUTING_SHEET_COMPLETED_LOCAL`
**Branch:** `codex/v8.0-cnc-process-routing-sheet`
**Baseline:** `b2d897e87248e4d87c6341635826c0c8b8b014a4`
**Publicação da branch atual:** não realizada

## Objetivo

Publicar e integrar a Matriz de Risco CNC da Rota 18 e implementar uma Folha de
Processo operacional teórica, determinística e auditável para a Rota 19.

## Escopo entregue

- O `VTP-AUTO-258-BATCH` recebeu parecer explícito `APROVADO (A)` do CTO.
- O PR #66 foi publicado, aprovado pelo Backend CI em 3m38s e pelo Frontend CI em
  1m24s, promovido a ready e integrado por squash em `b2d897e`.
- A branch remota da Rota 18 foi removida e a `main` local foi sincronizada com
  `origin/main` antes da criação da branch da Rota 19.
- O gerador cria `SETUP` seguido dos passes CAM em ordem, distribui o tempo teórico
  por volume removido e registra ferramenta, inserto descritivo, Vc, f, ap, rpm,
  avanço, fixação e revisão de balanço.
- `MachiningProcessSheetPayload` e seus contratos filhos revalidam estoque, placa,
  folga, sequência, IDs, parâmetros e tempos contra os snapshots incorporados.
- O manifesto `vena-ia.cnc-machining-report/v1` rejeita folhas transplantadas e
  verifica plano, peça, ferramentas, operações, parâmetros, envelope, proximidade e
  estimativa de ciclo.
- O exportador TEXT e o viewer Web exibem a tabela cronológica, setup, instruções e
  a nota obrigatória de aprovação pelo preparador de máquinas.

## Arquivos criados

- `apps/api/app/modules/cnc/services/process_sheet_generator.py`
- `apps/api/tests/unit/cnc/test_process_sheet_generator.py`
- `docs/cto/CTO-CODEX-AUTO-268-BATCH.md`

## Arquivos modificados

- `CONTEXT.md`
- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/machining_report.py`
- `apps/api/app/modules/cnc/services/text_report_exporter.py`
- `apps/api/tests/integration/cnc/test_cnc_generation_router.py`
- `apps/api/tests/unit/cnc/test_machining_report.py`
- `apps/web/src/components/cnc/MachiningTechnicalReportViewer.tsx`
- `apps/web/tests/machining-technical-report-viewer.test.ts`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Testes e verificações

- API completa: `883 passed, 2 skipped`.
- Domínio CNC: `180 passed`.
- Gerador, relatório e integração focados: `48 passed`.
- Viewer Web compilado: `18 passed`.
- TypeScript integral: aprovado.
- Next lint: aprovado sem avisos ou erros.
- Ruff: aprovado.
- mypy: aprovado em 193 fontes.
- `git diff --check`: aprovado.
- Nenhuma dependência externa de rede foi instalada.

## Critérios de aceitação

- Sequência CAM desordenada ou operação divergente falha fechado.
- Parâmetros ausentes/inválidos, tempo negativo, estoque fora do envelope ou folga
  nula são rejeitados.
- Snapshots transplantados de CAM, estoque, envelope, proximidade ou tempo são
  rejeitados pelo contrato e pelo manifesto.
- JSON, TEXT e Web incluem folha, metadados de setup, tabela operacional e nota de
  governança.
- Não existem botões ou caminhos de autorização, envio, DNC, transferência NC ou
  cycle start.

## Limites e próximos passos

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Emitir `VTP-AUTO-268-BATCH`, solicitar parecer do CTO e aguardar a próxima ordem.
A branch da Rota 19 permanece local e sem push.
