# Registro de Entrega — CTO-CODEX-AUTO-389-BATCH

**Data:** 2026-09-14
**Estado:** `CNC_GUIDEWAY_CUTTING_MOMENT_LOAD_AUDITOR_COMPLETED_LOCAL`
**Branch:** `codex/v9.3-cnc-guideway-cutting-moment-load-auditor`
**Implementação:** commit atômico desta entrega
**Baseline:** `09d5df2f26f881fbb23d51d8e30e52a4e814129b`

## Objetivo

Publicar e integrar a Rota CNC 30 aprovada e implementar a Rota 31 para auditar
cargas diretas, momentos tombantes e carga equivalente nos patins dos guias
lineares do carro, mantendo o resultado revisável e sem autoridade física.

## Escopo

- PR #79 publicado, aprovado pelo Frontend CI em 1m10s e Backend CI em 3m42s,
  promovido e integrado por squash em `09d5df2`; branch remota removida e main
  sincronizada.
- Decomposição explícita da força Kienzle em força tangencial `Fc`, força axial de
  avanço `Ff` e força radial `Fr` por razões declaradas e revalidadas.
- Momentos de arfagem `My = Ff·Lz + Fc·Lx`, guinada
  `Mz = Ff·Ly + Fr·Lz` e rolamento `Mx = Fr·Ly + Fc·Lz`.
- Carga máxima conservadora por patim calculada pela soma da carga vetorial direta
  distribuída entre quatro blocos e das reações dos três momentos em seus vãos.
- Gate em `0,5 × C0`, com estados `GUIDEWAY_LOAD_COMPLIANT` e
  `GUIDEWAY_DYNAMIC_OVERLOAD_WARNING` e falha fechada para forças, geometrias ou
  capacidade inválidas.
- Integração no relatório JSON/TEXT e painel Web com `Mx`, `My`, `Mz`, carga máxima,
  capacidade, razão de carga e a nota mandatória, sem controles de hardware.

## Arquivos criados

- `apps/api/app/modules/cnc/services/guideway_load_auditor.py`
- `apps/api/tests/unit/cnc/test_guideway_load_auditor.py`
- `docs/cto/CTO-CODEX-AUTO-389-BATCH.md`

## Arquivos modificados

- Contratos e relatório CNC: `schemas.py`, `machining_report.py` e
  `text_report_exporter.py`.
- Testes unitários e de integração do relatório/endpoint.
- Viewer e testes compilados do relatório técnico Web.
- `CONTEXT.md`, `CURRENT_ORDER.md`, `EXECUTION_STATUS.md` e `ORDER_HISTORY.md`.

## Testes realizados

- 363 testes CNC unitários e de integração aprovados.
- 42 testes Web compilados com `node:test` aprovados.
- Ruff, mypy em 237 fontes, TypeScript estrito, Next lint e `git diff --check`
  aprovados.

## Critérios de aceitação

- O contrato imutável recalcula componentes de força, momentos, reações, carga
  máxima, razão e status; snapshots Kienzle transplantados falham fechados.
- Distâncias nulas ou negativas, `C0` ausente/inválido e forças fora do envelope
  físico são rejeitados.
- JSON, TEXT e Web exibem os três momentos, a carga por patim, a capacidade e a
  razão de carga com os badges mandatórios.
- A nota técnica obrigatória está visível e não existem controles de atuadores.
- `PHYSICAL_USE_AUTHORIZED=FALSE`, G9 pendente e todas as capacidades de envio,
  transferência e início de ciclo continuam desabilitadas.

## Próximos passos

Solicitar parecer do CTO e aguardar a próxima ordem. A branch permanece local,
sem push neste lote.

VTP-AUTO-389-BATCH
Status: A
Resumo: PR #79 integrado e Rota CNC 31 concluída localmente com auditoria de
momentos e carga por patim em JSON, TEXT e Web.
Bloqueador: NÃO
Próxima: Solicitar parecer do CTO e aguardar a próxima ordem sem encerrar a execução.
