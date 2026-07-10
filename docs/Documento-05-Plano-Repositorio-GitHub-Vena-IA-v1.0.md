# Vena_IA Platform

# Documento 05 — Plano de Criação do Repositório GitHub e Estrutura Inicial Vena_IA v1.0

**Status:** Plano Operacional  
**Data:** 2026-07-10  
**Projeto:** Vena_IA — Engenharia Inteligente para Manufatura CNC  
**Documentos relacionados:** `PROJECT.md`, `ROADMAP.md`, `DECISIONS.md`  
**ADR relacionado:** `ADR-001 — Adoção de Arquitetura Modular Monolith`

---

# 1. Objetivo

Definir o plano operacional para criação do repositório GitHub da Vena_IA Platform e implementação da estrutura inicial do projeto.

Este documento orienta a transição da fundação documental para a execução técnica em código.

---

# 2. Nome do Repositório

Nome recomendado:

```text
vena-ia-platform
```

Justificativa:

* claro e profissional;
* compatível com convenções de repositórios;
* evita underscore no nome público do projeto;
* comunica que o projeto é uma plataforma;
* preserva a identidade Vena_IA no conteúdo e documentação.

Nome interno do projeto:

```text
Vena_IA Platform
```

---

# 3. Visibilidade Inicial

Recomendação:

```text
Privado
```

Justificativa:

* o projeto possui potencial comercial;
* pode envolver pesquisa de mestrado;
* ainda não há definição final de licença;
* evita exposição prematura de arquitetura, código e estratégia.

A abertura pública do repositório deverá ser decisão futura registrada em `DECISIONS.md` ou ADR específico.

---

# 4. Branch Principal

Branch padrão recomendada:

```text
main
```

Política inicial:

* commits diretos permitidos apenas na fase inicial se houver desenvolvimento individual;
* ativar proteção de branch quando o CI estiver operacional;
* exigir checks antes de merge quando houver workflows configurados;
* usar Pull Requests para mudanças relevantes quando o projeto ganhar colaboradores.

---

# 5. Estrutura Inicial do Repositório

Estrutura oficial:

```text
vena-ia-platform/
├── apps/
│   ├── api/
│   └── web/
├── packages/
│   ├── ui/
│   ├── auth/
│   ├── engineering/
│   ├── ai/
│   └── database/
├── services/
│   ├── rag/
│   ├── parser-step/
│   ├── parser-dxf/
│   └── parser-stl/
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── features/
│   └── research/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker/
│   ├── postgres/
│   ├── redis/
│   └── minio/
├── scripts/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── LICENSE
├── PROJECT.md
├── README.md
└── pyproject.toml
```

---

# 6. Arquivos Obrigatórios Iniciais

## 6.1 `README.md`

Deverá conter:

* nome do projeto;
* descrição;
* objetivos;
* stack;
* arquitetura resumida;
* status;
* instruções futuras de instalação;
* links para documentos principais.

## 6.2 `PROJECT.md`

Documento mestre do projeto. Deve ser copiado da versão oficial já criada.

## 6.3 `docs/adr/ADR-001.md`

Registro da decisão arquitetural inicial.

## 6.4 `docs/ROADMAP.md`

Roadmap executivo.

## 6.5 `docs/DECISIONS.md`

Registro vivo de decisões.

## 6.6 `.env.example`

Variáveis iniciais:

```env
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
WEB_PORT=3000

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=vena_ia
POSTGRES_USER=vena_ia
POSTGRES_PASSWORD=change_me

REDIS_HOST=redis
REDIS_PORT=6379

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=change_me
MINIO_SECRET_KEY=change_me
MINIO_BUCKET=vena-ia-files

OPENAI_API_KEY=
```

## 6.7 `.gitignore`

Deverá proteger:

* ambientes virtuais;
* dependências;
* builds;
* caches;
* arquivos `.env`;
* artefatos temporários;
* arquivos locais de IDE.

## 6.8 `docker-compose.yml`

Serviços previstos:

* postgres;
* redis;
* minio;
* api;
* web.

Na primeira versão, `api` e `web` podem ser incluídos como placeholders até os projetos serem criados.

---

# 7. Ordem de Execução Recomendada

1. Criar repositório privado `vena-ia-platform`.
2. Criar branch principal `main`.
3. Criar estrutura de diretórios.
4. Copiar `PROJECT.md`.
5. Copiar ADR-001 para `docs/adr/ADR-001.md`.
6. Copiar `ROADMAP.md` para `docs/ROADMAP.md`.
7. Copiar `DECISIONS.md` para `docs/DECISIONS.md`.
8. Criar `README.md`.
9. Criar `.gitignore`.
10. Criar `.env.example`.
11. Criar `docker-compose.yml`.
12. Criar placeholders de README nas pastas principais.
13. Criar primeiro commit.
14. Criar issues e milestones iniciais.
15. Preparar workflows de CI.

---

