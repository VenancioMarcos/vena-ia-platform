# CTO-CODEX-AUTO-075 — Fundação canônica de estratégias CAM

**Status:** `CAM_ROTA_1_STRATEGY_FOUNDATION_PR_OPEN_AWAITING_CI_AND_REVIEW`
**Data:** 2026-09-12
**Branch:** `codex/v4.0-cam-turning-strategies-foundation`
**Baseline:** `3f2b19877c528cab0d080fcb1bc0756f4bef7390`
**Commit funcional:** `92d3651`

## Objetivo

Criar o domínio canônico CAM e a primeira fundação matemática determinística para
estratégias 2D de torneamento, limitada a faceamento e desbaste analíticos sujeitos
a revisão, sem G-code, pós-processador, conexão de máquina ou autoridade física.

## Escopo

- Enums canônicos para `FACING`, `ROUGH_TURNING`, `FINISHING` e `GROOVING`, além
  de orientação de ferramenta e compensação.
- Contratos Pydantic v2 estritos e imutáveis para ferramenta, parâmetros de corte,
  pontos RZ, bounding box, passes, requisição e resposta.
- Planejamento determinístico de faceamento entre o plano inicial do estoque e o
  plano alvo, decomposto pela profundidade máxima de corte.
- Desbaste longitudinal para perfis externos axissimétricos com spans axiais
  contínuos e acesso frontal, incluindo os raios de degrau como níveis obrigatórios.
- Cálculo analítico do volume removido por passe e total validado no contrato.
- Falha fechada para perfil fora do bounding box, envelope inconsistente, spans
  incompletos, abordagem traseira não suportada, excesso de passes e operações
  `FINISHING`/`GROOVING`, que permanecem não implementadas.
- Resposta fixa em `PLANNED_REQUIRES_REVIEW`, com `executable_output=false`,
  `physical_use_authorized=false`, G9 pendente e perfil de controlador não resolvido.

## Arquivos criados

- `apps/api/app/modules/cam/__init__.py`
- `apps/api/app/modules/cam/enums.py`
- `apps/api/app/modules/cam/schemas.py`
- `apps/api/app/modules/cam/services/__init__.py`
- `apps/api/app/modules/cam/services/strategy_engine.py`
- `apps/api/tests/unit/cam/test_turning_strategy_engine.py`
- `docs/cto/CTO-CODEX-AUTO-075.md`

## Arquivos modificados

- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Testes realizados

- Teste focado CAM: 9 aprovados.
- Regressão Python integral: 749 aprovados, 9 ignorados.
- Regressão da API: 680 aprovados, 2 ignorados.
- Web: 64 testes `node:test` aprovados; TypeScript e Next lint aprovados.
- Ruff: aprovado.
- mypy: 202 arquivos sem problemas.
- `git diff --check`: aprovado.

## Critérios de aceitação

- Desbaste linear válido gera níveis determinísticos limitados por `ap`.
- Faceamento respeita o intervalo entre `Z_stock` e `Z_target`.
- `ap <= 0`, `f <= 0`, perfis inconsistentes e operações ainda não implementadas
  falham fechado.
- Contratos rejeitam coerção e tentativa de forjar autorização física.
- Nenhum arquivo de frontend, dependência, trajetória executável ou emissão foi
  incorporado ao commit funcional.

## Próximos passos

AUTO-075 foi aprovada pelo CTO. A AUTO-076 publica a branch, abre Draft PR contra
`main`, coleta o CI inicial e retorna ao CTO sem executar merge.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.
