# Registro de Entrega — CTO-CODEX-AUTO-419-BATCH

**Data:** 2026-09-15
**Estado:** `CNC_BEARING_L10H_FATIGUE_LIFE_AUDITOR_COMPLETED_LOCAL`
**Branch:** `codex/v9.6-cnc-bearing-l10h-fatigue-life-auditor`
**Implementação:** commit atômico desta entrega
**Baseline:** `fbae22f0ce658b3d6dba26366ec6038ccf82196c`

## Objetivo

Publicar e integrar a Rota CNC 33 aprovada e implementar a Rota 34 para estimar a
vida nominal L10h dos rolamentos do fuso conforme ISO 281, mantendo o resultado
revisável e sem autoridade física.

## Escopo

- PR #82 publicado, aprovado pelo Frontend CI em 1m23s e Backend CI em 3m03s,
  promovido e integrado por squash em `fbae22f`; branch remota removida e main
  sincronizada.
- Carga dinâmica equivalente calculada por `P=X·Fr+Y·Fa`, com `Fr` derivada do
  snapshot Kienzle e `Fa` formada pela força axial mais a pré-carga declarada.
- Vida básica ISO 281 calculada por `(C/P)^p`, com `p=3` para esferas de contato
  angular e `p=10/3` para rolos cilíndricos ou cônicos.
- Viscosidade ajustada pela temperatura estimada da Rota 33, razão `kappa=nu/nu1`,
  fator conservador `aISO` e conversão da vida modificada em L10h.
- Integração no relatório JSON/TEXT e painel Web com carga, L10, L10h, `kappa`,
  conformidade ou warning e nota mandatória, sem controles de hardware.

## Arquivos criados

- `apps/api/app/modules/cnc/services/bearing_life_auditor.py`
- `apps/api/tests/unit/cnc/test_bearing_life_auditor.py`
- `docs/cto/CTO-CODEX-AUTO-419-BATCH.md`

## Arquivos modificados

- Contratos e relatório CNC: `schemas.py`, `machining_report.py` e
  `text_report_exporter.py`.
- Testes unitários e de integração do relatório/endpoint.
- Viewer e testes compilados do relatório técnico Web.
- `CONTEXT.md`, `CURRENT_ORDER.md`, `EXECUTION_STATUS.md` e `ORDER_HISTORY.md`.

## Testes realizados

- 411 testes CNC unitários e de integração aprovados.
- 48 testes Web do viewer compilados com `node:test` aprovados.
- Ruff, mypy em 240 fontes, TypeScript estrito, Next lint e `git diff --check`
  aprovados.

## Critérios de aceitação

- O contrato imutável recalcula cargas radial e axial, carga equivalente, expoente,
  viscosidade operacional, `kappa`, `aISO`, L10 e L10h; snapshots térmicos
  transplantados falham fechados.
- Os expoentes 3 e 10/3 possuem cenários determinísticos, e o regime contínuo de
  alta rotação abaixo de 5.000 h aciona `PREMATURE_BEARING_FATIGUE_WARNING`.
- Capacidade dinâmica ausente, nula ou não finita, RPM não física, fatores inválidos
  e geometria de origem corrompida são rejeitados.
- JSON, TEXT e Web exibem a telemetria e a nota técnica obrigatória, sem controles
  de lubrificação, rolamentos ou máquina.
- `PHYSICAL_USE_AUTHORIZED=FALSE`, G9 pendente e todas as capacidades de envio,
  transferência e início de ciclo continuam desabilitadas.

## Próximos passos

Solicitar parecer do CTO e aguardar a próxima ordem. A branch permanece local,
sem push neste lote.

VTP-AUTO-419-BATCH
Status: A
Resumo: PR #82 integrado e Rota CNC 34 concluída localmente com auditoria ISO 281
de vida L10h dos rolamentos do fuso em JSON, TEXT e Web.
Bloqueador: NÃO
Próxima: Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
