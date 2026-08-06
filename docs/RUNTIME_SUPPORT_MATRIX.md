# Matriz oficial de suporte de runtimes e imagens

**Contrato:** `vena-ia.runtime-policy/v1`
**Manifesto executável:** `runtime-policy.json`
**Data de validação:** 2026-08-05
**Escopo:** v1.6 Package 1 — Runtime and Container Reproducibility

## Decisão de suporte

Python **3.13.11** é o único runtime oficial. Python **3.14.6** é experimental:
a instalação e a regressão local passam, mas ele não integra o gate principal e
não amplia `requires-python`. Node.js **22.20.0** e pnpm **11.9.0** são as versões
oficiais e exatas. Uma versão apenas iniciar não constitui suporte.

| Runtime | Suportado | Mínimo | CI | Container | Local recomendado | Estado e evidência |
|---|---:|---:|---:|---:|---:|---|
| Python | 3.13.11 | 3.13 | 3.13.11 | 3.13.11 | 3.13.11 | Oficial; CI instala, executa Ruff, mypy, Alembic, API, worker, jobs/recovery e operações com serviços reais. |
| Python | 3.14.6 | — | — | — | somente avaliação | Experimental; regressão local aprovada, sem promessa de compatibilidade nem bloqueio do CI. |
| pip | 26.1.2 | 26.1.2 | 26.1.2 | 26.1.2 | 26.1.2 | Ferramenta de instalação fixada; dependências Python ainda não possuem lock transitive multiplataforma. |
| Node.js | 22.20.0 | 22.20.0 | 22.20.0 | 22.20.0 | 22.20.0 | Oficial; typecheck e build de produção com lockfile congelado. |
| pnpm | 11.9.0 | 11.9.0 | 11.9.0 | 11.9.0 | 11.9.0 | Exato em `packageManager`, CI e Dockerfile. |
| PostgreSQL/pgvector | PostgreSQL 17 + pgvector 0.8.1 | PostgreSQL 17 | imagem fixada | imagem fixada | Compose | Integração, migrations e backup/restore reais no Backend CI. |
| Redis | 7.4.7 | 7.4 | imagem fixada | imagem fixada | Compose | Auth store, fila, recovery e concorrência reais no Backend CI. |
| MinIO | RELEASE.2025-09-07T16-13-09Z | mesma release | imagem fixada | imagem fixada | Compose | Storage, readiness e backup/restore reais no Backend CI. |
| Docker Engine/CLI | 29.x recomendado | 24.x | runner GitHub | não aplicável | CLI 29.4.1 auditado | Config validada; daemon local indisponível, builds ficam no Runtime Policy CI. |
| Docker Compose | Compose v2+ | 2.27 | plugin do runner | não aplicável | 5.1.3 auditado | `docker compose config` obrigatório; não representa runtime real. |

## Imagens imutáveis

As referências completas vivem em `runtime-policy.json`. Tags legíveis são sempre
acompanhadas pelo digest multi-arquitetura imutável:

| Uso | Tag | Digest | Origem/licença |
|---|---|---|---|
| API | `python:3.13.11-slim-bookworm` | `sha256:20080e807bfc404f8450b185cf0fc95d553462673598549613735f70a5b4d5d0` | Docker Official Image; Python PSF e componentes Debian |
| Web | `node:22.20.0-alpine3.22` | `sha256:dbcedd8aeab47fbc0f4dd4bffa55b7c3c729a707875968d467aaaea42d6225af` | Docker Official Image; Node.js MIT e componentes Alpine |
| PostgreSQL/pgvector | `pgvector/pgvector:0.8.1-pg17` | `sha256:3e8b3adfd27b5707128f60956f62a793c3c9326ea8cfaf0eab7adccb5d700b21` | projeto pgvector; PostgreSQL License |
| Redis | `redis:7.4.7-alpine` | `sha256:02f2cc4882f8bf87c79a220ac958f58c700bdec0dfb9b9ea61b62fb0e8f1bfcf` | Docker Official Image; licença Redis 7.4 deve ser revista antes de distribuição externa |
| MinIO | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | `sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e` | imagem oficial MinIO; AGPLv3 |

Fontes: repositórios oficiais Docker Library, `pgvector/pgvector`, `redis` e
`minio/minio`. A release MinIO de 2025-10-15 publicada no GitHub não possuía imagem
Docker correspondente no registro durante a auditoria; foi selecionada a release
Docker oficial mais recente que pôde ter manifesto e digest verificados. Isso não
autoriza upgrade automático.

## Política de suporte e atualização

Suporte oficial exige instalação limpa, lint, typecheck, testes, migrations,
runtime e integrações aplicáveis. A revisão é trimestral e também ocorre diante de
advisory crítico ou fim de suporte. Toda atualização segue
`docs/runbooks/RUNTIME_AND_IMAGE_UPDATES.md`, em branch dedicada, com revisão
humana, compatibilidade de dados e rollback. Não existe merge automático.

## Limitações

Não há lock transitive Python multiplataforma nem scanner de vulnerabilidades/SBOM
integrado; portanto, não se afirma reprodutibilidade byte a byte nem ausência de
vulnerabilidades. Digests tornam as bases/imagens imutáveis, mas atualização exige
reconstrução e regressão. Builds locais não foram declarados PASS sem daemon.
