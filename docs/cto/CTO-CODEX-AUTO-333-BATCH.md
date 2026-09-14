# Registro de Entrega — CTO-CODEX-AUTO-324 a AUTO-333

**Data:** 2026-09-14
**Estado:** `CNC_COOLANT_PRESSURE_FLOW_CONTRACT_V2_SCAFFOLDED_LOCAL`
**Branch:** `codex/v8.7-cnc-coolant-pressure-flow-auditor`
**Baseline:** `abbbcad44964553aa474760910b7afc551e1da88`

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

## Publicação, CI e integração da Rota 25

- Commit funcional `28b1d6c` e correção de cobertura `ed51c08`.
- Draft PR #73 promovido após Frontend CI em 1m24s e Backend CI em 3m47s.
- Estado pré-merge confirmado: `OPEN`, `isDraft=false`, `MERGEABLE/CLEAN`.
- Squash merge concluído em `abbbcad44964553aa474760910b7afc551e1da88`.
- Branch remota removida e `main=origin/main`.

## Inicialização da Rota 26

O contrato `vena-ia.cnc-coolant-pressure-flow-audit/v2` registra modo Flood ou
MQL, vazão e pressão programadas, requisitos mínimos nas zonas primária,
ferramenta-cavaco e ferramenta-peça, margens e status de dissipação térmica.
As tabelas são imutáveis por contrato e qualquer duplicata, adulteração,
valor não finito ou promoção de controle automático falha fechado.

Validação da Rota 26: 270 testes CNC, 12 focados, Ruff, mypy em 231 fontes e
`git diff --check`.

## Limites e continuidade

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Emitir `VTP-AUTO-333-BATCH`, solicitar parecer do CTO e aguardar a próxima
ordem sem encerrar a execução. A Rota 26 permanece local sem push.
