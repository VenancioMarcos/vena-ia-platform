# Registro de Entrega — VTP-AUTO-218-BATCH

**Status:** A
**Data:** 2026-09-13
**Branch:** `codex/v7.5-cnc-cycle-time-cost-estimator`
**Baseline:** `a8a07cfa01b0cba5b5b594cc561ec642bddb7c4f`

## Objetivo

Publicar e integrar a auditoria Taylor da Rota 13 e implementar uma estimativa
analítica e multicritério de tempo e custo de usinagem.

## Escopo

- Draft PR #61, CI remoto, transição para Ready, squash merge e sincronização da main.
- Soma de corte, rápido, trocas de ferramenta e setups nominais.
- Custo de máquina por tempo total e desgaste proporcional de aresta pela vida Taylor.
- Perfis tabulados BRL e USD, com validação fail-closed de tempos, custos e divisores.
- Contrato Pydantic imutável, com validação dos subtotais e vínculos do manifesto.
- Integração no relatório JSON, exportador textual e visualizador Web.

## Arquivos Criados

- `apps/api/app/modules/cnc/services/cost_time_estimator.py`
- `apps/api/tests/unit/cnc/test_cost_time_estimator.py`
- `docs/cto/CTO-CODEX-AUTO-218-BATCH.md`

## Arquivos Modificados

- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/machining_report.py`
- `apps/api/app/modules/cnc/services/text_report_exporter.py`
- `apps/api/tests/unit/cnc/test_machining_report.py`
- `apps/web/src/components/cnc/MachiningTechnicalReportViewer.tsx`
- `apps/web/tests/machining-technical-report-viewer.test.ts`
- `CONTEXT.md` e registros em `docs/cto/`.

## Testes Realizados

- 109 testes Python do domínio CNC: aprovados; 29 testes focados de custo/relatório.
- 10 testes Web sob compilação TypeScript estrita: aprovados.
- Ruff sobre API e testes CNC, mypy em 201 fontes e `git diff --check`: aprovados.
- Nenhuma dependência externa de rede instalada.

## Critérios de Aceitação

- O tempo total soma corte, rápido, trocas e setup, inclusive em cenários múltiplos.
- O custo total soma taxa de máquina e desgaste Taylor de cada ferramenta.
- Tempos/custos negativos, perfil ausente e vida inválida falham fechados.
- O manifesto rejeita custo transplantado de outro ciclo ou conjunto de ferramentas.
- JSON, laudo e viewer exibem subtotais e a limitação econômica obrigatória.
- `PHYSICAL_USE_AUTHORIZED=FALSE`, `G9=PENDING_AUTHORITATIVE_REVIEW`,
  `NO_HUMAN_REVIEW_BYPASS=TRUE`, `MACHINE_SEND/DNC/NC_TRANSFER/CYCLE_START=false`,
  `emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximos Passos

Enviar `VTP-AUTO-218-BATCH` ao CTO e aguardar parecer e próxima ordem. A branch
permanece local, sem push.
