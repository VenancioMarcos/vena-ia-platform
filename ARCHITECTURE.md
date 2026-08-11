# ARCHITECTURE.md — Arquitetura Técnica da Vena_IA Platform

**Status:** Documento Oficial
**Versão:** 1.0
**Decisão arquitetural formal:** `docs/adr/ADR-001.md`
**Documentos relacionados:** `PROJECT.md`, `CONTEXT.md`, `docs/DECISIONS.md`

---

## 1. Estratégia Arquitetural

A Vena_IA Platform adota **Modular Monolith** como arquitetura inicial (`docs/adr/ADR-001.md`, `DEC-003`), com organização de código em **monorepo** (`DEC-004`).

Essa escolha prioriza velocidade de desenvolvimento e simplicidade operacional na fase de fundação, mantendo fronteiras de domínio claras o suficiente para permitir extração futura de serviços quando houver justificativa técnica registrada.

---

## 2. Visão Geral do Fluxo

```text
apps/web (Next.js)
        ↓  HTTP/REST
apps/api (FastAPI)
        ↓
packages/database (SQLAlchemy + Alembic)
        ↓
PostgreSQL + pgvector
        ↑
packages/ai  ←→  services/rag  ←→  OpenAI API
```

Arquivos técnicos (STEP, STL, DXF, IGES) fluem por:

```text
Upload → apps/api → MinIO (armazenamento) → services/parser-* → metadados no PostgreSQL
```

---

## 3. Organização do Repositório

```text
apps/
├── api/            Backend FastAPI (Core, Auth, Projetos, Arquivos, Chat)
└── web/             Frontend Next.js (Dashboard, Console técnico)

packages/
├── ui/               Componentes compartilhados
├── auth/             Lógica de autenticação/autorização
├── engineering/       Regras de domínio de engenharia (CAD/CAM/CNC)
├── ai/                Camada de abstração de provedores de IA
└── database/          Modelos, migrations e acesso a dados

services/
├── rag/               Pipeline de ingestão e busca semântica
├── parser-step/       Interpretação de arquivos STEP
├── parser-dxf/        Interpretação de arquivos DXF
└── parser-stl/         Interpretação de arquivos STL

docs/                  Documentação técnica detalhada e ADRs
tests/                 Testes unitários, integração e e2e
docker/                Configuração de infraestrutura local
scripts/               Scripts de automação e bootstrap
.github/               Templates de issue/PR e workflows de CI
.ai/                   Protocolo de colaboração entre agentes de IA
```

A estrutura completa e a justificativa de cada decisão estão em `docs/DECISIONS.md` (`DEC-004`, `DEC-005`).

---

## 4. Domínios Funcionais

| Domínio | Responsabilidade |
|---|---|
| **Core** | Usuários, autenticação, projetos, dashboard, arquivos, chat |
| **Engenharia** | CAD, CAM, CNC, materiais, ferramentas, processos, simulação |
| **Pesquisa** | Artigos científicos, PDFs, referências, DOE, ANOVA, relatórios |
| **Enterprise** | Lean Manufacturing, OEE, PCP, ERP, Analytics |

---

## 5. Stack Tecnológica

A stack completa está registrada em `PROJECT.md` (Seção 8) e `docs/DECISIONS.md` (`DEC-005`). Resumo:

* **Frontend:** Next.js, React, TypeScript, Tailwind CSS, shadcn/ui.
* **Backend:** Python 3.13, FastAPI, SQLAlchemy, Alembic, Pydantic v2.
* **Dados:** PostgreSQL, pgvector, Redis, MinIO.
* **Infraestrutura:** Docker, Docker Compose, GitHub Actions.
* **IA:** OpenAI API, embeddings, RAG, agentes especializados.

Qualquer substituição de tecnologia central exige novo ADR (`GOVERNANCE.md`, Seção 6).

---

## 6. Princípios Arquiteturais

1. Modular Monolith até haver justificativa técnica para extração de serviço.
2. Domínios com fronteiras claras dentro do monolito (sem acoplamento cruzado direto entre `packages/`).
3. IA como camada de infraestrutura (`packages/ai`), nunca acoplada diretamente à lógica de negócio.
4. Segurança desde a fundação (`DEC-009`, `SECURITY.md`).
5. Nenhuma implementação sem documentação correspondente (`PROJECT.md`, Seção 19).

---

## 7. Security Gate v0.4.1

```text
Frontend
  → POST /auth/login
  → cookie HttpOnly / Bearer JWT assinado
  → get_current_user
  → identidade e papel confirmados no banco
  → AuthorizationService
  → recurso próprio, regra administrativa ou resposta segura
```

Senhas são protegidas por PBKDF2-HMAC-SHA256. A autenticação reside em
`apps/api/app/modules/auth`; regras reutilizáveis de papel e propriedade ficam em
`authorization.py`. O frontend nunca define `owner_id` ou `role`.

Uploads passam por tamanho, normalização, extensão, MIME e magic bytes antes de
serem enviados ao MinIO. Na v0.4.1, apenas PDF é permitido.

