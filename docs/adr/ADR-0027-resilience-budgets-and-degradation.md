# ADR-0027 — Budgets de resiliência e degradação segura

**Status:** Aprovada
**Data:** 2026-08-05
**Decisão relacionada:** DEC-028
**Riscos:** R-018, R-033, R-034, R-038

## Contexto

Timeouts e retries existiam de forma dispersa. O provider de IA não classificava
falhas e jobs não tinham teto de backoff separado, permitindo deriva operacional.

## Decisão

Adotar `vena-ia.resilience-policy/v1` como inventário executável e fail-closed.
Aplicar deadline global, attempts limitados, backoff exponencial com teto/jitter,
classificação explícita e `Retry-After` bounded ao provider. Limitar concorrência
de IA por processo sem fila ilimitada. Fixar budgets de PostgreSQL, Redis e MinIO;
preservar PostgreSQL como fonte do recovery e retry durável/idempotente do worker.

## Consequências

Falhas temporárias podem recuperar sem tempestade; falhas permanentes não são
repetidas. Nenhuma resposta falsa ou embedding inválido é persistido. A concorrência
de IA ainda não é distribuída e timeout síncrono não é preemptivo. Capacidade,
autoscaling, SLO/SLA e deploy permanecem fora deste package.
