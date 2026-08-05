# Runbook — Jobs assíncronos

## Contrato e componentes

- PostgreSQL é a fonte de verdade do contrato `vena-ia.job/v1`.
- Redis coordena ready/delayed/lease e guarda somente `job_id`, tipo e IDs de correlação.
- `python -m scripts.worker` executa handlers allowlisted no mesmo Modular Monolith.
- `/ready` exige PostgreSQL, Redis, MinIO e heartbeat recente do worker.

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

- `JOB_EXECUTION_FAILED`: consulte logs correlacionados do operador; a API não expõe
  stack, conteúdo ou mensagem original da dependência.
- `JOB_TYPE_NOT_ALLOWED`: dado persistido não possui handler aprovado; não execute.
- `JOB_TIMEOUT`: o orçamento foi excedido; verifique dependências e efeito parcial
  antes de retry. A substituição de chunks é idempotente.
- readiness `worker=unavailable`: confirme o container/processo e o Redis. Nunca
  altere manualmente o status para simular conclusão.
- retries esgotados: preserve o job e sua auditoria; corrija a dependência antes de
  uma repetição autorizada.

## Limites

Não há OCR, execução de payload, shell do usuário, backend externo de telemetria,
deploy independente ou garantia de capacidade. PDF sem camada textual falha de
forma explícita e exige avaliação futura antes de qualquer OCR.
