# CTO-CODEX-AUTO-058 — Integração E2E CAD e Perfil RZ

**Data:** 2026-09-12
**Branch:** `codex/v3.4-e2e-cad-integration`
**Base da missão:** `03aaf2dbee2ca7c5d52bf1d3984aa2923cfd4a83`
**Estado:** `ROTA_4_E2E_CAD_INTEGRATION_IN_PROGRESS`

## Objetivo e escopo

Conectar a experiência STEP da rota de torneamento aos endpoints autenticados do
gateway CAD integrado na `main`. O frontend despacha o arquivo, acompanha o job e,
quando a API retorna `COMPLETED`, converte o contrato RZ em um perfil tipado e o
apresenta em SVG para revisão humana.

## Decisão técnica

A fronteira HTTP reconhece somente os campos snake_case publicados pelo backend e
usa rotas distintas para criação e consulta do job. A conversão valida estados,
identificador, coordenadas finitas, raio não negativo, bounding box e marcador de
revisão antes de criar `TurningProfile2D`. Respostas concluídas incompletas ou
malformadas falham fechadas e não chegam ao renderizador.

O perfil analítico utiliza a projeção métrica RZ já validada pelo frontend. A tela
mostra raio máximo, comprimento Z e o selo `Perfil 2D Analítico (Revisão
Obrigatória)`. Os fixtures sintéticos continuam disponíveis como referência local.

## Arquivos criados ou modificados

- `apps/web/lib/cad-dispatch-service.ts`
- `apps/web/components/cam/TurningProfile2D.tsx`
- `apps/web/components/cam/TurningViewerContainer.tsx`
- `apps/web/tests/cad-dispatch-service.test.ts`
- `apps/web/tests/turning-profile-component.test.ts`
- `docs/cto/CTO-CODEX-AUTO-058.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `CONTEXT.md`

## Critérios de aceitação

- POST e GET usam `/api/v1/cad/step/dispatch` e
  `/api/v1/cad/step/jobs/{job_id}` por padrão.
- O payload `COMPLETED` válido é convertido em `TurningProfile2D` sem aceitar
  coordenadas inválidas ou remover a exigência de revisão.
- O perfil real aparece em SVG com raio máximo, comprimento Z e selo defensivo.
- Controles e indicadores de emissão física permanecem bloqueados.
- Web, TypeScript, lint, Python, Ruff e diff permanecem verdes.

## Validação executada

- Web: 62 testes `node:test` aprovados.
- TypeScript: `tsc --noEmit --incremental false` aprovado.
- Next lint: zero erros e zero avisos de regras.
- Backend: suíte completa aprovada, com 732 testes e 9 ignorados.
- Ruff e `git diff --check`: aprovados.

## Governança

Esta missão produz somente visualização analítica sujeita a revisão. Não cria plano
CAM, G-code, saída executável, transmissão ou autoridade física. Após o commit local,
enviar VTP-AUTO-058 ao CTO e aguardar a próxima ordem; sem push.
