# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-390 a AUTO-399
**Estado:** CNC_BALLSCREW_AXIAL_THRUST_BUCKLING_AUDITOR_COMPLETED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v9.4-cnc-ballscrew-axial-thrust-buckling-auditor`
**Baseline da branch:** `81b5fad62b7ff60f3b0b6454fa6fae76c70ee573`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O CTO aprovou o `VTP-AUTO-389-BATCH`. A Rota 31 foi publicada no PR #80,
validada pelo Frontend CI em 1m18s e Backend CI em 3m42s, promovida para revisão
e integrada por squash em `81b5fad`. A branch remota foi removida e o checkout
principal ficou alinhado a `origin/main`.

A Rota 32 vincula o auditor do fuso de esferas ao snapshot íntegro das cargas nas
guias. O empuxo axial total combina `Ff`, atrito sobre peso e `Fr` e inércia do
carro. O contrato calcula o limite de flambagem de Euler e a RPM crítica a partir
do diâmetro de raiz, comprimento e fatores de montagem, com alertas acima de 50%
da carga crítica ou 80% da rotação crítica. Manifesto JSON, laudo TEXT e painel
Web revalidam fontes e derivados e não expõem controles de servo ou hardware.

Validação local concluída: 377 testes CNC, 44 testes Web compilados, Ruff, mypy em
238 fontes, TypeScript estrito, Next lint e `git diff --check`.

## Continuidade

Emitir `VTP-AUTO-399-BATCH`, solicitar parecer do CTO e aguardar a próxima ordem.
A branch da Rota 32 permanece exclusivamente local e não deve ser publicada neste
lote.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
