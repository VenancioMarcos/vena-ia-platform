# CTO-CODEX-AUTO-096 a AUTO-100 — Publicação CNC Rota 1 e gateway E2E

**Status:** `CNC_ROTA_2_E2E_GATEWAY_COMPLETED_LOCAL`
**Data:** 2026-09-13
**Branch:** `codex/v5.1-cnc-e2e-gateway`
**Baseline:** `136941809c1acf481f7f7c476664a15009476553`

## Objetivo

Publicar e integrar a fundação CNC da Rota 1 e criar o gateway autenticado que
transforma um plano CAM pertencente ao usuário em candidato ISO revisável, mantendo
todos os controles físicos e de emissão desativados.

## Execução do lote

| Ordem | Resultado |
| --- | --- |
| AUTO-096 | Branch Rota 1 publicada e Draft PR #43 aberto. |
| AUTO-097 | Backend CI aprovado em 3m26s; PR marcado Ready for Review, `MERGEABLE` e `CLEAN`. |
| AUTO-098 | PR #43 integrado em `1369418`; branch remota removida e `main` sincronizada. |
| AUTO-099 | Gateway CNC autenticado e armazenamento process-local owner-scoped implementados. |
| AUTO-100 | Integração, regressão e governança consolidadas localmente, sem push. |

## Escopo técnico

- O gateway CAM salva o plano e seus parâmetros de corte em um registro process-local
  associado ao usuário autenticado.
- `POST /api/v1/cnc/turning/generate` aceita `plan_id`, perfil allowlisted e número
  de programa.
- A consulta do plano é owner-scoped; ausência e acesso cruzado usam a mesma resposta
  404 para não revelar a existência do recurso.
- O contexto autenticado da rota autoriza somente a criação de candidato para revisão;
  G9, emissão, transmissão e uso físico continuam bloqueados.
- O contrato CAM estendido é normalizado explicitamente antes da revalidação estrita.
- Perfil inválido ou plano incompatível retorna 422; ausência de autenticação retorna
  401.

## Arquivos criados

- `apps/api/app/modules/cam/repository.py`
- `apps/api/app/modules/cnc/router.py`
- `apps/api/tests/integration/cnc/test_cnc_generation_router.py`
- `docs/cto/CTO-CODEX-AUTO-100-BATCH.md`

## Arquivos modificados

- `apps/api/app/main.py`
- `apps/api/app/modules/cam/router.py`
- `apps/api/app/modules/cnc/schemas.py`
- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Validação

- Testes focados CAM, CNC e gateway: 12 aprovados.
- Regressão Python: 766 aprovados, 9 ignorados.
- Web: 64 testes `node:test` aprovados.
- Ruff: aprovado.
- mypy: 208 arquivos sem problemas.
- `git diff --check`: aprovado.

## Critérios de aceitação

- Um plano CAM pertencente ao usuário produz resposta determinística e revisável.
- Requisições anônimas, acesso cruzado e controlador fora do allowlist falham
  fechados em 401, 404 e 422.
- O gateway não expõe operações de machine-send, DNC, transferência NC ou cycle
  start.
- Nenhuma dependência externa foi instalada e a branch Rota 2 não foi publicada.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

## Próxima etapa

Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