# 8. Commits Iniciais

## Commit 1

```text
chore: initialize project documentation
```

Conteúdo:

* `PROJECT.md`;
* `docs/adr/ADR-001.md`;
* `docs/ROADMAP.md`;
* `docs/DECISIONS.md`;
* `README.md`.

## Commit 2

```text
chore: add initial monorepo structure
```

Conteúdo:

* `apps/`;
* `packages/`;
* `services/`;
* `tests/`;
* `docker/`;
* `scripts/`;
* `.github/`.

## Commit 3

```text
chore: add local development environment skeleton
```

Conteúdo:

* `.env.example`;
* `.gitignore`;
* `docker-compose.yml`;
* documentação inicial de ambiente.

---

# 9. Milestones Iniciais

## Milestone 1 — Foundation v0.1

Objetivo:

* documentação;
* repositório;
* estrutura inicial;
* ambiente local base.

## Milestone 2 — Core v0.2

Objetivo:

* usuários;
* projetos;
* dashboard;
* arquivos;
* chats.

## Milestone 3 — IA Base v0.3

Objetivo:

* chat IA;
* integração OpenAI;
* histórico;
* prompts base.

## Milestone 4 — Upload e RAG v0.4-v0.5

Objetivo:

* upload;
* MinIO;
* embeddings;
* pgvector;
* busca semântica.

## Milestone 5 — MVP v1.0

Objetivo:

* fluxo principal completo;
* validação do MVP.

---

# 10. Issues Iniciais Recomendadas

## Foundation

* Criar estrutura inicial do monorepo.
* Adicionar documentação oficial do projeto.
* Criar `.env.example`.
* Criar `.gitignore`.
* Criar Docker Compose base.
* Criar README inicial.

## Backend

* Inicializar `apps/api` com FastAPI.
* Criar endpoint `/health`.
* Configurar SQLAlchemy.
* Configurar Alembic.
* Criar primeira migration.

## Frontend

* Inicializar `apps/web` com Next.js.
* Configurar Tailwind CSS.
* Configurar shadcn/ui.
* Criar layout principal.
* Criar tela inicial do dashboard.

## Infraestrutura

* Configurar PostgreSQL.
* Habilitar pgvector.
* Configurar Redis.
* Configurar MinIO.

## Qualidade

* Criar workflow backend CI.
* Criar workflow frontend CI.
* Definir padrão de commits.
* Documentar critérios de PR.

---

# 11. Templates GitHub

## Issue Template — Feature

Campos:

* objetivo;
* contexto;
* escopo;
* critérios de aceitação;
* documentação relacionada.

## Issue Template — Bug

Campos:

* descrição;
* comportamento esperado;
* comportamento atual;
* passos para reproduzir;
* logs;
* impacto.

## Pull Request Template

Campos:

* resumo;
* arquivos alterados;
* testes realizados;
* documentação atualizada;
* riscos;
* checklist.

---

# 12. Critérios de Validação da Fase 2

A Fase 2 será considerada concluída quando:

* repositório GitHub existir;
* branch `main` estiver configurada;
* documentação oficial estiver versionada;
* estrutura inicial de pastas existir;
* `.env.example` existir;
* `.gitignore` existir;
* `docker-compose.yml` inicial existir;
* README inicial existir;
* milestones iniciais estiverem definidos;
* issues iniciais estiverem registradas ou planejadas;
* primeiro commit estiver realizado.

---

# 13. Decisões Pendentes Antes da Execução

Antes de criar o repositório real, confirmar:

1. Conta ou organização GitHub onde o repositório será criado.
2. Visibilidade inicial: recomendação é privado.
3. Nome final: recomendação é `vena-ia-platform`.
4. Licença: recomendação é proprietária ou pendente inicialmente.

---

# 14. Registro de Entrega

## Objetivo

Criar o plano operacional para a Fase 2 — Repositório GitHub.

## Escopo

Inclui nome do repositório, visibilidade, branch, estrutura inicial, arquivos obrigatórios, commits, milestones, issues, templates e critérios de validação.

## Arquivos Criados

* `outputs/Documento-05-Plano-Repositorio-GitHub-Vena-IA-v1.0.md`

## Arquivos Modificados

* Nenhum.

## Testes Realizados

* Validação de consistência com `PROJECT.md`.
* Validação de consistência com ADR-001.
* Validação de consistência com `ROADMAP.md`.
* Validação de consistência com `DECISIONS.md`.

## Critérios de Aceitação

* Plano de repositório criado.
* Estrutura inicial definida.
* Ordem de execução documentada.
* Commits iniciais planejados.
* Milestones e issues iniciais definidos.
* Pendências antes da execução identificadas.

## Próximos Passos

Executar a Fase 2: criar o repositório GitHub e materializar a estrutura inicial do projeto.

---

**Fim do Documento 05 — Plano de Criação do Repositório GitHub e Estrutura Inicial Vena_IA v1.0**
