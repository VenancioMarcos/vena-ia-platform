# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-091 a AUTO-095
**Estado:** CNC_ROTA_1_GCODE_FOUNDATION_COMPLETED_LOCAL
**Data:** 2026-09-13
**Branch:** `codex/v5.0-cnc-generation-foundation`
**Baseline da branch:** `d3fafcd86eea65aa075e61904a33c2c2ba6888e8`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

A fundação CNC canônica acrescenta enums de controlador e modos, contratos Pydantic
v2 estritos e um formatador determinístico de candidatos ISO para os passes CAM de
torneamento. O texto inclui preâmbulo G21/G18, movimentos G00/G01, metadados de
percurso e tempo estimado e todas as salvaguardas permanentes.

## Continuidade

O lote está consolidado localmente e aguarda parecer do CTO. Nenhum push, endpoint,
envio a controlador, transferência NC, ciclo físico ou autorização de produção foi
adicionado.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
