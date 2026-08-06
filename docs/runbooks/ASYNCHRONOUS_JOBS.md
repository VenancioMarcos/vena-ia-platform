# Runbook — Jobs assíncronos

## Contrato e componentes

- PostgreSQL é a fonte de verdade do contrato `vena-ia.job/v1`.
- Redis coordena ready/delayed/lease e guarda somente `job_id`, tipo e IDs de correlação.
- `python -m scripts.worker` executa handlers allowlisted no mesmo Modular Monolith.
- `/ready` exige PostgreSQL, Redis, MinIO e heartbeat recente do worker.
- Cada ciclo reconcilia jobs não terminais do PostgreSQL antes do claim. Isso
  repopula uma fila Redis reiniciada sem reexecutar estados terminais.

## Inicialização local

```powershell
docker compose up -d postgres redis minio api worker web
docker compose ps
```

Sem Compose, configure o ambiente e execute o worker na raiz do repositório com o
pacote da API instalado. Não use `JOBS_QUEUE_PROVIDER=memory` em produção; a
configuração é recusada explicitamente.

## Operação

1. Confirme `/ready` e o health dos containers.
2. Inicie `POST /documents/{document_id}/jobs/processing` com uma chave de
   idempotência opaca e sem PII.
3. Consulte `GET /jobs/{job_id}`; não derive autorização de headers customizados.
4. Solicite cancelamento em `POST /jobs/{job_id}/cancel`.
5. Um job `FAILED` ou `TIMED_OUT`, ainda abaixo do limite, pode usar
   `POST /jobs/{job_id}/retry`.

## Diagnóstico seguro

- `PDF_ENCRYPTED`, `PDF_NO_TEXT`, `PDF_INVALID`: falhas explícitas e não retryable;
  não há OCR implícito.
- `RESOURCE_NOT_FOUND`: proprietário ou documento deixou de existir; não repetir.
- `QUEUE_UNAVAILABLE`/`DEPENDENCY_UNAVAILABLE`: restaurar a dependência e deixar o
  retry/reconciliador preservar o mesmo job.
- `JOB_TIMED_OUT`, `JOB_LEASE_LOST`, `JOB_RETRY_EXHAUSTED`: verificar efeito
  parcial e correlação antes de retry manual.
- `INTERNAL_PROCESSING_ERROR`: consulte logs correlacionados; a API não expõe stack,
  conteúdo ou mensagem original da dependência.
- `JOB_TYPE_NOT_ALLOWED`: dado persistido não possui handler aprovado; não execute.
- readiness `worker=unavailable`: confirme o container/processo e o Redis. Nunca
  altere manualmente o status para simular conclusão.
- retries esgotados: preserve o job e sua auditoria; corrija a dependência antes de
  uma repetição autorizada.

## Limites

Não há OCR, execução de payload, shell do usuário, backend externo de telemetria,
deploy independente ou garantia de capacidade. PDF sem camada textual falha de
  forma explícita e exige avaliação futura antes de qualquer OCR.

## Regras de recuperação

- `QUEUED`: enqueue idempotente; duplicatas não criam segundo handler.
- `RUNNING` com lease válido: preservado. Sem lease: `QUEUED` ou
  `JOB_RETRY_EXHAUSTED` quando no limite.
- `RETRY_SCHEDULED`: preserva `available_at`; quando vencido volta a `QUEUED`.
- `CANCELLATION_REQUESTED`: termina `CANCELLED`, inclusive após reinício.
- `SUCCEEDED`, `FAILED`, `CANCELLED`, `TIMED_OUT`: nunca reentram automaticamente.
- Retry manual de `FAILED`/`TIMED_OUT` respeita `max_attempts` e mantém `job_id`,
  request/correlation IDs, proprietário, projeto e recurso.

Procedimento detalhado e matriz dos vinte drills: `docs/runbooks/JOB_RECOVERY.md`.
## Guardrail de capacidade sintética

O perfil `vena-ia.capacity-profile/v1` usa dois workers controlados. Claims devem
ser únicos, fila final zero, nenhum job não terminal e recuperação após saturação.
Isso não autoriza aumentar workers em produção nem altera lease/heartbeat/recovery.
