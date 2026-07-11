# Vena_IA Platform

# Documento 04 — Registro de Decisões Vena_IA v1.0

**Status:** Registro Vivo do Projeto  
**Data de criação:** 2026-07-10  
**Projeto:** Vena_IA — Engenharia Inteligente para Manufatura CNC  
**Documento relacionado:** `PROJECT.md`  
**ADR relacionado:** `ADR-001 — Adoção de Arquitetura Modular Monolith`

---

# 1. Objetivo

Manter um registro organizado das decisões técnicas, arquiteturais, operacionais, científicas e estratégicas tomadas durante a evolução da Vena_IA Platform.

Este documento complementa os ADRs. Decisões maiores e estruturais devem possuir ADR próprio. Decisões menores, operacionais ou de acompanhamento podem ser registradas aqui.

---

# 2. Regras de Uso

Toda decisão registrada deverá conter:

* identificador;
* data;
* status;
* tipo;
* contexto;
* decisão;
* justificativa;
* impacto;
* documentos relacionados.

Status permitidos:

* Proposta;
* Aprovada;
* Substituída;
* Rejeitada;
* Em revisão.

Tipos permitidos:

* Arquitetura;
* Backend;
* Frontend;
* Banco de Dados;
* Infraestrutura;
* IA;
* Engenharia;
* Pesquisa;
* Produto;
* Segurança;
* Operação.

---

# 3. Relação entre DECISIONS e ADRs

Use `DECISIONS.md` para:

* registrar decisões rápidas;
* manter histórico de evolução;
* documentar ajustes operacionais;
* registrar decisões ainda pequenas demais para um ADR;
* apontar quando uma decisão exigir ADR futuro.

Use ADR para:

* decisões arquiteturais significativas;
* mudanças de direção;
* adoção ou substituição de tecnologia central;
* alteração relevante de infraestrutura;
* mudança de padrão de desenvolvimento;
* decisões com impacto de longo prazo.

---

# 4. Decisões Registradas

## DEC-001 — Documento Mestre como Fonte Oficial do Projeto

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Produto / Arquitetura / Operação  
**Documentos relacionados:** `PROJECT.md`

### Contexto

O projeto Vena_IA precisa de uma fonte central de verdade para manter consistência entre decisões técnicas, científicas e comerciais.

### Decisão

Adotar o `PROJECT.md` como documento fundador e fonte oficial de verdade da Vena_IA Platform.

### Justificativa

O projeto possui escopo amplo, envolvendo software, IA, engenharia mecânica, CAD/CAM/CNC, pesquisa científica e produto comercial. Sem uma referência central, decisões futuras tenderiam a se dispersar.

### Impacto

Toda decisão, implementação e documentação futura deverá permanecer consistente com o `PROJECT.md`.

---

## DEC-002 — ChatGPT Work como Ambiente Oficial de Gestão Técnica

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Operação  
**Documentos relacionados:** `PROJECT.md`

### Contexto

O projeto será conduzido com apoio de IA para arquitetura, implementação, documentação, revisão e pesquisa.

### Decisão

Adotar o ChatGPT Work como ambiente oficial de desenvolvimento assistido, gestão técnica e documentação do projeto.

### Justificativa

O ambiente permite centralizar decisões, acelerar documentação técnica, apoiar implementação e manter continuidade entre as fases.

### Impacto

O ChatGPT Work atuará como líder técnico assistido, respeitando limites de aprovação humana para contas, credenciais, pagamentos, acessos externos, publicação e decisões estratégicas irreversíveis.

---

## DEC-003 — Adoção de Modular Monolith como Arquitetura Inicial

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Arquitetura  
**Documentos relacionados:** ADR-001

### Contexto

A plataforma precisa evoluir por domínios sem assumir complexidade operacional excessiva no início.

### Decisão

Adotar Modular Monolith como arquitetura inicial oficial.

### Justificativa

A estratégia reduz complexidade, facilita testes, organiza o sistema por domínio e mantém caminho futuro para extração de serviços.

### Impacto

O repositório será estruturado em aplicações, pacotes, serviços e documentação. Microsserviços serão considerados apenas quando houver justificativa técnica e operacional registrada.

---

## DEC-004 — Adoção de Monorepo

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Arquitetura / Operação  
**Documentos relacionados:** ADR-001, `ROADMAP.md`

