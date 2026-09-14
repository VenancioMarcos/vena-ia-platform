# Registro de Entrega — CTO-CODEX-AUTO-334 a AUTO-338

**Data:** 2026-09-14
**Estado:** `CNC_COOLANT_PRESSURE_FLOW_WEB_HUD_COMPLETED_LOCAL`
**Branch:** `codex/v8.8-cnc-coolant-web-hud`
**Baseline:** `979ed4e913495d0e0173027f35d6e29735050a01`

## Objetivo e escopo

Publicar o contrato v2 da Rota 26 e integrar a auditoria analítica de pressão e
vazão de fluido ao relatório técnico e ao HUD Web. A entrega consome os requisitos
imutáveis de FLOOD/MQL nas zonas primária, ferramenta-cavaco e ferramenta-peça,
calcula margens contra os máximos requeridos e preserva o alerta fail-closed de
dissipação térmica insuficiente.

## Publicação e integração

- Draft PR #74: https://github.com/VenancioMarcos/vena-ia-platform/pull/74
- Backend CI aprovado em 3m42s.
- Estado pré-merge: `OPEN`, `isDraft=false`, `MERGEABLE/CLEAN`.
- Squash merge: `979ed4e913495d0e0173027f35d6e29735050a01`.
- Branch remota removida e `main=origin/main`.

## Implementação local

- Serviço determinístico para construir o snapshot FLOOD/MQL.
- Inclusão do payload no relatório JSON e validação das flags de segurança.
- Nova seção no laudo TEXT com as três zonas, vazão, pressão, margens e status.
- Tabela Web tipada por zona térmica, métricas programadas e badges
  `DISSIPAÇÃO TÉRMICA ADEQUADA` e
  `ALERTA: INSUFFICIENT_THERMAL_DISSIPATION_WARNING`.
- Nota obrigatória: “ESTIMATIVA ANALÍTICA DE DEMANDA DE FLUIDO - NÃO CONTROLA
  BOMBAS OU VÁLVULAS DE MÁQUINA”.

## Arquivos criados e modificados

- Criados: `apps/api/app/modules/cnc/services/coolant_pressure_flow_auditor.py`
  e este registro.
- Modificados: contratos CNC, compilador e exportador do relatório, testes API,
  viewer Web e testes Web.
- Atualizados: `CONTEXT.md`, `docs/cto/CURRENT_ORDER.md`,
  `docs/cto/EXECUTION_STATUS.md` e `docs/cto/ORDER_HISTORY.md`.

## Testes e critérios de aceitação

- 287 testes CNC aprovados.
- 32 testes compilados do visualizador Web aprovados.
- Ruff, mypy em 232 fontes, TypeScript e Next lint aprovados.
- `git diff --check` aprovado.
- Nenhuma dependência externa instalada.

## Limites e continuidade

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Emitir `VTP-AUTO-338-BATCH`, solicitar parecer do CTO e aguardar a próxima
ordem. A branch permanece local sem push.
