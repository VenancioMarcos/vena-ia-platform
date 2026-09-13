# CTO-CODEX-AUTO-159 a AUTO-163 — Visualizador web do relatório CNC

## Objetivo

Publicar a Rota CNC 7, integrar sua baseline e criar um visualizador declarativo
e estritamente não operacional para `vena-ia.cnc-machining-report/v1`.

## Escopo

- AUTO-159: branch da Rota 7 publicada e Draft PR #55 aberto.
- AUTO-160: primeira execução do Backend CI revelou import de helper de teste não
  portável para Linux. O fixture foi tornado autocontido em `ef524bb`; Backend CI
  passou em 3m29s. PR #55 está Ready for Review, MERGEABLE e CLEAN.
- AUTO-161: após autorização humana explícita, PR #55 integrado por squash em
  `3b6f8e6`; branch remota removida e `main=origin/main`.
- AUTO-162/163: preparados localmente na branch
  `codex/v6.9-cnc-report-viewer-web` e reancorados sobre o squash integrado.

## Arquivos Criados

- `apps/web/src/components/cnc/MachiningTechnicalReportViewer.tsx`
- `apps/web/tests/machining-technical-report-viewer.test.ts`
- Este registro.

## Arquivos Modificados

- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Testes Realizados

- Backend API local: 749 aprovados, 2 ignorados.
- Operações locais: 69 aprovados, 7 ignorados; total Python 818/9.
- Backend CI do PR #55: SUCCESS, 3m29s, Python 3.13.11.
- Web `node:test`: 77 aprovados; TypeScript e Next lint aprovados sem warnings.
- Ruff, mypy em 214 arquivos e `git diff --check`: aprovados.

## Critérios de Aceitação

O espelho TypeScript restringe schema, status e flags. O componente exibe tempos,
distâncias, ferramentas, operações, envelope, proximidade, hash, limitações e o
carimbo compulsório. Não contém botões nem controles de envio ou execução física.
Todas as invariantes permanecem literais e nenhum endpoint/backend foi alterado.

## Próximos Passos

Enviar o VTP atualizado ao CTO e aguardar nova ordem. A branch web não deve ser
publicada sem autorização explícita.