### Contexto

O projeto possui frontend, backend, pacotes compartilhados, serviços auxiliares, documentação e infraestrutura.

### Decisão

Adotar monorepo como organização inicial do código.

### Justificativa

O monorepo simplifica coordenação de mudanças, versionamento conjunto, documentação e evolução inicial da plataforma.

### Impacto

A estrutura inicial seguirá:

```text
apps/
packages/
services/
docs/
tests/
docker/
scripts/
.github/
```

---

## DEC-005 — Stack Técnica Inicial

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Arquitetura / Backend / Frontend / Infraestrutura / IA  
**Documentos relacionados:** `PROJECT.md`, ADR-001

### Contexto

A plataforma precisa de stack moderna, escalável e compatível com IA, engenharia e aplicações web profissionais.

### Decisão

Adotar a seguinte stack inicial:

* Next.js;
* React;
* TypeScript;
* Tailwind CSS;
* shadcn/ui;
* Python 3.13;
* FastAPI;
* SQLAlchemy;
* Alembic;
* Pydantic v2;
* PostgreSQL;
* pgvector;
* Redis;
* MinIO;
* Docker;
* Docker Compose;
* GitHub Actions;
* OpenAI API.

### Justificativa

A stack cobre frontend, backend, banco relacional, busca vetorial, cache, armazenamento de arquivos, infraestrutura local, CI/CD e IA.

### Impacto

Mudanças nessa stack deverão ser justificadas e registradas. Substituições de tecnologias centrais exigirão ADR.

---

## DEC-006 — Prioridade do MVP

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Produto  
**Documentos relacionados:** `PROJECT.md`, `ROADMAP.md`

### Contexto

O projeto possui escopo amplo e precisa de um MVP realista.

### Decisão

Definir o MVP v1.0 com:

* login;
* dashboard;
* criação de projetos;
* upload de arquivos;
* chat com IA;
* base de conhecimento;
* histórico de interações;
* relatório técnico inicial.

### Justificativa

Esses recursos validam o núcleo da plataforma antes de CAD/CAM/CNC avançados.

### Impacto

Módulos CAD, CAM, CNC, simulação, pesquisa avançada e enterprise serão evoluídos após a base operacional.

---

## DEC-007 — Documentação Obrigatória para Alterações Relevantes

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Operação / Qualidade  
**Documentos relacionados:** `PROJECT.md`

### Contexto

O projeto exige rastreabilidade técnica por sua natureza de software, pesquisa e produto.

### Decisão

Toda alteração significativa deverá atualizar documentação correspondente e, quando aplicável, criar ADR ou registrar decisão neste arquivo.

### Justificativa

Essa prática reduz perda de contexto, facilita pesquisa acadêmica, melhora manutenção e dá base para evolução comercial.

### Impacto

Nenhuma implementação relevante deve ser considerada concluída sem documentação correspondente.

---

## DEC-008 — GitHub como Plataforma de Versionamento e CI/CD

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Operação / Infraestrutura  
**Documentos relacionados:** `ROADMAP.md`

### Contexto

O projeto precisa de versionamento, histórico, issues, milestones, revisão e integração contínua.

### Decisão

Adotar GitHub como plataforma oficial para repositório, issues, milestones e GitHub Actions.

### Justificativa

GitHub é compatível com a stack definida, oferece CI/CD integrado e facilita evolução colaborativa futura.

### Impacto

A criação do repositório será parte da Fase 2. Proteção de branch, templates e milestones deverão ser configurados progressivamente.

---

## DEC-009 — Segurança desde a Fundação

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Segurança  
**Documentos relacionados:** ADR-001, `ROADMAP.md`

### Contexto

A plataforma lidará com arquivos técnicos, documentos, dados de usuários e possíveis informações industriais sensíveis.

### Decisão

Aplicar regras mínimas de segurança desde a fundação:

* não versionar segredos;
* usar `.env.example`;
* validar entradas;
* controlar tipos e tamanhos de upload;
* preparar autenticação e autorização;
* registrar decisões sensíveis.

### Justificativa

Segurança tardia gera retrabalho e risco técnico.

### Impacto

Todos os módulos devem considerar segurança na fase de desenho, mesmo quando a implementação completa ficar para fases posteriores.

---

## DEC-010 — Correção do carregamento de configuração da API (Settings)

