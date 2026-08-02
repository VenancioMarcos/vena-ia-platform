# ADR-0019 — Contrato versionado de backup PostgreSQL

**Status:** Aprovada
**Data:** 2026-08-02
**Decisão relacionada:** `DEC-019`

## Contexto

A plataforma não possuía artefato verificável de backup, proteção contra restore
acidental nem teste reproduzível de recuperação PostgreSQL/pgvector.

## Decisão

Adotar dump PostgreSQL custom-format acompanhado de manifesto JSON versionado,
checksum SHA-256, migration head e identificação única do conjunto. Artefatos
devem ficar fora do repositório. Senha passa somente por `PGPASSWORD`.

Restore exige alvo vazio, confirmação e allowlist idênticas, valida checksum
antes da mutação, não usa `--clean` e confirma o Alembic head após concluir. O CI
executa round trip em banco descartável sem dados reais.

## Consequências

PostgreSQL 17 client tools compatíveis tornam-se requisito operacional. MinIO,
criptografia, retenção automatizada, agendamento e storage externo permanecem
fora do Package 1 e exigem decisões posteriores.
