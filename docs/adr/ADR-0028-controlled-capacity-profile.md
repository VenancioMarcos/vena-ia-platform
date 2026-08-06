# ADR-0028 — Perfil sintético e limites compartilhados da v1.6

**Status:** Aprovada
**Data:** 2026-08-06
**Decisão relacionada:** DEC-029

## Decisão

Adotar `vena-ia.capacity-profile/v1` e evidência checksummed v1. Duas APIs lógicas,
dois workers, concorrência 4, carga curta e soak de 3 s formam o perfil de CI. Usar
provider determinístico, PostgreSQL/Redis/MinIO existentes e nenhum dado/API real.

Para IA, escolher a decisão A: o limite por processo (8) é suficiente para a
topologia explicitamente testada (concorrência total 4), com limitação documentada.
Não criar coordenação Redis adicional sem evidência de saturação acima desse perfil.

## Consequências

R-034 avança apenas parcialmente por evidência sintética reproduzível. Não há
capacidade produtiva, SLA/SLO, piloto, deploy ou escalabilidade horizontal provada.
Estados críticos de auth/jobs continuam compartilhados em Redis/PostgreSQL; métricas
e concorrência IA permanecem por processo e documentadas.
