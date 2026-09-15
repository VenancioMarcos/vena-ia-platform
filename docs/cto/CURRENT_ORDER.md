# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-400 a AUTO-409
**Estado:** CNC_SPINDLE_BEARING_THERMAL_LOAD_AUDITOR_COMPLETED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v9.5-cnc-spindle-bearing-thermal-load-auditor`
**Baseline da branch:** `f26f20df585737cd789446024978d18fe9e8b592`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O CTO aprovou o `VTP-AUTO-399-BATCH`. A Rota 32 foi publicada no PR #81,
validada pelo Frontend CI em 1m17s e Backend CI em 3m35s, promovida para revisão
e integrada por squash em `f26f20d`. A branch remota foi removida e o checkout
principal ficou alinhado a `origin/main`.

A Rota 33 vincula o auditor térmico dos rolamentos ao snapshot íntegro das cargas
nas guias. O modelo Palmgren decompõe o torque de carga e o torque viscoso em dois
regimes de `ν·n`, converte o torque total em calor por `Q=M·ω` e estima o aumento
estacionário de temperatura por `ΔT=Q/(h·A)`. Manifesto JSON, laudo TEXT e painel
Web revalidam fontes e derivados, mostram o estado conforme ou superaquecido e não
expõem controles de refrigeração, circulação ou hardware.

Validação local concluída: 395 testes CNC, 46 testes Web compilados, Ruff, mypy em
239 fontes, TypeScript estrito, Next lint e `git diff --check`.

## Continuidade

Emitir `VTP-AUTO-409-BATCH`, solicitar parecer do CTO e aguardar a próxima ordem.
A branch da Rota 33 permanece exclusivamente local e não deve ser publicada neste
lote.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