Detalhes formais: `docs/adr/ADR-0009-security-gate-authentication.md`.

---

## 8. Evolução Planejada

A evolução por fases (v0.2 Core → v1.0 MVP) está detalhada em `docs/ROADMAP.md`. Mudanças estruturais relevantes nesta arquitetura devem gerar um novo ADR em `docs/adr/`.

---

## 9. Fundação RAG v0.5

```text
PDF validado no MinIO
  → TextExtractor (pypdf)
  → páginas com texto normalizado
  → ChunkingStrategy configurável
  → DocumentChunkRepository
  → PostgreSQL: document_chunks
  → AIService: embeddings
  → PostgreSQL/pgvector: vetores + índice HNSW
  → busca semântica autenticada por projeto
  → AIService: resposta fundamentada nos trechos recuperados
```

O processamento permanece no domínio `documents` do monólito modular e reutiliza
a autorização por proprietário/papel da v0.4.1. Contratos `Protocol` isolam
extractor, chunker, repository e service. Embeddings e geração permanecem
desacoplados por `AIService`; pgvector fornece similaridade por cosseno. O prompt
trata documentos como dados não confiáveis e exige resposta restrita ao contexto
recuperado. Decisão formal:
`docs/adr/ADR-0010-rag-foundation.md`.

---

## 10. CAD Inicial v0.6

```text
STEP Part 21 validado no MinIO
  → CADAnalysisService (autorização do documento)
  → StepTextParser (leitura textual conservadora)
  → metadados + entidades + pontos + envelope preliminar
  → relatório técnico com limitações explícitas
```

O parser não executa conteúdo do arquivo e não afirma propriedades topológicas.
Volume e propriedades de massa exigem futuro kernel OpenCascade validado. Decisão:
`docs/adr/ADR-0011-step-parser-foundation.md`.

---

## 11. Pesquisa Científica v0.9

```text
Projeto autorizado + PDF existente
  → ResearchArticle (metadados, sem duplicar o arquivo)
  → DocumentChunk existente
  → referências heurísticas com texto bruto e página
  → KnowledgeService/RAG com conteúdo tratado como não confiável
  → síntese rastreável e revisão humana

Projeto autorizado
  → plano DOE preliminar
  → dataset ANOVA descritivo e não inferencial
  → relatório DRAFT_REQUIRES_AUTHOR_REVIEW
```

O módulo `research` mantém entidades, schemas, contrato de repository,
implementação SQLAlchemy, serviços e rotas separados. Ele reutiliza autorização,
documentos e RAG; não cria upload, storage, chunks, embeddings ou provedores
paralelos. Decisão formal: `docs/adr/ADR-0014-scientific-research-foundation.md`.

---

## 12. Integração MVP v1.0

```text
Login → Dashboard → Projeto → PDF → Processing → Embeddings
  → ChatService → KnowledgeService/RAG
  → Message(user + status) + Message(assistant + evidence)
  → ResearchReport DRAFT_REQUIRES_HUMAN_REVIEW
```

`ChatService` é a fronteira transacional: falha do provider marca a pergunta como
`FAILED` e não persiste resposta falsa. O frontend apenas envia perguntas de
usuário; mensagens `assistant` vêm da orquestração interna. Decisão formal:
`docs/adr/ADR-0015-mvp-integration-v1.md`.

---

## 13. Processamento Assíncrono v1.5

```text
HTTP autenticado
  → JobService: owner/projeto/recurso + idempotência derivada
  → PostgreSQL: vena-ia.job/v1 (fonte de verdade)
  → Redis: somente job_id/tipo/correlação, claim + lease + delayed retry
  → scripts.worker (mesmos módulos, banco, release e ownership da API)
  → Documents/RAG: extração, chunks e indexação existentes
  → progresso/estado atômico + auditoria + métricas/spans locais
```

O worker é um processo operacional do mesmo Modular Monolith, não um microserviço:
não possui API, banco, domínio, release ou deploy independentes. Handlers são
allowlisted e nunca executam payload ou conteúdo do usuário. Heartbeat integra
readiness; leases abandonados voltam à fila. Decisão formal:
`docs/adr/ADR-0024-asynchronous-job-foundation.md`.

---

## 14. Integrated Engineering Workflow v2.0 Package 1

```text
Documento STEP autorizado
  → CADAnalysisService (uma análise)
  → geometry-analysis/v1 + geometry-features/v1
  → FeaturePlanningBridge (resultado CAD reutilizado)
  → EngineeringCatalogService (recommendation + report builder)
  → CNCPlanningService (cnc-neutral-plan/v1)
  → integrated-engineering-workflow/v1 + relatório integrado
```

`IntegratedEngineeringWorkflowService` é um orquestrador síncrono e efêmero dentro
do Modular Monolith. Não possui repository, tabela, migration, fila, worker ou engine
de domínio próprios. Cada elo preserva contratos/versionamento e falha fechada;
missing input, incompatibilidade e feature não suportada não são promovidos. O CNC
neutral plan estende o preview existente, sempre simulation-only, não executável e
sob revisão humana. Detalhes: `docs/INTEGRATED_ENGINEERING_WORKFLOW.md` e
`docs/CNC_NEUTRAL_PLAN.md`.

