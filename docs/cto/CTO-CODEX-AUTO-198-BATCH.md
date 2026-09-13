# Registro de Entrega — VTP-AUTO-198-BATCH

**Status:** A
**Data:** 2026-09-13
**Branch:** `codex/v7.3-cnc-cutting-power-force-estimator`
**Baseline:** `db1ff2edbfa2716451034eef12696b3ad91f3dc1`

## Objetivo

Publicar e integrar a auditoria de rugosidade da Rota 11 e implementar uma auditoria
energética analítica de torneamento baseada no modelo clássico de Kienzle.

## Escopo

- Draft PR #59, CI remoto, transição para Ready, squash merge e sincronização da main.
- Parâmetros tabulados para AISI 1020, ABNT 1045 e Alumínio 6061-T6.
- Cálculo de Fc, Pc, potência estimada do motor com rendimento 0,80 e MRR.
- Validação fail-closed de material, avanço, profundidade, ângulo, rotação e limites.
- Contrato Pydantic imutável com validação contra valores e status adulterados.
- Integração no manifesto, exportador textual e visualizador Web.

## Arquivos Criados

- `apps/api/app/modules/cnc/services/power_force_estimator.py`
- `apps/api/tests/unit/cnc/test_power_force_estimator.py`
- `docs/cto/CTO-CODEX-AUTO-198-BATCH.md`

## Arquivos Modificados

- `apps/api/app/modules/cam/schemas.py`
- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/machining_report.py`
- `apps/api/app/modules/cnc/services/text_report_exporter.py`
- `apps/api/tests/unit/cnc/test_machining_report.py`
- `apps/web/src/components/cnc/MachiningTechnicalReportViewer.tsx`
- `apps/web/tests/machining-technical-report-viewer.test.ts`
- `CONTEXT.md` e registros em `docs/cto/`.

## Testes Realizados

- 103 testes Python do domínio CNC, incluindo unidade e integração: aprovados.
- 7 testes Web compilados sob TypeScript estrito: aprovados.
- Ruff e mypy completos em 218 fontes, compilação TypeScript estrita e
  `git diff --check`: aprovados.
- O lint focado não foi repetido: a chamada Docker foi bloqueada porque o revisor
  automático de execução atingiu seu limite de uso; não houve diagnóstico de código.
- Nenhuma dependência externa de rede instalada.

## Critérios de Aceitação

- Equações de Kienzle, potência e MRR são determinísticas e verificadas.
- Entradas não físicas, rotação acima do limite e material não tabulado falham fechadas.
- O alerta usa o limite de potência configurável do perfil de máquina.
- Manifesto, laudo e viewer exibem as grandezas e a limitação obrigatória.
- `PHYSICAL_USE_AUTHORIZED=FALSE`, `G9=PENDING_AUTHORITATIVE_REVIEW`,
  `NO_HUMAN_REVIEW_BYPASS=TRUE`, `MACHINE_SEND/DNC/NC_TRANSFER/CYCLE_START=false`,
  `emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximos Passos

Enviar `VTP-AUTO-198-BATCH` ao CTO e aguardar parecer e próxima ordem. A branch
permanece local, sem push.
