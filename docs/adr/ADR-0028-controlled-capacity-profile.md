# ADR-0028 — Perfil controlado e integração real da v1.6

**Status:** Aprovada com remediação R1
**Data:** 2026-08-06
**Decisões relacionadas:** DEC-029, DEC-030

## Contexto

A primeira entrega criou contratos e um baseline sintético, mas representou duas
APIs e dois workers com threads, `deque` e lock no mesmo processo. O workflow usava
providers em memória e não iniciava MinIO. Essa evidência não comprovava a topologia
declarada e foi reclassificada como `HARNESS_ONLY_BASELINE`.

## Decisão

Preservar `vena-ia.capacity-profile/v1` e `vena-ia.capacity-evidence/v1`, mas exigir
no gate terminal duas APIs e dois workers independentes, PostgreSQL/pgvector, Redis e
MinIO compartilhados, migrations aplicadas e requisições HTTP reais. Auth e jobs
usam Redis. O provider determinístico local é construído somente em
`APP_ENV=capacity-ci` e nunca chama rede externa.

O cenário deve comprovar sessão, revogação, rate limit, idempotência, fila, claim,
lease recovery, heartbeat individual, MinIO, cancel/retry, RAG, isolamento,
backpressure e soak mínimo de 30 segundos. A evidência deve marcar o que não mede e
ser publicada de forma atômica, sem overwrite ou symlink.

## Decisão de concorrência

O limite de IA continua por processo. A decisão A é mantida apenas para a topologia
explicitamente testada, e o limite agregado observado é documentado como soma local.
Não existe coordenação distribuída de concorrência nem alegação horizontal.

## Consequências

R-034 avança somente para mitigação parcial/monitorar. R-032 permanece residual e
R-038 monitorado. O gate é CI descartável, não benchmark produtivo, piloto, deploy,
autoscaling, SLA ou SLO. Nenhuma migration, microserviço ou dependência paga é criada.
