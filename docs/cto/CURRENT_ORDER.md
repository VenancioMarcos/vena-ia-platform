# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-044
**Estado:** ROTA_2_STAGE_1_CONSOLIDATED_AWAITING_PR_AUTHORIZATION
**Data:** 2026-09-12
**Baseline inicial sincronizado:** `400d18af8235d7cac67965e28ba3eaa6bab43413` (merge do PR #31 na `main`).
**Branch local:** `codex/v3.2-step-cad-ingestion-web`
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Escopo vigente

A Rota 2 Etapa 1 consolida, apenas no frontend, validação cliente de arquivos STEP,
dropzone HTML5, extração textual limitada de metadados e card acessível de inspeção.
O pacote permanece local e aguarda autorização específica antes de qualquer push ou
Pull Request. Não há upload remoto, backend, geração NC ou autoridade física.

## Validação e entrega

AUTO-044 exige consolidar os registros AUTO-040 a AUTO-043, repetir a suíte web,
TypeScript, lint e verificação de diff e criar um commit exclusivamente documental.
Após a entrega, enviar VTP ao CTO, solicitar parecer e aguardar a próxima ordem.

## Limites permanentes

`NON_PRODUCTION`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`PHYSICAL_USE_AUTHORIZED=FALSE`; `NO_HUMAN_REVIEW_BYPASS=TRUE`;
`MACHINE_SEND=FALSE`; `DNC=FALSE`; `NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.

Não realizar push, merge, tag, release, deploy, mudança de credenciais ou operação
CNC sem o gate específico aplicável.
