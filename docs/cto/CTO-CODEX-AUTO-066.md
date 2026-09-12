# CTO-CODEX-AUTO-066 — Testes E2E e stress do pipeline CAD

**Status:** `ROTA_5_STAGE_2_STRESS_TESTS_IN_PROGRESS`
**Data:** 2026-09-12
**Branch:** `codex/v3.5-cad-e2e-stress-tests`
**Baseline:** `fce719a7b266ed4bf8e38a984f03e1f55ef57cac`

## Objetivo e escopo

Validar o pipeline de ingestão CAD no nível de sistema sob uploads concorrentes e
no teto de 15 MiB, cobrindo isolamento por proprietário, unicidade de jobs,
contrato concluído e limpeza determinística do sandbox. A missão adiciona somente
testes e registros de governança.

## Cenários implementados

- Quatro uploads STEP concorrentes via FastAPI `TestClient`, FormData e tokens de
  proprietários distintos, usando a extração OCCT completa.
- Unicidade dos quatro `job_id`, acesso exclusivo do proprietário e resposta
  `COMPLETED` com `PROFILE_AVAILABLE_REQUIRES_REVIEW`.
- Ausência de resíduos no sandbox depois de todos os processamentos concorrentes.
- Upload exatamente em 15 MiB com três blocos adicionais de entidades STEP,
  metadados parseados e contrato completo retornado.
- No cenário de limite, um processador limitado de teste evita usar padding
  artificial como benchmark do kernel, preservando a cobertura da ingestão,
  transições, resposta e limpeza.

## Arquivos criados ou modificados

- `apps/api/tests/api/test_cad_system_e2e.py`
- `docs/cto/CTO-CODEX-AUTO-066.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`
- `CONTEXT.md`

## Critérios de aceitação

- Uploads concorrentes não colidem nem vazam estado entre proprietários.
- O sandbox fica vazio após sucesso, inclusive no teto de tamanho.
- A resposta mantém revisão obrigatória sob carga.
- Python, Web e verificações estáticas permanecem verdes.

## Validação executada

- Backend: 740 testes aprovados e 9 ignorados.
- Web: 64 testes `node:test` aprovados.
- TypeScript e Next lint: aprovados, sem erros ou avisos de regras.
- Ruff e mypy: aprovados; 165 arquivos tipados sem problemas.
- `git diff --check`: aprovado.

## Limites permanentes

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`.

## Continuidade

Criar commit local atômico, sem push. Enviar VTP-AUTO-066 ao CTO, solicitar
parecer e aguardar a próxima ordem sem encerrar a execução.
