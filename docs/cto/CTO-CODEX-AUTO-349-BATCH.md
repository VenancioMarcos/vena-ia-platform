# Registro de Entrega — CTO-CODEX-AUTO-349-BATCH

**Data:** 2026-09-14
**Estado:** `CNC_WORKHOLDING_CLAMPING_PR_READY`
**Branch:** `codex/v8.9-cnc-workholding-clamping-auditor`
**Implementação:** `132be50f4f0d0cef76e8f91af654f3c2b1be1b6b`
**Baseline:** `e6da01d0f18e4da143078f6c1cfc33b401257bd0`

## Objetivo e escopo

Publicar o auditor de fixação/castanhas da Rota CNC 27, abrir o Pull Request,
homologar as esteiras remotas e promover a entrega para revisão sem executar
merge.

## Publicação e estado remoto

- PR #76: https://github.com/VenancioMarcos/vena-ia-platform/pull/76
- Frontend CI aprovado em 1m16s.
- Backend CI aprovado em 3m08s na reexecução.
- A execução Backend inicial concluiu os gates do código e falhou apenas no
  download da imagem MinIO por `504 Gateway Timeout`.
- Estado confirmado: `OPEN`, `isDraft=false`, `MERGEABLE/CLEAN`.
- Nenhum merge foi realizado.

## Conteúdo revisável

- Serviço analítico de perda centrífuga e força dinâmica residual para três
  castanhas autocentrantes.
- Contrato Pydantic com validação matemática e falha fechada.
- Integração ao manifesto JSON, laudo TEXT e painel Web tipado.
- Testes de cálculo, limites físicos, status seguro/crítico, renderização e
  ausência de controles de atuadores.

## Validação

- Local: 286 testes CNC unitários, 14 de integração e 34 Web.
- Local: Ruff, mypy em 233 fontes, TypeScript estrito, Next lint e diff.
- Remota: Backend e Frontend CI aprovados no commit de implementação.
- Nenhuma dependência externa instalada no host.

## Limites e continuidade

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Emitir `VTP-AUTO-349-BATCH`, solicitar parecer do CTO e aguardar a próxima
ordem. O PR permanece aberto e nenhum merge foi executado.
