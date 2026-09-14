# Registro de Entrega — CTO-CODEX-AUTO-324 a AUTO-333

**Data:** 2026-09-14
**Estado intermediário:** `CNC_CHIP_BREAKING_MACHINABILITY_AUDITOR_COMPLETED_LOCAL`
**Branch:** `codex/v8.6-cnc-chip-breaking-machinability-auditor`
**Baseline:** `294440258265c8b06afcbce49c426814293c7a85`

## Objetivo e escopo entregue nas ordens 324–329

A Rota 25 implementa o auditor determinístico de formação e quebra de cavaco.
O serviço deriva `h=f·sin(kr)`, `b=ap/sin(kr)`, razão de compressão por
material/ângulo de saída, espessura formada e comprimento livre. O ponto
operacional é comparado aos envelopes tabulados imutáveis PM, PR e PF.

O contrato Pydantic v2 recalcula todas as grandezas, recusa parâmetros não
finitos, nulos ou negativos, geometria desconhecida, tabela adulterada e
snapshots transplantados. O manifesto `vena-ia.cnc-machining-report/v1`, o
laudo TEXT e o visualizador Web incluem o painel, limites, badges e a nota:
“ESTIMATIVA ANALÍTICA DE FORMAÇÃO E QUEBRA DE CAVACO - NÃO CONSIDERA
FLUTUAÇÕES DINÂMICAS DE PRESSÃO DE REFRIGERAÇÃO OU VARIAÇÕES
MICROESTRUTURAIS”.

## Arquivos criados e modificados

- Criados: `apps/api/app/modules/cnc/services/chip_breaking_auditor.py` e este
  registro.
- Modificados: contratos CNC, compilador de relatório, exportador TEXT, testes
  API, viewer Web e testes Web.
- Atualizados: `CONTEXT.md`, `docs/cto/CURRENT_ORDER.md`,
  `docs/cto/EXECUTION_STATUS.md` e `docs/cto/ORDER_HISTORY.md`.

## Testes e critérios de aceitação

- 258 testes CNC e 53 testes focados aprovados.
- 30 testes compilados do visualizador Web aprovados.
- Ruff, mypy em 231 fontes, TypeScript, Next lint e `git diff --check`
  aprovados.
- Nenhuma dependência externa de rede foi instalada.

## Limites e continuidade

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Próxima etapa: publicar a branch, abrir o PR #73, validar CI, integrar por
squash e iniciar a Rota 26 sem push.
