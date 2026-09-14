# Registro de Entrega — CTO-CODEX-AUTO-294 a AUTO-303

**Data:** 2026-09-14
**Estado:** `CNC_THERMAL_EXPANSION_DRIFT_CONTRACT_V2_SCAFFOLDED_LOCAL`
**Branch:** `codex/v8.4-cnc-thermal-expansion-drift-auditor`
**Baseline:** `eae463ee990b66c70c874e21a4cba9f7c36c01e9`
**Publicação da branch atual:** não realizada

## Objetivo

Concluir, publicar e integrar a Rota CNC 22 e iniciar a Rota 23 com um contrato
Pydantic v2 defensivo para expansão térmica do tarugo e deriva do fuso em X/Z.

## Escopo entregue

- Serviço determinístico de interpolação da curva do fuso em regimes de torque e
  potência, com margem percentual e warning de sobrecarga.
- Contrato de envelope revalidado contra a auditoria Kienzle, incluindo curva,
  operação, potência, torque, margens, status e invariantes.
- Manifesto técnico e laudo TEXT estendidos com auditoria do fuso e ressalva S1/S6.
- Viewer Web com RPM, torque/potência requeridos e disponíveis, reserva do motor,
  barra de capacidade e badges de conformidade/sobrecarga.
- PR #70 publicado, validado, promovido com mergeability limpa e integrado por
  squash em `eae463e`; branch remota removida e main sincronizada.
- `ThermalExpansionDriftAuditPayload` v2 criado na Rota 23 com coeficientes tabulados
  para aços e alumínio, temperaturas médias, comprimentos de referência, expansão
  do tarugo, deriva do fuso, totais X/Z e limites declarados.
- O contrato térmico recalcula todos os valores e o status, rejeitando coeficiente,
  temperatura, geometria, deriva ou resultado adulterado e não finito.

## Arquivos criados na Rota 23

- `apps/api/tests/unit/cnc/test_thermal_expansion_drift_contract.py`
- `docs/cto/CTO-CODEX-AUTO-303-BATCH.md`

## Arquivos modificados na Rota 23

- `CONTEXT.md`
- `apps/api/app/modules/cnc/schemas.py`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Testes e verificações

- Rota 22 antes da publicação: `224 passed` CNC e `41 passed` focados.
- Web da Rota 22: `24 passed` sob compilação TypeScript.
- CI do PR #70: Frontend `SUCCESS` em 1m17s; Backend `SUCCESS` em 3m12s.
- A primeira execução Backend falhou por reset de conexão ao baixar MinIO de
  `quay.io`; a reexecução do mesmo commit concluiu com sucesso.
- Estado final local: `231 passed` CNC e `7 passed` focados térmicos.
- Ruff aprovado; mypy aprovado em 209 fontes; TypeScript e Next lint aprovados.
- `git diff --check` aprovado; nenhuma dependência externa de rede instalada.

## Critérios de aceitação

- Curva fora da faixa, RPM inválida, dados não finitos e fontes inconsistentes
  falham fechado.
- Sobrecarga de potência/torque permanece warning analítico sem autoridade física.
- Coeficientes térmicos são vinculados ao material e todos os deslocamentos X/Z são
  recalculados pelo contrato.
- Violações das tolerâncias X/Z produzem warning sem qualquer compensação automática.
- Toda a entrega mantém revisão humana e saída executável desativada.

## Limites e próximos passos

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Emitir `VTP-AUTO-303-BATCH`, solicitar parecer do CTO e aguardar a próxima ordem.
A branch da Rota 23 permanece local e sem push.
