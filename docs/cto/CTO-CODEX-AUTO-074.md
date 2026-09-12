# CTO-CODEX-AUTO-074 — Preparação do épico CAM

**Status:** `CAM_EPIC_PREPARATION_IN_PROGRESS`
**Data:** 2026-09-12
**Branch:** `codex/auto-074-cam-epic-preparation`
**Baseline CAD:** `v0.7.0-cad` → `a6babbde437e5547e00ba83038218d7d69178023`
**Main sincronizada:** `3f2b19877c528cab0d080fcb1bc0756f4bef7390`

## Objetivo

Preservar no upstream o fechamento documental da baseline CAD e mapear as
interfaces já existentes entre o perfil analítico RZ e um futuro domínio CAM,
sem implementar estratégia, trajetória, pós-processamento ou autoridade física.

## Escopo executado

- A `main` recebeu por fast-forward o fechamento documental `3f2b198` e foi
  publicada em `origin/main`.
- A tag anotada remota `v0.7.0-cad` permaneceu vinculada à baseline de produto
  `a6babbd`; o commit posterior altera somente governança.
- A estrutura do backend, do frontend e a fundação sintética de torneamento foram
  inspecionadas. Não existe diretório `apps/api/app/modules/cam/` no baseline.
- Nenhum arquivo funcional em `apps/api` ou `apps/web` foi alterado.

## Mapa das interfaces existentes

| Camada | Interface atual | Papel na futura fronteira CAM |
| --- | --- | --- |
| Ingestão API | `POST /api/v1/cad/step/dispatch` e `GET /api/v1/cad/step/jobs/{job_id}` em `apps/api/app/modules/cad/api/routes.py` | Produz um job autenticado e isolado por proprietário; CAM deve consumir apenas resultado concluído e autorizado para revisão. |
| Contrato CAD | `CadProfileData` em `apps/api/app/modules/cad/ingestion_schemas.py` | Entrega pontos `{r_mm, z_mm}`, bounding box, warnings e `PROFILE_AVAILABLE_REQUIRES_REVIEW`; não contém estoque, material, setup, ferramenta ou aprovação. |
| Processamento | `StepBackgroundProcessor` em `apps/api/app/modules/cad/services/step_processor.py` | Extrai e valida o perfil, falha fechado e remove o arquivo temporário; é a origem analítica, não um planejador CAM. |
| Geometria comum | `TurningProfile2D` em `apps/api/app/modules/engineering/turning_schemas.py` | Tipo interno reutilizado pelo extrator. Uma futura entrada CAM deve versionar proveniência e manter o gate de revisão. |
| Fundação sintética | `turning_planner.py`, `turning_service.py` e `turning_toolpath_schemas.py` | Há protótipos locais de `FACING` e `ROUGH_TURNING`, com verificação limitada. Eles não estão conectados ao job autenticado e declaram `executable_output=false`, `physical_use_authorized=false` e colisão não validada. |
| Cliente web | `apps/web/lib/cad-dispatch-service.ts` | Normaliza defensivamente o contrato RZ concluído, preserva warnings e rejeita payload inconsistente. |
| UI | `TurningViewerContainer.tsx` e `TurningProfile2D.tsx` em `apps/web/components/cam/` | Mantém o perfil processado em estado local e o renderiza para revisão. Ainda não existe seleção ou execução de estratégia CAM. |
| Rota | `apps/web/app/cam/turning/page.tsx` | Sandbox visual `NON_PRODUCTION`; ponto natural para uma futura interface declarativa, após contratos e ADR próprios. |

## Lacunas antes de estratégias de usinagem

1. Criar um módulo CAM explícito e um contrato versionado que referencie job,
   proprietário, perfil, unidade, datum, digest/proveniência, warnings e decisão
   humana de revisão sem copiar autoridade do cliente.
2. Definir entradas separadas para estoque, material, setup, fixação, ferramenta,
   tolerâncias e parâmetros. Nenhum desses dados pode ser inferido do perfil RZ.
3. Separar tipos de operação. A fundação atual cobre somente faceamento e desbaste
   sintéticos; acabamento e canais não possuem implementação CAM homologada.
4. Definir estados fail-closed para perfil não revisado, input ausente, conflito de
   ownership, planejamento inválido e verificação não executada.
5. Manter planejamento, verificação, pós-processamento e autorização física como
   gates distintos. Resultado CAM futuro continua não executável enquanto G9,
   controlador, colisão real e autorização humana não forem resolvidos.

## Arquivos criados

- `docs/cto/CTO-CODEX-AUTO-074.md`

## Arquivos modificados

- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Testes realizados

- Inspeção estática das rotas, schemas, processador, contratos de torneamento e UI.
- `git diff --check`.
- Verificação de alinhamento `main == origin/main == 3f2b198` antes da branch local.
- Verificação da tag anotada local e remota `v0.7.0-cad` sobre `a6babbd`.

## Critérios de aceitação

- Fechamento documental preservado no upstream.
- Pontos de integração e lacunas CAM documentados sem código funcional.
- Limites permanentes mantidos.

## Próximos passos

Submeter o VTP-AUTO-074 ao CTO e aguardar uma ordem delimitada para contratos do
épico CAM, sem iniciar implementação por inferência.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.
