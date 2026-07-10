# Vena_IA Platform

# Arquitetura Técnica Inicial

Este documento resume a arquitetura técnica inicial da Vena_IA Platform.

A decisão arquitetural oficial está registrada em:

```text
docs/adr/ADR-001.md
```

## Decisão Principal

A Vena_IA adota inicialmente a arquitetura **Modular Monolith**.

## Justificativa

Essa abordagem permite:

* desenvolvimento inicial mais simples;
* menor complexidade operacional;
* organização por domínio;
* facilidade de testes;
* futura extração de serviços quando houver maturidade técnica.

## Visão Geral

```text
Web Next.js
    ↓
FastAPI
    ↓
PostgreSQL + pgvector
    ↓
RAG / IA / Serviços de Engenharia
```

## Domínios

* Core: usuários, autenticação, projetos, arquivos e chat.
* Engenharia: CAD, CAM, CNC, materiais, ferramentas e processos.
* Pesquisa: artigos, PDFs, referências, DOE, ANOVA e relatórios.
* Enterprise: Lean, OEE, PCP, ERP e analytics.

## Infraestrutura Inicial

* PostgreSQL
* pgvector
* Redis
* MinIO
* Docker Compose

## Referências

* `PROJECT.md`
* `docs/adr/ADR-001.md`
* `docs/ROADMAP.md`
* `docs/DECISIONS.md`

