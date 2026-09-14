# Registro de Entrega — CTO-CODEX-AUTO-289 a AUTO-293

**Data:** 2026-09-14
**Estado:** `CNC_POWER_TORQUE_ENVELOPE_CONTRACT_V2_SCAFFOLDED_LOCAL`
**Branch:** `codex/v8.3-cnc-power-torque-envelope-auditor`
**Baseline:** `35b867f4833574fa4355aad08b2ade17f56c1043`
**Publicação da branch atual:** não realizada

## Objetivo

Publicar e integrar a auditoria de flexão elástica da Rota 21 e iniciar a Rota 22
com um contrato estrito para conferência da curva declarada de torque e potência do
fuso ao longo da faixa de RPM.

## Escopo entregue

- O `VTP-AUTO-288-BATCH` recebeu parecer explícito `APROVADO (A)` do CTO.
- O PR #69 foi publicado, aprovado pelo Backend CI em 3m45s e pelo Frontend CI em
  1m18s, promovido a ready e integrado por squash em `35b867f`.
- A branch remota da Rota 21 foi removida e a `main` local foi sincronizada com
  `origin/main` antes da criação da branch da Rota 22.
- `SpindlePowerTorqueCurvePoint` revalida cada ponto pela identidade
  `P[kW] = T[Nm] × 2π × rpm / 60000`.
- `SpindlePowerTorqueOperatingPoint` recompõe torque requerido, potência disponível,
  margens de potência/torque e o status do ponto de operação.
- `SpindlePowerTorqueEnvelopeAuditPayload` v2 exige curva de RPM estritamente
  crescente, limites idênticos aos extremos declarados, faixa limitada pelo snapshot
  Kienzle e presença da RPM de referência auditada.
- O torque disponível em cada ponto operacional é recalculado por interpolação
  linear da curva; potência requerida divergente da auditoria Kienzle, ponto fora da
  faixa, curva desordenada ou status adulterado falham fechado.
- O status consolidado é `POWER_TORQUE_ENVELOPE_COMPLIANT` quando todas as margens
  são não negativas e `POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING` caso contrário.

## Arquivos criados

- `apps/api/tests/unit/cnc/test_power_torque_envelope_contract.py`
- `docs/cto/CTO-CODEX-AUTO-293-BATCH.md`

## Arquivos modificados

- `CONTEXT.md`
- `apps/api/app/modules/cnc/schemas.py`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Testes e verificações

- Contrato v2 focado: `5 passed`.
- Suíte CNC completa: `216 passed`.
- Ruff integral: aprovado.
- mypy: aprovado em 208 fontes.
- TypeScript integral: aprovado.
- Next lint: aprovado sem avisos ou erros.
- `git diff --check`: aprovado.
- Nenhuma dependência externa de rede foi instalada.

## Critérios de aceitação

- Curvas de RPM desordenadas ou incompatíveis com o limite Kienzle são rejeitadas.
- Potência e torque de cada ponto obedecem à identidade mecânica declarada.
- Pontos operacionais usam interpolação reproduzível e mantêm a RPM Kienzle coberta.
- Margens negativas resultam no warning consolidado, sem conceder autoridade física.
- Snapshots, valores derivados e status adulterados são rejeitados pelo contrato.

## Limites e próximos passos

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Emitir `VTP-AUTO-293-BATCH`, solicitar parecer do CTO e aguardar a próxima ordem.
A branch da Rota 22 permanece local e sem push.
