# Evidência de capacidade controlada — v1.6 Package 3 R1

Contratos: `vena-ia.capacity-profile/v1` e `vena-ia.capacity-evidence/v1`.

## Reclassificação obrigatória

A evidência anterior do Package 3 é preservada e reclassificada como
`HARNESS_ONLY_BASELINE`. Ela mediu CPU/hash, `deque`, lock e `tracemalloc` no mesmo
processo. Não comprovou duas APIs, dois workers, autenticação/fila Redis, MinIO,
claims, soak ou recuperação da plataforma. Seus números não são capacidade da API.

## Gate integrado R1

O `Controlled Capacity CI` agora aplica Alembic e inicia, como processos ou serviços
descartáveis independentes:

- API A em `8101` e API B em `8102`;
- Worker A e Worker B pelo entrypoint oficial `scripts.worker`;
- PostgreSQL/pgvector e Redis fixados como services;
- MinIO fixado por tag e digest em container local do runner.

As duas APIs e os workers compartilham PostgreSQL, Redis e MinIO. O cenário usa
`AUTH_SECURITY_STORE=redis`, `JOBS_QUEUE_PROVIDER=redis`, credenciais exclusivas do
CI e provider determinístico local habilitado somente em `APP_ENV=capacity-ci`.
Nenhuma chamada externa de IA é permitida.

## Evidência observada

O artefato seguro distingue `harness_unit_baseline`, `process_integration_load`,
`process_integration_soak`, `e2e_cross_instance`, `worker_claims` e
`recovery_after_saturation`. Ele registra somente contagens e estados allowlisted:
processos iniciados, requisições, latências, jobs criados/terminais, claims
duplicados, fila inicial/pico/final, heartbeats, objetos MinIO, cleanup e campos
`NOT_MEASURED` quando a coleta não existe. PID, caminho pessoal, credencial, token,
conteúdo e IDs de domínio não entram no bundle.

O gate comprova por operações reais:

- health/readiness das duas APIs;
- registro/login na API A e autenticação na API B;
- projeto, documento e job alternados entre instâncias;
- idempotência, revogação e rate limit compartilhados;
- quatro PDFs sintéticos em MinIO, processamento por workers e RAG determinístico;
- cancelamento cruzado e retry a partir de falha terminal sintética no PostgreSQL
  descartável com transporte reconhecido/limpo, seguido por enqueue real; os jobs
  principais comprovam processamento real bem-sucedido;
- claim único, interrupção de worker, lease recovery e reinício;
- saturação por instância, `503`, `Retry-After: 1` e recuperação;
- indisponibilidade controlada do MinIO, falha segura e retorno;
- soak HTTP integrado mínimo de 30 segundos;
- isolamento cross-user e cleanup completo.

## Guardrails

O gate falha se houver claim duplicado, job não terminal, fila residual, falha no
cleanup, erro no soak, ausência de `503`/`Retry-After`, falha de recuperação de
worker/MinIO, menos de dois heartbeats ou violação cross-instance. R-034 permanece
parcialmente mitigado. Isto é CI descartável, não benchmark, piloto, deploy, SLA,
SLO, capacidade produtiva ou aprovação comercial.
