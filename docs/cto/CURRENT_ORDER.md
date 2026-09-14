# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-380 a AUTO-389
**Estado:** CNC_GUIDEWAY_CUTTING_MOMENT_LOAD_AUDITOR_COMPLETED_LOCAL
**Data:** 2026-09-14
**Branch:** `codex/v9.3-cnc-guideway-cutting-moment-load-auditor`
**Baseline da branch:** `09d5df2f26f881fbb23d51d8e30e52a4e814129b`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/01b0ab8ec45b2268

## Estado vigente

O CTO aprovou o `VTP-AUTO-379-BATCH`. A Rota 30 foi publicada no PR #79,
validada pelo Frontend CI em 1m10s e Backend CI em 3m42s, promovida para revisão
e integrada por squash em `09d5df2`. A branch remota foi removida e o checkout
principal ficou alinhado a `origin/main`.

A Rota 31 decompõe a força Kienzle em `Fc`, `Ff` e `Fr`, calcula os momentos de
rolamento, arfagem e guinada e combina a carga direta com as reações dos momentos
nos quatro patins. O maior carregamento é comparado a `0,5 × C0`, com warning de
sobrecarga dinâmica. Contrato Pydantic, manifesto JSON, laudo TEXT e painel Web
revalidam fontes e derivados e não expõem controles de hardware.

Validação local concluída: 363 testes CNC, 42 testes Web compilados, Ruff, mypy em
237 fontes, TypeScript estrito, Next lint e `git diff --check`.

## Continuidade

Emitir `VTP-AUTO-389-BATCH`, solicitar parecer do CTO e aguardar a próxima ordem.
A branch da Rota 31 permanece exclusivamente local e não deve ser publicada neste
lote.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
