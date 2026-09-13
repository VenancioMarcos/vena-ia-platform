# CTO-CODEX-AUTO-146 — Publicação e Pull Request da Rota CNC 5

## Objetivo

Publicar a auditoria estática de sintaxe G-code e abrir o Pull Request #53 contra
`main`, mantendo o artefato exclusivamente não executável.

## Escopo

- Publicar `codex/v6.6-cnc-gcode-syntax-linter`, que parte de `dd950938`.
- Abrir o Draft PR da Rota CNC 5 e acompanhar o CI remoto antes de qualquer merge.

## Arquivos Criados

- Este registro de missão.

## Arquivos Modificados

- `CONTEXT.md` e os registros em `docs/cto/`.

## Testes Realizados

- Validação local previamente homologada: 795 Python aprovados e 9 ignorados;
  TypeScript, Next lint, Ruff, mypy e `git diff --check` aprovados.

## Critérios de Aceitação

O PR preserva `PHYSICAL_USE_AUTHORIZED=FALSE`,
`G9=PENDING_AUTHORITATIVE_REVIEW`, `MACHINE_SEND=FALSE`, `DNC=FALSE`,
`NC_TRANSFER=FALSE`, `CYCLE_START=FALSE`,
`emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximos Passos

Publicar a branch, abrir o Draft PR #53 e aguardar a conclusão do CI antes de
promover o PR para revisão.
