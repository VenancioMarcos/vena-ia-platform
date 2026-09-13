# Registro de Entrega — VTP-AUTO-228-BATCH

**Status:** A
**Data:** 2026-09-13
**Branch:** `codex/v7.6-cnc-sustainability-carbon-estimator`
**Baseline:** `7ba19b4993dc14d710092e66fcdac40e4e6fac97`

## Objetivo

Publicar e integrar a auditoria de custo/tempo da Rota 14 e implementar uma auditoria
analítica de consumo elétrico e emissão de carbono CNC.

## Escopo

- Draft PR #62, CI remoto, transição para Ready, squash merge e sincronização da main.
- Energia de corte e standby corrigida pela eficiência elétrica declarada.
- Fatores tabulados para Brasil SIN, média dos EUA e média europeia.
- Conversão determinística de kWh em kg CO2e e validações fail-closed.
- Contrato Pydantic imutável e vínculo cruzado com potência Kienzle e tempo do ciclo.
- Integração no relatório JSON, exportador textual e visualizador Web informativo.

## Arquivos Criados

- `apps/api/app/modules/cnc/services/sustainability_estimator.py`
- `apps/api/tests/unit/cnc/test_sustainability_estimator.py`
- `docs/cto/CTO-CODEX-AUTO-228-BATCH.md`

## Arquivos Modificados

- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/machining_report.py`
- `apps/api/app/modules/cnc/services/text_report_exporter.py`
- `apps/api/tests/unit/cnc/test_machining_report.py`
- `apps/web/src/components/cnc/MachiningTechnicalReportViewer.tsx`
- `apps/web/tests/machining-technical-report-viewer.test.ts`
- `CONTEXT.md` e registros em `docs/cto/`.

## Testes Realizados

- 121 testes Python do domínio CNC: aprovados; 33 testes focados de sustentabilidade.
- 11 testes Web sob compilação TypeScript estrita: aprovados.
- Ruff sobre API e testes CNC, mypy em 202 fontes e `git diff --check`: aprovados.
- Nenhuma dependência externa de rede instalada.

## Critérios de Aceitação

- Energia total soma corte e standby, ambos corrigidos por eficiência elétrica.
- Carbono usa fatores imutáveis: BRASIL_SIN 0,085; USA_AVG 0,385; EU_AVG 0,230.
- Potências/tempos inválidos, região ausente e eficiência fora de `(0, 1]` falham fechados.
- O manifesto rejeita sustentabilidade transplantada de outra potência ou ciclo.
- JSON, laudo e viewer exibem energia, carbono, região e a limitação obrigatória.
- `PHYSICAL_USE_AUTHORIZED=FALSE`, `G9=PENDING_AUTHORITATIVE_REVIEW`,
  `NO_HUMAN_REVIEW_BYPASS=TRUE`, `MACHINE_SEND/DNC/NC_TRANSFER/CYCLE_START=false`,
  `emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximos Passos

Enviar `VTP-AUTO-228-BATCH` ao CTO e aguardar parecer e próxima ordem. A branch
permanece local, sem push.
