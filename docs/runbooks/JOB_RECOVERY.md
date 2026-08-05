# Runbook — Recovery de jobs v1.5

## Princípio

PostgreSQL é a fonte de verdade; Redis é transporte reconstruível. Não altere
status manualmente. Corrija a dependência, mantenha o mesmo `job_id` e execute o
worker. O reconciliador é automático, concorrente e auditado como `job.recovery`.

## Drill descartável

Use somente fixtures sintéticas. Execute:

```powershell
python -m pytest apps/api/tests/test_jobs.py apps/api/tests/test_job_recovery.py \
  apps/api/tests/test_document_extraction.py apps/api/tests/test_document_processing.py
```

No CI, `RUN_REDIS_INTEGRATION=1` acrescenta Redis real, dois consumidores e dois
recoverers concorrentes. O workflow também executa PostgreSQL/pgvector, MinIO,
Alembic e backup/restore criptografado em destinos descartáveis.

## Matriz dos cenários

| # | Interrupção/falha | Resultado determinístico |
|---|---|---|
| 1 | após claim, antes do handler | lease expira; mesmo job volta a `QUEUED` |
| 2 | durante extração | progresso seguro; lease/retry; chunks são substituídos |
| 3 | após efeito parcial | documento não fica `READY`; retry não anexa versão |
| 4 | durante indexação | documento volta `FAILED`; embeddings são substituídos |
| 5 | durante heartbeat | lease perdido gera `JOB_LEASE_LOST` e recovery |
| 6 | lease expirado | CAS `RUNNING→QUEUED`, limitado por tentativas |
| 7 | entrega duplicada | conjunto `scheduled` + lease dão um efeito lógico |
| 8 | dois workers | claim Lua exclusivo; apenas um handler inicia |
| 9 | API reiniciada | job/estado/correlação permanecem no PostgreSQL |
| 10 | worker reiniciado | reconciliador recupera abandono |
| 11 | Redis reiniciado | jobs não terminais repopulam o transporte |
| 12 | PostgreSQL indisponível | worker retorna degradação sem consumir |
| 13 | MinIO indisponível | `DEPENDENCY_UNAVAILABLE`, retry limitado |
| 14 | IA indisponível | `DEPENDENCY_UNAVAILABLE`, documento não `READY` |
| 15 | retry antes do reinício | `available_at` persiste e respeita o atraso |
| 16 | cancelamento antes do claim | `CANCELLED`; mensagem posterior é descartada |
| 17 | cancelamento em execução | verificado entre páginas/estágios; último progresso fica |
| 18 | timeout | `JOB_TIMED_OUT`; efeito incompleto não vira sucesso |
| 19 | recurso removido | `RESOURCE_NOT_FOUND`, terminal e sem vazamento |
| 20 | tentativas esgotadas | `JOB_RETRY_EXHAUSTED`, sem novo enqueue |

## Efeitos e progresso

Chunks são substituídos em transação por documento. Embeddings atualizam o mesmo
conjunto. `READY` só ocorre após indexação; `SUCCEEDED` só depois de `READY`.
Progresso é percentual inteiro, monotônico por CAS, limitado a 0–100 e só chega a
100 na conclusão do job. Retry/recovery reinicia em 0; cancelamento conserva o
último valor persistido.

## Limites

O timeout mede e recusa o resultado ao final do orçamento, mas não mata chamada
síncrona bloqueada. Isolamento preemptivo fica no gate futuro. Os drills não são
teste de carga, SLO, SLA ou prova de capacidade produtiva.

## Medição sintética local

Em 2026-08-05, Windows/Python local, `test_job_performance.py` mediu 2.000
primitivas enqueue/claim/ack em memória: 21,4 ms total, média 0,010385 ms,
p50 0,0032 ms, p95 0,0293 ms e p99 0,0445 ms. Corpus de extração: 500 páginas
sintéticas geradas por double, sem arquivo real. Esses números detectam regressão
algorítmica apenas; não representam Redis/PostgreSQL/MinIO, concorrência produtiva,
capacidade, SLA ou SLO.
