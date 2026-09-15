# Registro de Entrega — CTO-CODEX-AUTO-399-BATCH

**Data:** 2026-09-14
**Estado:** `CNC_BALLSCREW_AXIAL_THRUST_BUCKLING_AUDITOR_COMPLETED_LOCAL`
**Branch:** `codex/v9.4-cnc-ballscrew-axial-thrust-buckling-auditor`
**Implementação:** commit atômico desta entrega
**Baseline:** `81b5fad62b7ff60f3b0b6454fa6fae76c70ee573`

## Objetivo

Publicar e integrar a Rota CNC 31 aprovada e implementar a Rota 32 para auditar o
empuxo axial, a flambagem e a velocidade crítica do fuso de esferas do avanço,
mantendo o resultado revisável e sem autoridade física.

## Escopo

- PR #80 publicado, aprovado pelo Frontend CI em 1m18s e Backend CI em 3m42s,
  promovido e integrado por squash em `81b5fad`; branch remota removida e main
  sincronizada.
- Empuxo axial total calculado por
  `Ff + μ_guias·(m_carro·g + Fr) + m_carro·a`, usando as forças revalidadas da
  auditoria das guias.
- Limite de flambagem calculado pela equação de Euler com
  `I = π·d_raiz⁴/64`, módulo elástico, comprimento e fator de montagem declarados.
- Velocidade crítica derivada do diâmetro de raiz, comprimento e fator de montagem;
  rotação operacional derivada do avanço axial e do passo do fuso.
- Gates determinísticos em 50% do limite de Euler e 80% da RPM crítica, com
  precedência para o risco de flambagem.
- Integração no relatório JSON/TEXT e painel Web com empuxo, limite, RPM operacional
  e crítica, razões e nota mandatória, sem controles de servo ou hardware.

## Arquivos criados

- `apps/api/app/modules/cnc/services/ballscrew_auditor.py`
- `apps/api/tests/unit/cnc/test_ballscrew_auditor.py`
- `docs/cto/CTO-CODEX-AUTO-399-BATCH.md`

## Arquivos modificados

- Contratos e relatório CNC: `schemas.py`, `machining_report.py` e
  `text_report_exporter.py`.
- Testes unitários e de integração do relatório/endpoint.
- Viewer e testes compilados do relatório técnico Web.
- `CONTEXT.md`, `CURRENT_ORDER.md`, `EXECUTION_STATUS.md` e `ORDER_HISTORY.md`.

## Testes realizados

- 377 testes CNC unitários e de integração aprovados.
- 44 testes Web compilados com `node:test` aprovados.
- Ruff, mypy em 238 fontes, TypeScript estrito, Next lint e `git diff --check`
  aprovados.

## Critérios de aceitação

- O contrato imutável recalcula empuxo, inércia, limite de Euler, RPM crítica,
  rotação operacional, razões e status; snapshots das guias transplantados falham
  fechados.
- Diâmetro de raiz nulo/negativo, comprimento inválido e fatores de montagem
  ausentes ou inválidos são rejeitados.
- Corte pesado/interrompido e G00 extrapolado acionam os warnings correspondentes.
- JSON, TEXT e Web exibem a telemetria e a nota técnica obrigatória, sem controles
  de servo motor.
- `PHYSICAL_USE_AUTHORIZED=FALSE`, G9 pendente e todas as capacidades de envio,
  transferência e início de ciclo continuam desabilitadas.

## Próximos passos

Solicitar parecer do CTO e aguardar a próxima ordem. A branch permanece local,
sem push neste lote.

VTP-AUTO-399-BATCH
Status: A
Resumo: PR #80 integrado e Rota CNC 32 concluída localmente com auditoria de
empuxo axial, flambagem e velocidade crítica do fuso em JSON, TEXT e Web.
Bloqueador: NÃO
Próxima: Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
