# Evidência de validação — v1.6 Package 2

**Data:** 2026-08-05/06
**Contrato:** `vena-ia.resilience-policy/v1`
**Head de código:** `1905884359d2e298c6d2f3f6113586e47c1c69fb`

## Local controlado

* resilience policy e runtime policy: PASS;
* Ruff: PASS; mypy: 138 arquivos sem issues;
* API: 266 passed, 2 skips condicionais;
* operações: 55 passed, 6 skips condicionais;
* frontend: typecheck e production build PASS;
* Compose config PASS; Alembic head `b18e4c7d2a91`, sem migration;
* drill: vinte cenários sintéticos, sem API externa paga ou dados reais;
* benchmark de 1.000 drills: 87,375 ms total, média 0,087375 ms,
  p50 0,0762 ms, p95 0,113 ms, p99 0,1465 ms.

O benchmark mede somente overhead Python local do contrato/drill. Não mede
throughput, capacidade, usuários, SLA, SLO, autoscaling ou prontidão produtiva.

## GitHub Actions

* Backend CI `31059513786`: Ruff, mypy, ciclo Alembic, 268 testes de API e 61
  operacionais PASS com PostgreSQL/pgvector, Redis e MinIO reais;
* Frontend CI `31059513849`: pnpm frozen, typecheck e build PASS;
* Runtime Policy CI `31059513794`: runtime policy, resilience policy, Compose e
  builds das imagens fixadas API/Web PASS;
* probe descartável: backup 0,350 s, restore 0,348 s, RPO técnico 1,186 s para
  1 objeto/27 bytes, sem SLO produtivo.

## Limitações preservadas

Concorrência de IA é por processo. Timeout de biblioteca síncrona permanece
cooperativo. Não houve integração com provider de IA externo, teste formal de
carga/capacidade, merge, tag, Release ou deploy.
