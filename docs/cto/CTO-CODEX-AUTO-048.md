# CTO-CODEX-AUTO-048 — Despacho assíncrono STEP cliente

## Objetivo

Abrir a Etapa 2 da Rota 2 com contratos e serviço cliente para despacho e consulta
de jobs STEP, sem integrar interface, backend ou operação física.

## Escopo

- DTOs tipados de payload e estado do job.
- `FormData` com arquivo, nome e schema STEP.
- Envio e consulta com transporte injetável, timeout abortável e falha estruturada.
- Testes determinísticos sem chamadas reais de rede.

## Validação

- 55 testes web aprovados.
- TypeScript e Next lint aprovados, com zero erros e zero avisos.
- 727 testes Python aprovados e 9 ignorados.
- Ruff e `git diff --check` aprovados.

## Limites

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.
