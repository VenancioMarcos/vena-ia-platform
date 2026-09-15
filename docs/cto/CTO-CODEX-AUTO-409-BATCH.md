# Registro de Entrega — CTO-CODEX-AUTO-409-BATCH

**Data:** 2026-09-14
**Estado:** `CNC_SPINDLE_BEARING_THERMAL_LOAD_AUDITOR_COMPLETED_LOCAL`
**Branch:** `codex/v9.5-cnc-spindle-bearing-thermal-load-auditor`
**Implementação:** commit atômico desta entrega
**Baseline:** `f26f20df585737cd789446024978d18fe9e8b592`

## Objetivo

Publicar e integrar a Rota CNC 32 aprovada e implementar a Rota 33 para estimar a
carga térmica nos rolamentos do fuso, mantendo o resultado revisável e sem
autoridade física.

## Escopo

- PR #81 publicado, aprovado pelo Frontend CI em 1m17s e Backend CI em 3m35s,
  promovido e integrado por squash em `f26f20d`; branch remota removida e main
  sincronizada.
- Torque de carga Palmgren calculado por `M_carga=f1·P1·dm`, com a carga
  equivalente derivada de `Fc`, `Ff`, `Fr` e da pré-carga interna declarada.
- Torque viscoso calculado nos regimes `ν·n >= 2000` e `ν·n < 2000`, com unidades
  convertidas explicitamente de N·mm para N·m.
- Calor calculado por `Q=(M_carga+M_viscoso)·ω` e temperatura estacionária por
  `20 °C + Q/(h·A)`, comparada ao limite térmico declarado.
- Integração no relatório JSON/TEXT e painel Web com torque total, calor,
  temperatura estimada, limite e nota mandatória, sem controles de refrigeração
  ou circulação.

## Arquivos criados

- `apps/api/app/modules/cnc/services/spindle_bearing_auditor.py`
- `apps/api/tests/unit/cnc/test_spindle_bearing_auditor.py`
- `docs/cto/CTO-CODEX-AUTO-409-BATCH.md`

## Arquivos modificados

- Contratos e relatório CNC: `schemas.py`, `machining_report.py` e
  `text_report_exporter.py`.
- Testes unitários e de integração do relatório/endpoint.
- Viewer e testes compilados do relatório técnico Web.
- `CONTEXT.md`, `CURRENT_ORDER.md`, `EXECUTION_STATUS.md` e `ORDER_HISTORY.md`.

## Testes realizados

- 395 testes CNC unitários e de integração aprovados.
- 46 testes Web do viewer compilados com `node:test` aprovados.
- Ruff, mypy em 239 fontes, TypeScript estrito, Next lint e `git diff --check`
  aprovados.

## Critérios de aceitação

- O contrato imutável recalcula carga equivalente, torques de carga e viscoso,
  torque total, calor, aumento de temperatura e status; snapshots das guias
  transplantados falham fechados.
- RPM não física ou fora do envelope, viscosidade nula/ausente, pré-carga
  ausente/negativa e área de dissipação inválida são rejeitadas.
- O regime contínuo próximo ao teto sem resfriamento forçado aciona
  `SPINDLE_BEARING_OVERHEATING_WARNING`.
- JSON, TEXT e Web exibem a telemetria e a nota técnica obrigatória, sem controles
  de circulação ou refrigeração.
- `PHYSICAL_USE_AUTHORIZED=FALSE`, G9 pendente e todas as capacidades de envio,
  transferência e início de ciclo continuam desabilitadas.

## Próximos passos

Solicitar parecer do CTO e aguardar a próxima ordem. A branch permanece local,
sem push neste lote.

VTP-AUTO-409-BATCH
Status: A
Resumo: PR #81 integrado e Rota CNC 33 concluída localmente com auditoria Palmgren
de carga térmica dos rolamentos do fuso em JSON, TEXT e Web.
Bloqueador: NÃO
Próxima: Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
