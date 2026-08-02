# ADR-0020 — Contrato MinIO e consistência entre stores

**Status:** Aprovada
**Data:** 2026-08-02
**Decisão relacionada:** `DEC-020`

## Contexto

O Package 1 tornou o PostgreSQL recuperável, mas metadados restaurados poderiam
referenciar objetos ausentes, órfãos ou pertencentes a outro projeto no MinIO.

## Decisão

Adotar `vena-ia.minio-backup/v1` para exportar objetos fora do repositório com
manifesto determinístico, SHA-256 do conteúdo e metadados não sensíveis. Restore
exige bucket/prefixo vazio, confirmação e allowlist exatas, validação integral
antes da primeira escrita e verificação posterior; falhas removem escrita parcial.

Adotar `vena-ia.backup-set/v1` para relacionar manifestos PostgreSQL e MinIO pelo
mesmo UUID, timestamp e versão da aplicação, preservando Alembic head, contagens
e checksums dos manifestos. Ausências, órfãos e divergências de isolamento causam
falha fechada; o software não tenta reparar automaticamente.

## Consequências

O CI usa apenas dados descartáveis e comprova perda/restore dos dois stores. A
retenção inicial é manual por classe e expiração documentadas. Criptografia não
é implementada na aplicação: deverá usar criptografia nativa do destino e gestão
de chaves aprovada em pacote posterior. Agendamento, nuvem e dados reais continuam
fora do escopo.
