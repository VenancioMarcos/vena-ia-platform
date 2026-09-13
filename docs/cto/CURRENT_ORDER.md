# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-088
**Estado:** CAM_ROTA_4_E2E_GATEWAY_PR_OPEN_AWAITING_CI_AND_REVIEW
**Data:** 2026-09-13
**Branch:** `codex/v4.3-cam-e2e-planning-gateway`
**Baseline da branch:** `ad231f8a044e47e51fd4c1335a5fc0ad84fa4de0`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Estado vigente

O endpoint autenticado `POST /api/v1/cam/turning/plan` liga jobs CAD concluídos e
pertencentes ao usuário ao motor analítico CAM. Somente perfis com estado
`PROFILE_AVAILABLE_REQUIRES_REVIEW` são aceitos; a resposta mantém
`PLANNED_REQUIRES_REVIEW`, `executable_output=false` e todas as salvaguardas.

## Continuidade

Consolidar a governança, publicar a branch, abrir o Draft PR contra `main`, coletar
o estado inicial do CI e enviar o VTP-AUTO-088. Nenhum merge está autorizado.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.
