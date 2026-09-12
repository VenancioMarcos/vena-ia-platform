# CTO-CODEX-AUTO-053 — Backend Ingestion Gateway & Sandbox Persistence

**Data:** 2026-09-12
**Branch:** `codex/v3.3-cad-backend-gateway`
**Baseline:** `75b96080ee9bf1201c2ffda2f70bf9b3e172963c`
**Estado:** `ROTA_3_BACKEND_GATEWAY_IN_PROGRESS`

## Objetivo e escopo

Abrir a Rota 3 com uma fronteira autenticada para receber arquivos STEP sem
carregá-los integralmente em memória e sem ativar o pipeline físico. A rota
`POST /api/v1/cad/step/dispatch` devolve um identificador de job e o estado
`QUEUED`; `GET /api/v1/cad/step/jobs/{job_id}` permite consulta isolada pelo
proprietário.

O repositório organiza CAD em `app/modules/cad`; por isso os novos contratos e
serviços permanecem nesse módulo, preservando a arquitetura vigente, enquanto a
URL pública exigida continua exatamente sob `/api/v1/cad`.

## Implementação e limites defensivos

- `.step` e `.stp` são aceitos sem distinção entre maiúsculas e minúsculas.
- A assinatura `ISO-10303-21;` precisa ocorrer no primeiro bloco de 64 KiB,
  antes da criação do arquivo de sandbox.
- A cópia usa blocos limitados e rejeita payload acima de 15 MiB, removendo o
  arquivo parcial.
- O nome original nunca compõe o caminho persistido; cada arquivo recebe UUIDv4
  e permissões restritas no sandbox temporário pertencente ao processo.
- O registro de job permanece em memória e vinculado ao usuário autenticado.
  O encerramento da aplicação elimina o sandbox que ela criou.
- Esta etapa somente enfileira. Extração geométrica exige datum/unidade
  autoritativos e será conectada por ordem posterior; nenhuma inferência ou
  autorização física foi introduzida.

## Arquivos criados ou modificados

- `apps/api/app/modules/cad/ingestion.py`
- `apps/api/app/modules/cad/ingestion_schemas.py`
- `apps/api/app/modules/cad/dependencies.py`
- `apps/api/app/modules/cad/api/routes.py`
- `apps/api/app/main.py`
- `apps/api/tests/api/test_cad_gateway.py`
- `docs/cto/CTO-CODEX-AUTO-053.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`
- `CONTEXT.md`

## Critérios de aceitação

- Upload STEP válido retorna HTTP 202 com job `QUEUED`, metadados e schema.
- Extensão inválida retorna HTTP 400 sem resíduo em sandbox.
- Assinatura ausente ou limite excedido retorna HTTP 422 sem resíduo.
- Upload sem autenticação retorna HTTP 401 e não persiste conteúdo.
- O status de um job só pode ser consultado por seu proprietário.
- Suítes e verificações exigidas devem permanecer verdes antes do commit.

## Validação executada

- Backend: 731 testes aprovados e 9 ignorados.
- Gateway focado: 4 testes aprovados, incluindo autenticação, isolamento,
  extensões, assinatura, limite e limpeza defensiva.
- Web: 59 testes `node:test` aprovados após compilação TypeScript isolada.
- TypeScript: `tsc --noEmit --incremental false` aprovado.
- Next lint: zero erros e zero avisos.
- Ruff e `git diff --check`: aprovados.

## Governança e próximos passos

`PHYSICAL_USE_AUTHORIZED=FALSE`, `G9=PENDING_AUTHORITATIVE_REVIEW`,
`NO_HUMAN_REVIEW_BYPASS=TRUE`, `MACHINE_SEND=FALSE`, `DNC=FALSE`,
`NC_TRANSFER=FALSE`, `CYCLE_START=FALSE` e
`emission_status=CONTROLLER_PROFILE_UNRESOLVED` permanecem invariáveis.

Após validação e commit local, enviar VTP-AUTO-053 ao CTO e aguardar a próxima
ordem. Nenhum push integra esta missão.
