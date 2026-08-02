# ADR-0021 — Criptografia autenticada, retenção e job de backup

**Status:** Aprovada
**Data:** 2026-08-02
**Decisão relacionada:** `DEC-021`

## Contexto

Os Packages 1–2 restauravam os stores, mas não protegiam artefatos em repouso,
não executavam retenção e não impediam jobs concorrentes.

## Decisão

Adotar `cryptography==49.0.0` (PyCA, licença `Apache-2.0 OR BSD-3-Clause`) e
AES-256-GCM para criptografia autenticada em streaming. O contrato
`vena-ia.encrypted-backup-set/v1` autentica manifesto e cada artefato com AAD que
vincula contrato, set, `key_id` e path. Chaves têm exatamente 32 bytes em Base64,
ficam fora do repositório/argumentos/logs e não possuem default. O projeto não
possui lockfile Python; a versão exata no `pyproject.toml` é o controle
reprodutível aplicável e o CI instala essa mesma versão.

Retenção valida e descriptografa todos os sets antes de planejar, usa dry-run por
padrão, classes diária/semanal/mensal, quantidade/idade, proteção e confirmação
exata do root. Sets são movidos atomicamente antes de descarte e o último válido
é preservado. O job usa worker interno, lock exclusivo e timeout, sem daemon.

## Consequências

O `key_id` não secreto permite rotação; restaurar um set antigo exige selecionar
a chave antiga correspondente no secret manager externo. Ausência de KMS pago não
bloqueia testes locais, mas custódia/rotação operacional continuam gate pré-piloto.
O recovery drill registra métricas do ambiente descartável, nunca SLO de produção.
