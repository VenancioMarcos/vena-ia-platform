# CTO-CODEX-AUTO-062 — Hardening e resiliência do pipeline CAD

**Status:** `ROTA_5_CAD_HARDENING_PR_OPEN_AWAITING_CI_AND_REVIEW`
**Data:** 2026-09-12  
**Branch:** `codex/v3.5-cad-hardening-resilience`  
**Baseline:** `e8774a7ccbd7517e7cf08c906b7ffcbbb5bdb954`

## Objetivo e escopo

Abrir a primeira etapa da Rota 5 com validação conservadora do perfil RZ extraído,
avisos estruturados para tolerâncias aceitáveis e feedback defensivo na interface.
O escopo não inclui CAM, G-code, pós-processamento, transmissão ou operação física.

## Implementação

- O processador STEP rejeita pontos inválidos, segmentos degenerados, perfis abertos
  acima de 0,05 mm, auto-interseções e envelopes acima de 5.000 mm de raio ou
  10.000 mm de extensão axial.
- Perfis cujo fechamento possui folga positiva de até 0,05 mm permanecem sujeitos a
  revisão e recebem `PROFILE_CLOSURE_GAP_WITHIN_TOLERANCE`.
- Contornos que começam e terminam no eixo R=0 mantêm o fechamento axial implícito
  usado pela extração vigente.
- Falhas geométricas conhecidas retornam códigos sanitizados e estáveis no job; erros
  internos continuam ocultos por `STEP_PROFILE_EXTRACTION_FAILED`.
- O contrato `CadProfileData` expõe `warnings`; o cliente valida o vetor antes de
  renderizá-lo e o card apresenta cada aviso com revisão obrigatória.

## Arquivos criados ou modificados

- `apps/api/app/modules/cad/services/step_processor.py`
- `apps/api/app/modules/cad/ingestion_schemas.py`
- `apps/api/tests/unit/test_step_processor_geometry.py`
- `apps/api/tests/api/test_cad_gateway.py`
- `apps/web/lib/cad-dispatch-service.ts`
- `apps/web/components/cam/TurningViewerContainer.tsx`
- `apps/web/components/cam/StepMetadataCard.tsx`
- `apps/web/tests/cad-dispatch-service.test.ts`
- `apps/web/tests/step-metadata-card.test.ts`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `CONTEXT.md`

## Critérios de aceitação

- Perfis degenerados, abertos, auto-intersectantes ou fora do envelope falham fechado.
- Pequenas folgas de fechamento geram aviso sem remover a revisão obrigatória.
- A UI apresenta avisos aceitos pela validação estrita do contrato.
- As suítes completas e verificações estáticas permanecem verdes.

## Validação executada

- Backend: 738 testes aprovados e 9 ignorados.
- Web: 64 testes `node:test` aprovados.
- TypeScript e Next lint: aprovados, sem erros ou avisos de regras.
- Ruff e mypy: aprovados; 165 arquivos tipados sem problemas.
- `git diff --check`: aprovado.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.

## Continuidade

O commit funcional `db78731` foi aprovado pelo CTO. AUTO-063 consolida a
documentação, publica a branch e abre o PR, sem merge.
