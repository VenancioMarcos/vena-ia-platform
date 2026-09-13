# CTO-CODEX-AUTO-141 a AUTO-145 — Hardening integrado e auditor estático CNC

## Objetivo

Publicar e integrar o hardening concorrente do CAD e iniciar a Rota 5 CNC com
auditoria estática fail-closed de candidatos G-code não executáveis.

## Escopo

- PR #52 criado em draft, validado pelo Backend CI e integrado por squash em
  `dd950938bf3e7bdb2a7447647964c8542b69b26c`.
- Auditor léxico/sintático limitado a Fanuc 0i, Siemens 840D e Haas, com relatório
  `VALID | REJECTED` e violações por linha.
- Validação mandatória do cabeçalho de governança, dos identificadores de programa,
  chamadas de ferramenta, valores F/S e conflitos de movimento G00/G01.

## Arquivos criados e modificados

- `apps/api/app/modules/cnc/services/syntax_linter.py`
- `apps/api/tests/unit/cnc/test_syntax_linter.py`
- `apps/api/app/modules/cnc/services/gcode_formatter.py`
- `apps/api/app/modules/cnc/services/__init__.py`
- registros CTO e `CONTEXT.md`.

## Testes realizados

- Testes CNC focados: 14 aprovados.
- Backend completo: `795 passed, 9 skipped`.
- TypeScript e Next lint: aprovados, sem avisos.
- Ruff, mypy (179 arquivos) e `git diff --check`: aprovados.

## Critérios de aceitação

O auditor não executa, aprova para máquina ou transmite programas. Qualquer erro
sintático ou ausência de governança resulta em `REJECTED`; o formatador também
chama o gate antes da validação cinemática. Permanecem `PHYSICAL_USE_AUTHORIZED=FALSE`,
`G9=PENDING_AUTHORITATIVE_REVIEW`, `MACHINE_SEND=FALSE`, `DNC=FALSE`,
`NC_TRANSFER=FALSE`, `CYCLE_START=FALSE`,
`emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximos passos

Consolidar o commit local e enviar VTP-AUTO-145-BATCH ao CTO, sem push da Rota 5.
