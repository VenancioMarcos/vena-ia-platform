# CTO-CODEX-AUTO-136 a AUTO-140 — release oficial e hardening de concorrência CAD

**Data:** 2026-09-13

**Estado:** `CAD_E2E_CONCURRENCY_HARDENING_COMPLETED_LOCAL`

**Branch:** `codex/v6.5-test-concurrency-hardening`

**Baseline:** `1857018acea48238d835869eb115b8b84a83733f`

## Resultado consolidado

| Ordem | Resultado |
|---|---|
| AUTO-136 | Branch documental publicada e Draft PR #51 aberto. |
| AUTO-137 | PR #51 sem checks aplicáveis por ser documental; confirmado `OPEN`, `isDraft=false`, `MERGEABLE` e `CLEAN`. |
| AUTO-138 | PR #51 integrado por squash em `1857018`; tag oficial `v0.3.0-sim-rc1` publicada e `main` alinhada. |
| AUTO-139 | O E2E CAD substituiu a autenticação SQLite compartilhada por identidades UUID e clientes por worker no cenário concorrente. |
| AUTO-140 | Cinco repetições concorrentes e a suíte agregada foram aprovadas sem flutuação. |

## Diagnóstico e correção

O endpoint e o gateway não tinham falha funcional. A instabilidade era causada por
quatro workers concorrentes passando pela fixture global SQLite em memória durante
a autenticação. O teste de gateway agora usa identidades UUID por requisição via
override local de `get_current_user`, preserva a verificação owner-scoped e isola o
`TestClient` de cada worker. Os testes de autenticação permanecem cobertos nas
suítes próprias.

## Validação

- Teste E2E concorrente repetido cinco vezes: aprovado.
- `pytest`: `791 passed, 9 skipped`.
- Web `node:test`: `73 passed, 0 failed`.
- TypeScript e Next lint: aprovados, sem warnings.
- Ruff check e mypy: aprovados; mypy em 210 arquivos.
- `git diff --check`: aprovado.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
Nenhuma comunicação física, deploy ou push da branch de hardening foi executado.
