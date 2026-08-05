# ADR-0023 — Incident drill, evidence and observability retention

**Status:** Aprovada
**Data:** 2026-08-04
**Decisão relacionada:** `DEC-024`

## Contexto

Os Packages 1–2 tornaram requisições correlacionáveis e adicionaram métricas,
auditoria, alertas e tracing locais. Faltava demonstrar o uso combinado desses
sinais e decidir retenção sem contratar ou improvisar infraestrutura externa.

## Decisão

Adotar `vena-ia.incident-drill/v1` para drills controlados e descartáveis. Cada
cenário registra somente campos allowlisted, UUIDs de request/correlação, estado,
métrica, código de alerta, evento auditável quando aplicável, resultado e
limitação. O bundle é JSON determinístico, possui SHA-256, fica fora do
repositório e recusa overwrite, traversal e symlink.

A auditoria sensível permanece persistente no PostgreSQL com retenção configurada
de 90 dias. Métricas e spans permanecem locais e efêmeros; reinício perde o estado
e réplicas não agregam. Backend histórico, exporter e transporte externo somente
podem ser introduzidos em gate futuro autorizado.

Limiares são inteiros limitados e calibrados por cenários sintéticos. Não usam IDs
de domínio, comportamento individual, dados reais ou conteúdo de usuário e não
representam SLO, SLA ou capacidade de produção.

## Consequências

Existe evidência operacional reproduzível sem expandir a superfície externa.
R-010 é mitigado pela correlação persistente, retenção e drill. R-032 permanece
parcialmente mitigado e R-033 monitorado devido a histórico efêmero, réplicas e
dependências externas. Alertas continuam no-op/local, sem garantia de entrega.