**Data:** 2026-07-10  
**Status:** Aprovada  
**Tipo:** Backend / Qualidade  
**Documentos relacionados:** `apps/api/app/core/config.py`, `.env.example`

### Contexto

Durante a validação do ambiente local (Fase 1), identificou-se que `apps/api` falhava ao iniciar: o `Settings` (Pydantic Settings) só reconhecia 5 variáveis, enquanto o `.env.example` define 14. Por padrão, `pydantic-settings` rejeita variáveis de ambiente não declaradas no schema, o que gerava `ValidationError` e impedia o boot da API.

Além disso, `DATABASE_URL`/`REDIS_URL` e os hosts (`POSTGRES_HOST`, `REDIS_HOST`, `MINIO_ENDPOINT`) no `.env.example` apontavam para nomes de serviço do Docker Compose (`postgres`, `redis`, `minio`), que não resolvem quando `apps/api` roda no host via `venv` — fluxo documentado como padrão em `README.md`.

### Decisão

1. `Settings` foi reescrito para declarar todas as variáveis presentes em `.env.example`, com `extra="ignore"` como proteção adicional contra variáveis futuras não mapeadas.
2. `database_url` e `redis_url` passam a ser opcionais; quando não informados, são compostos a partir dos campos individuais (`postgres_*`, `redis_host`, `redis_port`) via propriedades `sqlalchemy_database_url` e `redis_connection_url`.
3. `.env.example` foi atualizado para usar `localhost` como host padrão de Postgres/Redis/MinIO, compatível com o fluxo documentado (`docker compose up postgres redis minio` + `apps/api` rodando no host).

### Justificativa

A API precisa iniciar corretamente no fluxo de desenvolvimento local documentado, que é o caminho crítico de qualquer IA ou pessoa validando o projeto pela primeira vez. Corrigir na raiz evita que o mesmo erro se repita a cada nova sessão de validação.

### Impacto

* `apps/api` agora inicia com sucesso usando `.env.example` copiado para `.env`, sem depender do Docker Compose para o processo da API em si.
* Validado localmente: `GET /health` retorna `200`, `GET /docs` (Swagger) retorna `200`, suíte `pytest` com 2 testes passando.
* Se `apps/api` vier a rodar dentro do próprio Docker Compose (serviço `api`) no futuro, os hosts precisarão ser sobrescritos para os nomes de serviço do Docker (`postgres`, `redis`, `minio`) — comentário deixado no `.env.example` para isso.

---

---

## DEC-011 — Implementação da v0.2 Core: modelos, migrations e persistência

**Data:** 2026-07-11  
**Status:** Aprovada  
**Tipo:** Backend / Frontend / Arquitetura  
**Documentos relacionados:** `docs/ROADMAP.md` (v0.2 — Core), `docs/adr/ADR-001.md`

### Contexto

A v0.2 — Core exige usuários, projetos, estrutura de arquivos, chats, mensagens, modelos de banco, primeira migration e testes de API principais (`docs/ROADMAP.md`).

### Decisão

1. **Modelos ORM dentro de `apps/api/app/modules/<domínio>/models.py`**, não em `packages/database` (que segue como placeholder). Cada módulo (`users`, `projects`, `files`, `chats`) ganhou `models.py` (SQLAlchemy) e `schemas.py` (Pydantic), compartilhando um único `Base` declarativo (`app/core/database.py`).
2. **Alembic configurado** em `apps/api/migrations/`, com a primeira migration (`2aea3ea35160_initial_core_schema`) criando as tabelas `users`, `projects`, `files`, `chats`, `messages`.
3. **Rotas de `users`, `projects`, `files`, `chat`** passam a persistir de verdade (antes retornavam listas vazias fixas), com validação de relação (ex.: projeto exige `owner_id` de um usuário existente; arquivo e chat exigem projeto existente).
4. **Testes automatizados usam SQLite em memória** (`apps/api/tests/conftest.py`), não PostgreSQL. É uma substituição só para testes — PostgreSQL continua sendo o banco oficial (`DEC-005`). SQLite foi escolhido por não exigir serviço externo rodando durante `pytest`, mantendo a suíte rápida e portátil entre agentes de IA.
5. **Dashboard mínimo em `apps/web/app/dashboard/page.tsx`**, consumindo a API real (`NEXT_PUBLIC_API_URL`) para listar e criar projetos. Como autenticação real ainda não existe (planejada para a Fase 6), o formulário cria/reaproveita um usuário simples a partir de nome e e-mail — solução temporária, não é o modelo de autenticação final.

