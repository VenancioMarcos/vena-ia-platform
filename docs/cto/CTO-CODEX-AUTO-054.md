# CTO-CODEX-AUTO-054 — Background STEP Processor e Perfil RZ

**Data:** 2026-09-12
**Branch:** `codex/v3.3-cad-backend-gateway`
**Base da missão:** `e88a787`
**Estado:** `ROTA_3_STEP_BACKGROUND_PROCESSOR_IN_PROGRESS`

## Objetivo e escopo

Conectar o job criado pelo gateway a um processamento local em background. A
resposta do dispatch preserva `QUEUED`; a tarefa muda o registro para
`PROCESSING` e termina em `COMPLETED` com perfil RZ limitado, ou `FAILED` com
mensagem pública estável. O arquivo do sandbox é sempre removido.

## Decisão técnica

O worker reutiliza `StepTextParser`, `OpenCascadeGeometryKernel` e
`extract_turning_profile`. Não tenta derivar geometria de texto ISO-10303-21.
O contrato desta rota declara explicitamente datum na origem do mundo, eixo +Z,
unidade extraída do STEP e tolerâncias conservadoras já usadas pelos fixtures de
torneamento. Entradas incompatíveis falham fechadas; o resultado mantém
`PROFILE_AVAILABLE_REQUIRES_REVIEW` e não estabelece manufaturabilidade.

O `BackgroundTasks` do FastAPI executa a função síncrona fora do event loop. Isso
mantém o endpoint responsivo e permite substituir futuramente o executor por uma
fila durável sem alterar o contrato HTTP desta etapa.

## Resultado e contrato

`CadJobStatusResponse.profile_data` é opcional e contém pontos `{r_mm, z_mm}` e
bounding box com raio máximo, Z mínimo/máximo e comprimento total. Falhas não
expõem exceções nativas, caminhos ou stacktraces. O registro em memória permanece
isolado pelo proprietário mesmo depois da limpeza do arquivo.

## Arquivos criados ou modificados

- `apps/api/app/modules/cad/services/step_processor.py`
- `apps/api/app/modules/cad/services/__init__.py`
- `apps/api/app/modules/cad/ingestion.py`
- `apps/api/app/modules/cad/ingestion_schemas.py`
- `apps/api/app/modules/cad/dependencies.py`
- `apps/api/app/modules/cad/api/routes.py`
- `apps/api/tests/api/test_cad_gateway.py`
- `docs/cto/CTO-CODEX-AUTO-054.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`
- `CONTEXT.md`

## Critérios de aceitação

- O POST retorna job `QUEUED`; o processamento real conclui fixture cilíndrico
  como `COMPLETED` com perfil RZ e bounding box revisáveis.
- Conteúdo geometricamente inválido termina em `FAILED` com erro estável.
- O arquivo temporário é removido após sucesso e falha.
- Autenticação, isolamento por proprietário e limites da AUTO-053 permanecem.
- Suítes Python/Web, TypeScript, lint, Ruff e diff devem permanecer verdes.

## Validação executada

- Backend: 732 testes aprovados e 9 ignorados.
- Gateway/processor focado: 5 testes aprovados, cobrindo sucesso real, falha
  sanitizada, limpeza, validação, autenticação e isolamento.
- Web: 59 testes `node:test` aprovados.
- TypeScript: `tsc --noEmit --incremental false` aprovado.
- Next lint: zero erros e zero avisos.
- Mypy do módulo CAD e da aplicação: aprovado sem ocorrências.
- Ruff e `git diff --check`: aprovados.

## Governança

Nenhum plano CAM, pós-processador, G-code, transmissão ou autoridade física foi
adicionado. Os limites permanentes permanecem invariáveis. Após validação e
commit local, enviar VTP-AUTO-054 e aguardar a próxima ordem; sem push.
