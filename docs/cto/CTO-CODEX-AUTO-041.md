# CTO-CODEX-AUTO-041 — Integração STEP na rota de torneamento

**Data:** 2026-09-12  
**Estado:** Concluída localmente — aguardando parecer do CTO  
**Branch:** `codex/v3.2-step-cad-ingestion-web`

## Objetivo

Integrar a seleção local de arquivos STEP à rota `/cam/turning`, preservando o
visualizador sintético e mantendo explícito o bloqueio de qualquer emissão de G-code
ou despacho físico.

## Entrega

- `TurningViewerContainer` passa a montar `StepUploadZone` e conserva os fixtures
  sintéticos como visualização local.
- Um STEP aceito mostra nome, tamanho formatado e o banner “Arquivo local carregado
  — Pipeline de geometria analítica aguardando despacho”.
- A limpeza da dropzone remove os metadados locais e restaura imediatamente a
  apresentação baseada em fixtures.
- Não há upload, HTTP, integração de backend, alteração de contratos, geração de
  G-code ou despacho físico.

## Evidências

- Web: 46 testes `node:test` aprovados, incluindo integração SSR do banner e do
  visualizador com um STEP local simulado.
- TypeScript: `tsc --noEmit --incremental false` aprovado.
- Lint: `next lint` aprovado sem erros ou avisos.
- Backend: `pytest -q` aprovado com 727 testes e 9 skips.
- Qualidade: `ruff check .` e `git diff --check` aprovados.

## Limites preservados

`PHYSICAL_USE_AUTHORIZED=FALSE`, `G9=PENDING_AUTHORITATIVE_REVIEW`,
`NO_HUMAN_REVIEW_BYPASS=TRUE`, `MACHINE_SEND=FALSE`, `DNC=FALSE`,
`NC_TRANSFER=FALSE`, `CYCLE_START=FALSE` e
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.

O commit é somente local. Push, merge, tag, release e deploy permanecem fora do
escopo.
