# Registro de Entrega — VTP-AUTO-208-BATCH

**Status:** A
**Data:** 2026-09-13
**Branch:** `codex/v7.4-cnc-tool-life-taylor-estimator`
**Baseline:** `bc7a58237236482dd3aff23d1b0c239a8ac74cb5`

## Objetivo

Publicar e integrar a auditoria energética Kienzle da Rota 12 e implementar uma
estimativa analítica de vida útil de ferramenta baseada na equação de Taylor.

## Escopo

- Draft PR #60, CI remoto, transição para Ready, squash merge e sincronização da main.
- Perfis Taylor tabulados para metal duro em aço carbono e Alumínio 6061-T6.
- Cálculo `Vc * T^n = C`, vida estimada e consumo pelo tempo efetivo por ferramenta.
- Validação fail-closed de ferramenta, material, velocidade, tempo e coeficientes.
- Contrato Pydantic imutável, com detecção de parâmetros, resultados e status adulterados.
- Integração no relatório JSON, exportador textual e visualizador Web com progresso.

## Arquivos Criados

- `apps/api/app/modules/cnc/services/tool_life_estimator.py`
- `apps/api/tests/unit/cnc/test_tool_life_estimator.py`
- `docs/cto/CTO-CODEX-AUTO-208-BATCH.md`

## Arquivos Modificados

- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/machining_report.py`
- `apps/api/app/modules/cnc/services/text_report_exporter.py`
- `apps/api/tests/unit/cnc/test_machining_report.py`
- `apps/web/src/components/cnc/MachiningTechnicalReportViewer.tsx`
- `apps/web/tests/machining-technical-report-viewer.test.ts`
- `CONTEXT.md` e registros em `docs/cto/`.

## Testes Realizados

- 100 testes Python do domínio CNC: aprovados.
- 9 testes Web sob compilação TypeScript estrita: aprovados.
- Ruff sobre API e testes CNC, mypy em 200 fontes e `git diff --check`: aprovados.
- Nenhuma dependência externa de rede instalada.

## Critérios de Aceitação

- A equação de Taylor é determinística para velocidades de 150, 200 e 250 m/min.
- Perfis não tabulados, entradas não físicas e payloads adulterados falham fechados.
- Consumo acima de 80% produz `TOOL_LIFE_EXHAUSTED_WARNING` e alerta visual crítico.
- JSON, laudo e viewer exibem vida, consumo e a limitação analítica obrigatória.
- `PHYSICAL_USE_AUTHORIZED=FALSE`, `G9=PENDING_AUTHORITATIVE_REVIEW`,
  `NO_HUMAN_REVIEW_BYPASS=TRUE`, `MACHINE_SEND/DNC/NC_TRANSFER/CYCLE_START=false`,
  `emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximos Passos

Enviar `VTP-AUTO-208-BATCH` ao CTO e aguardar parecer e próxima ordem. A branch
permanece local, sem push.