---

## 15. Specialized Assistance v2.0 Package 2

```text
Inputs reproduzíveis + auth
  → IntegratedEngineeringWorkflowService (snapshot autoridade)
  → context builder allowlisted por profile
  → Documents/RAG + Research autorizados quando profile=RESEARCH
  → AIService existente (texto explicativo sem tools)
  → output validation fail-closed
  → specialized-assistance/v1 + grounded-research-assistance/v1
```

O texto generativo é separado do snapshot determinístico e nunca volta como input de
rules, recommendation, planning ou CNC. O deterministic input trace cobre profile,
workflow, evidence e template, sem exigir resposta byte-a-byte. Grounding ausente e
provider failure preservam o workflow. Não há nova persistência, migration, fila,
provider, vector store ou frontend. Detalhes: `docs/SPECIALIZED_ASSISTANCE.md`.

---

## 16. Operational Dashboard v2.0 Package 3

O componente `EngineeringWorkspace` é camada de presentation/orchestration dentro da
página de projeto e usa o cliente HTTP único. Tipos explícitos refletem os contratos
`integrated-engineering-workflow/v1`, `cnc-neutral-plan/v1`,
`specialized-assistance/v1` e `grounded-research-assistance/v1`.

O frontend não calcula status global, recommendation, planning, validação CNC ou
autoridade científica. Ele apresenta `workflow_status`, estados por estágio,
evidence/citations, limitações e revisão humana retornados pelo backend. O
acknowledgement é somente view state local. Não há nova persistência, migration,
cliente HTTP, ledger ou subsistema operacional. Detalhes:
`docs/OPERATIONAL_ENGINEERING_DASHBOARD.md`.

---

## 17. Enterprise Engineering Governance v2.1 Package 1

```text
JWT + usuário persistido
  → OrganizationAuthorization (membership ativa)
  → EngineeringCatalogService (OWNER/ADMIN write; membership read)
  → EngineeringCatalogRepository (consulta filtrada)
  → engineering_catalog_items (scope_type + organization_id)
  → recommendation/planning/workflow/assistance com provenance
```

O ownership referencia Organization; Team não foi adicionado por falta de requisito.
`ORGANIZATION_OWNED`, `SYSTEM_REFERENCE` read-only e `LEGACY_UNSCOPED` bloqueado
separam proveniência. A auditoria existente registra mutações, sem ledger paralelo.
Decisão formal: `docs/adr/ADR-0030-engineering-catalog-ownership.md`.

### Governance evidence — Package 2

`CatalogGovernanceEvidence` é um read model efêmero gerado depois da autorização do
mesmo service. Não possui tabela, repository, ledger ou migration. A rota GET por
recurso evita agregação cross-tenant. Audit evidence referencia a classe de evento
existente, sem fabricar correlação por resource ID ausente no schema de auditoria.
O Release Candidate v2.1.0 fecha exatamente Packages 1–2 sem Package 3 e sem nova
fronteira arquitetural. Contratos de domínio v1 e Alembic `e61c4f8a2b90` permanecem.

---

## 18. General Geometry Evidence v2.2 Package 1

```text
STEP autorizado + metadata textual
  → OpenCascadeGeometryKernel (um único transfer/load)
  → KernelGeometry + FeatureRecognizer v1 preservados
  → GeometryEvidenceBuilder bounded
  → vena-ia.geometry-topology-evidence/v1
```

O evidence é um read model efêmero no módulo CAD existente. Não possui repository,
tabela, migration, fila ou microserviço. IDs derivam de descritores geométricos
canônicos e da identidade/versionamento do kernel; empates são expostos como grupos
de ambiguidade. Unidade desconhecida e topologia inválida não emitem elementos.
Tolerâncias de kernel/modelagem são separadas e manufacturing tolerance permanece
`NOT_PROVIDED`. Detalhes: `docs/GEOMETRY_TOPOLOGY_EVIDENCE.md` e ADR-0031.

---

## 19. Manufacturing Interpretation v2.2 Package 2

```text
geometry-topology-evidence/v1 + explicit stock/intent/constraints
  → ManufacturingPlanningService (bounded deterministic rules)
  → existing organization-scoped EngineeringCatalogService
  → manufacturing-geometry-model/v1
  → verified-process-plan/v1 + planning-verification-evidence/v1
```

O serviço é efêmero e permanece no Modular Monolith. Stock não é inferido da peça;
faces finais são protegidas; accessibility/datum/WCS/setup são candidatos. Recursos
reutilizam exatamente ownership/autorização v2.1. Verification cobre coerência,
missing inputs, resources, precedence e replay, nunca remoção física, colisão ou
cinemática. Detalhes: `docs/MANUFACTURING_GEOMETRY_MODEL.md` e ADR-0032.
