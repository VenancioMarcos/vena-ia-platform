# CTO-CODEX-AUTO-179 a AUTO-188 — Auditoria de rugosidade teórica CNC

**Status:** Entrega técnica local concluída
**Data:** 2026-09-13
**Papel:** Executor Técnico (Codex)
**Branch:** `codex/v7.2-cnc-surface-roughness-estimator`
**Baseline:** `8d06fe5fbe17d4fef4f5ca4ed600ec112768b5fb`

## Objetivo

Publicar a Rota 10 e acrescentar ao relatório CNC uma estimativa ideal de rugosidade
de torneamento, com limites formais que impeçam sua interpretação como medição ou
aprovação física.

## Escopo entregue

- PR #58 aberto, aprovado pelo Backend CI em 3m27s e pelo Frontend CI em 1m09s,
  promovido a Ready e integrado por squash em `8d06fe5`; branch remota removida e
  `main=origin/main`.
- Serviço `roughness_estimator.py` com `Rz/Rt = f²/(8·rε)` e
  `Ra = f²/(32·rε)`, convertido de milímetros para micrômetros.
- Validação fail-closed de avanço, raio de ponta e tolerância Ra nominal, incluindo
  rejeição de zero, negativos, booleanos, NaN, infinito e faixas excessivas.
- Contrato estrito `vena-ia.cnc-surface-roughness-audit/v1` com Ra/Rz teóricos,
  avanço, raio, tolerância nominal opcional, tag de conformidade e flags imutáveis.
- Campo opcional `nominal_surface_roughness_ra_um` no pedido CAM para que a tag use
  um limite declarado; ausência resulta explicitamente em
  `NOMINAL_RA_TOLERANCE_UNAVAILABLE`.
- Integração da auditoria ao manifesto JSON e ao laudo textual, sem alterar o gate
  dimensional owner-scoped.
- Viewer Web com Ra, Rz, avanço, raio e a nota obrigatória
  `RUGOSIDADE TEÓRICA CINEMÁTICA - NÃO CONSIDERA VIBRAÇÃO OU DESGASTE DA FERRAMENTA`.

## Arquivos criados ou modificados

- `apps/api/app/modules/cam/schemas.py`
- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/roughness_estimator.py`
- `apps/api/app/modules/cnc/services/machining_report.py`
- `apps/api/app/modules/cnc/services/text_report_exporter.py`
- `apps/api/tests/unit/cnc/test_roughness_estimator.py`
- `apps/api/tests/unit/cnc/test_machining_report.py`
- `apps/web/src/components/cnc/MachiningTechnicalReportViewer.tsx`
- `apps/web/tests/machining-technical-report-viewer.test.ts`
- `CONTEXT.md` e registros em `docs/cto/`

## Validação

- PR #58: Backend CI e Frontend CI aprovados antes do squash.
- 5/5 testes `node:test` focados aprovados após compilação TypeScript estrita em
  imagem local validada.
- Smoke API em contêiner aprovou os raios ISO 0,4/0,8/1,2 mm, as duas tags de
  conformidade, a integração no manifesto e a exportação textual.
- `compileall` e `git diff --check` aprovados; nenhuma dependência de rede instalada.
- A suíte agregada da Rota 11 ficará para a esteira CI quando esta branch receber
  autorização de publicação, conforme diretriz do CTO no parecer AUTO-178.

## Critérios de aceitação

- Fórmulas e unidade µm são determinísticas e cobertas por casos nominais e extremos.
- A tag não presume conformidade quando não existe tolerância nominal declarada.
- O relatório identifica o modelo como cinemático ideal e exclui vibração, desgaste
  e efeitos de material.
- Permanecem fixos `PHYSICAL_USE_AUTHORIZED=FALSE`,
  `G9=PENDING_AUTHORITATIVE_REVIEW`, `NO_HUMAN_REVIEW_BYPASS=TRUE`,
  `MACHINE_SEND/DNC/NC_TRANSFER/CYCLE_START=false`,
  `emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximo passo

Enviar VTP-AUTO-188-BATCH ao CTO e aguardar parecer. A branch e o commit permanecem
locais, sem push.
