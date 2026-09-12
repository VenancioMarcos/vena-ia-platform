# CTO-CODEX-AUTO-040 — Fundação da Rota 2

**Data:** 2026-09-12  
**Estado:** Concluída localmente — aguardando parecer do CTO  
**Baseline:** `400d18af8235d7cac67965e28ba3eaa6bab43413`

## Objetivo

Criar a fundação local da ingestão STEP no frontend: validação limitada em memória
e interface declarativa de seleção/arrastar e soltar, sem upload ou integração de API.

## Escopo

- Validação de extensão, tamanho e cabeçalho ISO-10303-21.
- Dropzone HTML5 com estados ocioso, arrastando, aceito e rejeitado.
- Testes unitários `node:test` para aceitação e rejeições da validação.

## Fora de escopo

Backend, contratos em `packages/`, rede/HTTP, dependências, push, G-code, CNC e
alterações dos limites `PHYSICAL_USE_AUTHORIZED=FALSE` e
`G9=PENDING_AUTHORITATIVE_REVIEW`.

## Critérios de aceitação

O módulo deve ler somente um cabeçalho limitado após validar extensão e tamanho; a
interface não pode enviar o arquivo a uma rede; as validações locais exigidas devem
terminar sem regressão antes do commit local autorizado.

## Arquivos criados e modificados

- `apps/web/lib/cad-validation.ts`
- `apps/web/components/cam/StepUploadZone.tsx`
- `apps/web/tests/cad-validation.test.ts`
- `CONTEXT.md` e registros em `docs/cto/`

## Testes realizados

- Web: 45 testes `node:test` aprovados, incluindo os quatro casos novos.
- TypeScript: `tsc --noEmit --incremental false` aprovado.
- Lint: `next lint` aprovado sem erros ou avisos.
- Backend: `pytest -q` aprovado com 727 testes e 9 skips.
- Qualidade: `ruff check .` e `git diff --check` aprovados.

O Node local foi `v24.19.0`; o manifest declara `22.20.x`. Nenhuma dependência ou
arquivo de manifesto foi alterado.
