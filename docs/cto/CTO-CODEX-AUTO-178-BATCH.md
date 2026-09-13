# CTO-CODEX-AUTO-169 a AUTO-178 — Gate dimensional e laudo textual CNC

**Status:** Entrega técnica local concluída
**Data:** 2026-09-13
**Papel:** Executor Técnico (Codex)
**Branch:** `codex/v7.1-cnc-dimensional-gate-integration`
**Baseline:** `ac65258800f2a5a685763ea03bd37a2146df3f91`

## Objetivo

Integrar o auditor dimensional da Rota 9 ao manifesto analítico, disponibilizar um
laudo textual restrito e apresentar a evidência dimensional na interface, sem criar
saída executável nem autoridade física.

## Escopo entregue

- PR #57 aprovado pelo Backend CI, promovido a revisão e integrado por squash em
  `ac65258`; branch remota removida e `main` sincronizada.
- Limites nominais R/Z do BRep preservados no registro owner-scoped do plano CAM e
  incluídos no fingerprint que vincula plano, simulação e relatório.
- Auditoria dimensional executada após a revalidação da simulação e antes da criação
  do manifesto. Divergências retornam 422 estruturado com evidência analítica e sem
  texto de programa.
- Contrato JSON do relatório ampliado com `geometry_audit`, incluindo valores
  nominais, programados, desvios assinados e tolerâncias.
- Formatador textual determinístico com o carimbo
  `RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO` em todas as seções.
- Endpoint autenticado e owner-scoped
  `GET /api/v1/cnc/turning/plans/{plan_id}/report/download`, com attachment, nome
  opaco, `no-store`, `nosniff` e CSP restritiva. Ausência de simulação ou auditoria
  rejeitada fecha o acesso ao arquivo.
- Viewer web com status visual, tabela de desvios e link de exportação textual com
  o aviso obrigatório, sem controles de máquina.

## Arquivos criados ou modificados

- `apps/api/app/modules/cam/repository.py`
- `apps/api/app/modules/cam/router.py`
- `apps/api/app/modules/cnc/router.py`
- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/geometry_auditor.py`
- `apps/api/app/modules/cnc/services/machining_report.py`
- `apps/api/app/modules/cnc/services/text_report_exporter.py`
- `apps/api/tests/integration/cnc/test_cnc_generation_router.py`
- `apps/api/tests/unit/cnc/test_machining_report.py`
- `apps/web/src/components/cnc/MachiningTechnicalReportViewer.tsx`
- `apps/web/tests/machining-technical-report-viewer.test.ts`
- `CONTEXT.md` e registros em `docs/cto/`

## Validação

- 46 testes focados das ordens 172–173 passaram antes da ampliação do contrato.
- 4 testes `node:test` do viewer passaram após compilação TypeScript estrita em
  imagem Docker local validada.
- Smokes na imagem API local aprovaram contrato, relatório, cinco carimbos,
  endpoint de download, headers restritivos, isolamento owner-scoped e bloqueio
  422 em auditoria rejeitada.
- `compileall` e `git diff --check` aprovados.
- A suíte integral Python e o typecheck web completo não puderam ser repetidos no
  ambiente final: o Python global não possui pytest e a imagem web local não contém
  Playwright. Nenhuma dependência foi instalada pela rede, conforme a ordem.

## Critérios de aceitação

- Manifesto e download existem somente com simulação vinculada e auditoria aprovada.
- Rejeição dimensional fornece evidência estruturada e não produz arquivo.
- Cada seção textual repete o carimbo obrigatório.
- Interface distingue conformidade e desvio e não oferece comandos físicos.
- Permanecem fixos `PHYSICAL_USE_AUTHORIZED=FALSE`,
  `G9=PENDING_AUTHORITATIVE_REVIEW`, `NO_HUMAN_REVIEW_BYPASS=TRUE`,
  `MACHINE_SEND/DNC/NC_TRANSFER/CYCLE_START=false`,
  `emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximo passo

Enviar VTP-AUTO-178-BATCH ao CTO e aguardar parecer. A branch e o commit permanecem
locais, sem push.
