# Registro de Entrega — CTO-CODEX-AUTO-314 a AUTO-323

**Data:** 2026-09-14
**Estado:** `CNC_CHIP_BREAKING_MACHINABILITY_CONTRACT_V2_SCAFFOLDED_LOCAL`
**Branch:** `codex/v8.6-cnc-chip-breaking-machinability-auditor`
**Baseline:** `294440258265c8b06afcbce49c426814293c7a85`
**Publicação da branch atual:** não realizada

## Objetivo e escopo entregue

A Rota 24 implementou o serviço analítico de desgaste de flanco, integração no
manifesto e laudo TEXT e telemetria Web. O contrato recalcula VB, desvios radial e
axial, raio de ponta efetivo e warning por consumo superior a 50% da tolerância.
O PR #72 passou Frontend CI em 1m17s e Backend CI em 3m36s, ficou
`MERGEABLE/CLEAN` e foi integrado por squash em `2944402`; a branch remota foi
removida e a main sincronizada.

A Rota 25 iniciou `ChipBreakingMachinabilityAuditPayload` no schema
`vena-ia.cnc-chip-breaking-machinability-audit/v2`. O contrato registra razão de
compressão, comprimento livre do cavaco e envelopes seguros f×ap por quebra-cavaco
tabulado. Ele recalcula a razão, resolve a referência selecionada, classifica o
ponto de corte e rejeita limites invertidos, duplicatas, referências ausentes,
valores não finitos e promoção de autoridade automática ou física.

## Arquivos da Rota 25

- Modificado: `apps/api/app/modules/cnc/schemas.py`.
- Criado: `apps/api/tests/unit/cnc/test_chip_breaking_machinability_contract.py`.
- Atualizados: `CONTEXT.md`, `docs/cto/CURRENT_ORDER.md`,
  `docs/cto/EXECUTION_STATUS.md`, `docs/cto/ORDER_HISTORY.md` e este registro.

## Testes e critérios de aceitação

- `252 passed` na suíte CNC e `5 passed` focados no scaffold da Rota 25.
- Testes cobrem replay, ponto dentro/fora do envelope, adulteração da razão,
  referência ausente, limites invertidos e autoridade proibida.
- Ruff, mypy em 211 fontes e `git diff --check` aprovados.
- Nenhuma dependência externa de rede foi instalada.

## Limites e próximos passos

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Emitir `VTP-AUTO-323-BATCH`, solicitar parecer do CTO e aguardar a próxima ordem.