### Justificativa

Manter os modelos dentro de `apps/api` evita a complexidade prematura de empacotar `packages/database` como uma dependência local instalável antes de existir um segundo consumidor real (ex.: um worker em `services/`). Isso é consistente com o princípio de Modular Monolith incremental (`DEC-003`) — extrair para `packages/database` quando houver justificativa técnica clara, não antes.

### Impacto

* `packages/database` permanece como placeholder documentado; qualquer IA que for extrair os modelos para lá deve atualizar este registro.
* Critério de conclusão da v0.2 (`docs/ROADMAP.md`) foi validado localmente: criação de usuário, projeto, arquivo e mensagem funcionando ponta a ponta via API, com dashboard mínimo consumindo os mesmos endpoints.
* A ausência de autenticação real no formulário do dashboard é uma limitação conhecida e temporária — não deve ser interpretada como padrão de segurança aceitável para produção (`SECURITY.md`).
* Validado com Python 3.12 (ambiente de IA não possuía 3.13 disponível); `pyproject.toml` continua exigindo `>=3.13` (`DEC-005`), sem alteração — validação final em 3.13 real ainda pendente do lado do responsável humano.

---

---

# 5. Decisões Pendentes

## PEN-001 — Nome Final do Repositório GitHub

**Status:** Pendente  
**Tipo:** Operação  
**Opções iniciais:**

* `vena-ia`;
* `Vena_IA`;
* `vena-ia-platform`.

Recomendação técnica inicial:

* `vena-ia-platform`

Justificativa:

* nome claro;
* compatível com padrão de repositórios;
* evita underscore;
* comunica produto/plataforma.

---

## PEN-002 — Licença Inicial

**Status:** Pendente  
**Tipo:** Produto / Jurídico  
**Opções:**

* privada inicialmente;
* MIT;
* Apache-2.0;
* licença proprietária.

Recomendação inicial:

* manter repositório privado e licença proprietária até definição comercial.

---

## PEN-003 — Estratégia de Deploy

**Status:** Pendente  
**Tipo:** Infraestrutura  
**Observação:**

Deploy não faz parte da Fase 1. Deverá ser decidido após ambiente local e MVP inicial.

---

## PEN-004 — Provedor de Autenticação

**Status:** Pendente  
**Tipo:** Segurança / Backend  
**Opções:**

* autenticação própria com JWT;
* provedor externo;
* abordagem híbrida.

Recomendação inicial:

* autenticação própria com JWT para o MVP, mantendo abstração para troca futura.

---

# 6. Template para Novas Decisões

```markdown
## DEC-XXX — Título da Decisão

**Data:** AAAA-MM-DD
**Status:** Proposta | Aprovada | Substituída | Rejeitada | Em revisão
**Tipo:** Arquitetura | Backend | Frontend | Banco de Dados | Infraestrutura | IA | Engenharia | Pesquisa | Produto | Segurança | Operação
**Documentos relacionados:** 

### Contexto

Descrever o problema, necessidade ou situação.

### Decisão

Descrever a decisão tomada.

### Justificativa

Explicar por que essa decisão foi escolhida.

### Impacto

Descrever efeitos, riscos, limitações e consequências.
```

---

# 7. Registro de Entrega

## Objetivo

Criar o registro vivo de decisões do projeto Vena_IA.

## Escopo

Inclui regras de uso, relação com ADRs, decisões iniciais aprovadas, decisões pendentes e template de novas decisões.

## Arquivos Criados

* `outputs/DECISIONS.md`

## Arquivos Modificados

* Nenhum.

## Testes Realizados

* Validação de consistência com `PROJECT.md`.
* Validação de consistência com ADR-001.
* Validação de consistência com `ROADMAP.md`.

## Critérios de Aceitação

* Registro de decisões criado em Markdown.
* Decisões iniciais documentadas.
* Pendências estratégicas identificadas.
* Template de novas decisões disponível.

## Próximos Passos

Criar o Documento 05 — Plano de Criação do Repositório GitHub e Estrutura Inicial Vena_IA v1.0.

---

**Fim do Documento 04 — Registro de Decisões Vena_IA v1.0**
