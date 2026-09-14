# Registro de Entrega — CTO-CODEX-AUTO-269 a AUTO-278

**Data:** 2026-09-14
**Estado:** `CNC_RESIDUAL_STOCK_AUDITOR_COMPLETED_LOCAL`
**Branch:** `codex/v8.1-cnc-residual-stock-auditor`
**Baseline:** `70515987d1b19758d549e8a6ff188dfa81116188`
**Publicação da branch atual:** não realizada

## Objetivo

Publicar e integrar a Folha de Processo da Rota 19 e implementar uma auditoria 2D,
determinística e vinculada ao perfil BRep para o sobremetal residual em processo da
Rota 20.

## Escopo entregue

- O `VTP-AUTO-268-BATCH` recebeu parecer explícito `APROVADO (A)` do CTO.
- O PR #67 foi publicado, aprovado pelo Backend CI em 2m49s e pelo Frontend CI em
  1m29s, promovido a ready e integrado por squash em `7051598`.
- A branch remota da Rota 19 foi removida e a `main` local foi sincronizada com
  `origin/main` antes da criação da branch da Rota 20.
- O registro do plano agora preserva o perfil R/Z nominal extraído do BRep; o
  fingerprint cobre requisição, resposta, limites e perfil, fechando a cadeia de
  rastreabilidade usada pelo relatório.
- `audit_residual_stock` recompõe as seções axiais nominais e o menor raio alcançado
  pelos segmentos CAM em cada seção. O resultado inclui sobremetal mínimo, máximo e
  médio, indicação explícita de gouging e snapshots completos das fontes.
- Qualquer sobremetal negativo produz `CRITICAL_GOUGING_VIOLATION`; valor máximo
  acima de `finish_allowance_nominal + 0,05 mm` produz
  `EXCESS_MATERIAL_DETECTED`; os demais casos produzem
  `UNIFORM_ALLOWANCE_COMPLIANT`.
- Perfis fora do estoque, sem seções axiais, descontínuos ou com degrau radial maior
  que a aresta de corte declarada falham fechado.
- O contrato imutável recalcula seções, envelope CAM, agregados e status e o
  relatório rejeita auditorias transplantadas de outro plano ou geometria.
- O exportador TEXT inclui a seção `AUDITORIA DE MATERIAL REMANESCENTE`; o viewer
  Web mostra máximo/mínimo/média/limite e os badges `SOBREMETAL HOMOGÊNEO` e
  `ALERTA: SUBCORTE DETECTADO (GOUGING)`.
- JSON, TEXT e Web exibem a nota obrigatória:
  `AUDITORIA ANALÍTICA DE MATERIAL REMANESCENTE - NÃO SUBSTITUI MEDIÇÃO
  TRIDIMENSIONAL FÍSICA EM CMM`.

## Arquivos criados

- `apps/api/app/modules/cnc/services/residual_stock_auditor.py`
- `apps/api/tests/unit/cnc/test_residual_stock_auditor.py`
- `docs/cto/CTO-CODEX-AUTO-278-BATCH.md`

## Arquivos modificados

- `CONTEXT.md`
- `apps/api/app/modules/cam/repository.py`
- `apps/api/app/modules/cam/router.py`
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

- API completa: `889 passed, 2 skipped`.
- Domínio CNC: `186 passed`.
- Auditor, relatório e integração focados: `46 passed`.
- Viewer Web compilado offline: `20 passed`.
- TypeScript integral: aprovado.
- Ruff: aprovado.
- mypy: aprovado em 226 fontes.
- Next lint: aprovado sem avisos ou erros.
- `git diff --check`: aprovado.
- Nenhuma dependência externa de rede foi instalada.

## Critérios de aceitação

- Um delta residual negativo é detectado exatamente como gouging crítico e nunca é
  convertido em tolerância aceitável.
- Sobremetal uniforme até `finish_allowance + 0,05 mm` é aceito; excesso acima do
  limite é sinalizado como sobrecarga potencial do passe de acabamento.
- Degraus nominais incompatíveis com o comprimento de aresta declarado são
  rejeitados com erro estável.
- Alterações nos snapshots, seções, raios alcançados, agregados ou status são
  rejeitadas pelo contrato ou pelo manifesto do relatório.
- O painel Web e o laudo textual exibem telemetria, badge e limitação CMM sem
  controles de autorização, envio, DNC, transferência NC ou cycle start.

## Limites e próximos passos

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Emitir `VTP-AUTO-278-BATCH`, solicitar parecer do CTO e aguardar a próxima ordem.
A branch da Rota 20 permanece local e sem push.
