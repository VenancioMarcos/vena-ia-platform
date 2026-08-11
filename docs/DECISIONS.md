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

## DEC-012 — v0.4.1 Security Gate antes do RAG

**Data:** 2026-07-29
**Status:** Aprovada
**Tipo:** Segurança / Backend / Frontend
**Documentos relacionados:** `docs/adr/ADR-0009-security-gate-authentication.md`, `docs/AUTHORIZATION_MATRIX.md`

### Contexto

A auditoria da v0.4.0 encontrou vulnerabilidades críticas de identidade, papel,
propriedade e validação de upload.

### Decisão

Interromper a progressão para v0.5 RAG e entregar primeiro a v0.4.1 com senha
PBKDF2, token JWT assinado, sessão HttpOnly, autorização centralizada e upload
restrito a PDF validado por magic bytes.

### Justificativa

Construir RAG antes de isolar usuários e projetos ampliaria o impacto de acesso
indevido a documentos e respostas.

### Impacto

`X-User-ID` deixa de autenticar, o cliente deixa de definir `role` e `owner_id`,
rotas sensíveis exigem sessão válida e a v0.5 depende da aprovação deste branch.

---

## DEC-013 — Fundação RAG no domínio Documents

**Data:** 2026-07-30
**Status:** Aprovada
**Tipo:** Arquitetura / Backend / IA
**Documentos relacionados:** `docs/adr/ADR-0010-rag-foundation.md`, `docs/ROADMAP.md`

### Contexto

Com a v0.4.1 publicada, a v0.5 precisa iniciar por uma base testável de ingestão,
sem antecipar embeddings, recuperação semântica ou geração com LLM.

### Decisão

Implementar no domínio `documents` a extração de texto por página, chunking
configurável, persistência rastreável em `document_chunks` e contratos substituíveis
para extractor, chunker, repository e service.

### Justificativa

A abordagem preserva o monólito modular, reutiliza armazenamento e autorização
existentes e mantém a primeira entrega limitada a ingestão documental verificável.

### Impacto

O backend avança para v0.5.0 e adiciona `pypdf` e uma migration. OCR, embeddings,
pgvector, busca vetorial e respostas com LLM continuam explicitamente fora do escopo.

---

## DEC-014 — Fundação científica reutiliza Documents e RAG

**Data:** 2026-07-30
**Status:** Aprovada
**Tipo:** Pesquisa / Arquitetura / IA
**Documentos relacionados:** `docs/adr/ADR-0014-scientific-research-foundation.md`

### Contexto

A v0.9 precisa organizar artigos, referências, sínteses, DOE, ANOVA e relatórios
sem criar outra infraestrutura de documentos e sem alegações científicas ou
estatísticas indevidas.

### Decisão

Criar o domínio `research` referenciando projetos/documentos existentes,
reutilizando chunks e `KnowledgeService`, e manter estados explícitos de revisão
humana para extração, síntese, DOE, ANOVA e relatórios.

### Justificativa

A abordagem preserva autorização e rastreabilidade, reduz duplicação e separa
dados científicos estruturados de arquivos, vetores e conteúdo já persistidos.

### Impacto

A migration `d04f6b8a3c19` cria cinco tabelas de pesquisa. OCR, consulta externa de
DOI, ANOVA inferencial, revisão sistemática e publicação continuam fora do escopo.

---

## DEC-015 — Integração do MVP v1.0 pelo fluxo existente

**Data:** 2026-07-30
**Status:** Aprovada
**Tipo:** Produto / Arquitetura / Backend / Frontend
**Documentos relacionados:** `docs/adr/ADR-0015-mvp-integration-v1.md`

### Contexto

As capacidades do roadmap existiam em módulos, mas chat/IA e histórico estavam
desacoplados e o frontend não oferecia o fluxo completo.

### Decisão

Integrar os módulos existentes por `ChatService`, persistir evidências/estado nas
mensagens, reutilizar `ResearchReport` e entregar uma página de projeto que conduz
PDF → processamento/indexação → pergunta/histórico → relatório.

### Impacto

A migration `e15a7c9d4f20` é a única mudança de schema. O envio público de mensagem
não aceita `assistant`. O E2E determinístico comprova o fluxo e o isolamento entre
usuários sem consumir API paga.

---

## DEC-016 — Sequenciamento pós-v1.1 até v2.0 por gates de risco

**Data:** 2026-08-01
**Status:** Aprovada
**Tipo:** Produto / Segurança / Operação
**Documentos relacionados:** `docs/ROADMAP.md`, `docs/RISK_REGISTER.md`,
`docs/PERMANENT_OPERATIONAL_LIMITS.md`

### Contexto

A v1.1 estabilizou o MVP, mas rate limiting, revogação de sessão,
backup/restore, observabilidade, processamento assíncrono e capacidade ainda
bloqueiam piloto ou produção. Ao mesmo tempo, o plano fundador prevê evolução
CAD/CAM/CNC, pesquisa e produto comercial.

### Decisão

Sequenciar v1.2–v2.0 por gates dependentes: segurança/proteção de dados,
backup/restore, observabilidade, processamento assíncrono, confiabilidade e
escala, engenharia/CAM, CAD/features, piloto controlado e consolidação v2.0.

A v1.2 inicia por rate limiting configurável para cadastro e login. Essa primeira
camada local não substitui gateway ou armazenamento distribuído antes de produção
horizontal. Cada versão exige seus próprios gates, testes e aceite antes da seguinte.

### Justificativa

Tratar riscos operacionais antes de ampliar engenharia reduz impacto de abuso ou
perda de dados, torna falhas diagnosticáveis e cria base mensurável para um piloto.
As versões de engenharia reutilizam capacidades e limites já documentados, sem
inventar módulos fora do `PROJECT.md`.

### Impacto

O roadmap passa a definir v1.2 a v2.0. Deploy, compra, publicação comercial,
G-code liberado e transmissão CNC continuam missões separadas e dependentes de
autorização explícita. Mudança arquitetural real durante uma versão exige ADR.

---

## DEC-017 — Auditoria persistente e versão de autenticação

**Data:** 2026-08-02
**Status:** Aprovada
**Tipo:** Segurança / Banco de Dados
**Documentos relacionados:** `docs/adr/ADR-0017-security-audit-credential-version.md`,
`SECURITY.md`, `docs/RISK_REGISTER.md`

### Contexto

Contas anteriores ao Security Gate podem ter `password_hash` nulo, e eventos
sensíveis não possuíam trilha persistente. A denylist local não basta para
invalidar todas as sessões de uma conta após definir sua credencial.

### Decisão

Persistir eventos mínimos redigidos em tabela própria e adicionar uma versão de
autenticação ao usuário e ao JWT. Somente admin define credencial ausente de
outra conta; a operação incrementa a versão e invalida tokens anteriores.

### Justificativa

A solução reutiliza autenticação, autorização, PBKDF2, SQLAlchemy e Alembic,
sem provedor externo, recuperação pública ou segredo em log.

### Impacto

A migration `f42a1b7c9d30` cria a tabela e a coluna. Auditoria tem consulta admin
limitada e retenção operacional de 90 dias. Logout geral ainda usa denylist
local; observabilidade completa continua planejada para v1.4.

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

**Status:** Resolvida por `DEC-012` e `ADR-0009`
**Tipo:** Segurança / Backend  
**Opções:**

* autenticação própria com JWT;
* provedor externo;
* abordagem híbrida.

Decisão:

* autenticação própria com JWT assinado para o MVP, mantendo fronteiras que
  permitam substituição futura.

---

## DEC-018 — Redis para controles distribuídos de autenticação

**Data:** 2026-08-02
**Status:** Aprovada
**Tipo:** Segurança / Infraestrutura
**Documentos relacionados:** `docs/adr/ADR-0018-distributed-authentication-security-store.md`,
`SECURITY.md`, `docs/RISK_REGISTER.md`

### Contexto

Rate limiting e revogação locais não compartilhavam estado entre réplicas.

### Decisão

Usar o Redis já existente para incremento/TTL atômicos de rate limiting e para
revogação por chave derivada do fingerprint até a expiração do JWT. Falhas do
Redis bloqueiam os fluxos protegidos e geram auditoria; memória exige modo
explícito de desenvolvimento/teste. Preservar `auth_version` no banco.

### Impacto

Redis passa a ser dependência obrigatória por padrão para autenticação. Chaves
têm namespace, TTL e não contêm origem, token, PII ou fingerprint em texto puro.
Gateway/proxy confiável continua uma decisão separada.

---

## DEC-019 — Contrato versionado de backup PostgreSQL

**Data:** 2026-08-02
**Status:** Aprovada
**Tipo:** Operação / Banco de Dados / Segurança
**Documentos relacionados:** `docs/adr/ADR-0019-postgresql-backup-contract.md`,
`docs/runbooks/POSTGRES_BACKUP_RESTORE.md`, `docs/RISK_REGISTER.md`

### Contexto

Não existia backup verificável, manifesto ou proteção contra restore acidental.

### Decisão

Usar dump custom-format com manifesto versionado, SHA-256, migration head e UUID.
Artefatos ficam fora do Git; senha passa apenas por ambiente. Restore exige alvo
vazio, confirmação/allowlist exatas e validação antes e depois da mutação.

### Impacto

O CI realiza round trip descartável com PostgreSQL/pgvector. MinIO, criptografia,
retenção automatizada, agendamento e storage externo continuam fora do pacote.

---

## DEC-020 — Contrato MinIO e backup-set consistente

**Data:** 2026-08-02
**Status:** Aprovada
**Tipo:** Operação / Armazenamento / Segurança
**Documentos relacionados:** `docs/adr/ADR-0020-minio-cross-store-backup-contract.md`,
`docs/runbooks/POSTGRES_BACKUP_RESTORE.md`, `docs/RISK_REGISTER.md`

### Contexto

Recuperar somente PostgreSQL não garante a existência e integridade dos objetos
referenciados no MinIO.

### Decisão

Versionar contratos separados para objetos MinIO e para o conjunto PostgreSQL +
MinIO. Ambos compartilham UUID, timestamp e versão. O conjunto registra Alembic
head, contagens e checksums, e falha fechado sem reparo automático em qualquer
inconsistência. Restore MinIO exige destino vazio, confirmação e allowlist.

### Impacto

O CI comprova round trip combinado descartável. Retenção segue classe manual e
expiração de 30 dias no ambiente não produtivo; descarte exige validação de outro
backup recuperável. Criptografia fica delegada ao storage e gestão de chaves a
ser aprovada, evitando formato criptográfico próprio.

---

## DEC-021 — Bundle criptografado, retenção e execução controlada

**Data:** 2026-08-02
**Status:** Aprovada
**Tipo:** Operação / Criptografia / Recuperação
**Documentos relacionados:** `docs/adr/ADR-0021-encrypted-backup-retention.md`,
`docs/runbooks/BACKUP_RETENTION_AND_SCHEDULING.md`,
`docs/runbooks/RECOVERY_DRILL.md`

### Contexto

Backup verificável ainda precisava de proteção autenticada, expiração segura,
exclusão por set completo, controle de concorrência e medição de recuperação.

### Decisão

Usar AES-256-GCM da dependência fixada `cryptography==49.0.0`, chave externa e
`key_id` não sensível. Retenção é fail-closed, dry-run por padrão e nunca exclui
o último set válido. O job é um CLI com lock e timeout, adequado a cron/Task
Scheduler sem instalar daemon ou agendamento no computador do proprietário.

### Impacto

Chaves antigas devem permanecer recuperáveis em custódia externa para rotação.
O drill mede somente o cenário descartável; KMS, nuvem, dados reais, agendamento
real e SLOs de produção continuam fora do escopo.

---

## DEC-022 — Schema estruturado e contexto de correlação

**Data:** 2026-08-02
**Status:** Aprovada
**Tipo:** Observabilidade / Segurança / API
**Documentos relacionados:** `docs/adr/ADR-0022-structured-observability-context.md`,
`docs/runbooks/OBSERVABILITY.md`, `docs/RISK_REGISTER.md`

### Contexto

Health e auditoria existiam, mas não havia correlação estável entre requisição,
serviços, resposta e falha.

### Decisão

Usar UUIDs validados para request/correlation ID, `ContextVar` para propagação e
eventos JSON `vena-ia.observability/v1` com allowlist estrita. Não coletar body,
headers sensíveis ou conteúdo de documentos/IA. Readiness informa apenas estado
por dependência, sem diagnóstico sensível.

### Impacto

Falhas são correlacionáveis sem expor segredo. Métricas, tracing, alertas e envio
externo continuam fora do Package 1.

---

## DEC-023 — Métricas, auditoria correlacionada e contratos locais de alerta/tracing

**Data:** 2026-08-02
**Status:** Aprovada
**Tipo:** Observabilidade / Segurança / Operação
**Documentos relacionados:** `docs/adr/ADR-0022-structured-observability-context.md`,
`docs/runbooks/OBSERVABILITY.md`, `docs/runbooks/ALERTS.md`

### Contexto

O contexto estruturado do Package 1 não agregava sinais operacionais, não
persistia os identificadores na auditoria e não oferecia contratos substituíveis
para alertas ou tracing.

### Decisão

Adotar `vena-ia.metrics/v1` em memória, com nomes e labels fechados, rotas por
template e falha do coletor sem impacto na requisição. O endpoint é opt-in e
exige admin. Persistir UUIDs de request/correlação na auditoria sem duplicar os
eventos de autenticação. Alertas e spans usam somente providers no-op/local,
allowlists e nenhuma entrega/exportação externa.

### Impacto

A API ganha diagnóstico local correlacionável sem SaaS nem dados de usuário. As
métricas são por processo e não constituem SLO, capacidade ou retenção histórica;
um backend externo exige decisão e autorização posteriores.

---

## DEC-024 — Evidência operacional local e retenção separada por tipo de sinal

**Data:** 2026-08-04
**Status:** Aprovada
**Tipo:** Arquitetura / Segurança / Operação
**Documentos relacionados:** `docs/adr/ADR-0023-incident-drill-evidence-retention.md`,
`docs/runbooks/INCIDENT_DRILL.md`, `docs/RISK_REGISTER.md`

### Contexto

Métricas e spans locais não sobrevivem ao reinício e não existe infraestrutura
aprovada para telemetria histórica externa. Ao mesmo tempo, eventos sensíveis
precisam de retenção auditável e os gates da v1.4 exigem evidência reproduzível.

### Decisão

Manter auditoria sensível persistente no PostgreSQL sob a política atual de 90
dias. Manter métricas e tracing efêmeros por processo, sem improvisar backend
distribuído ou transporte externo. Produzir evidência controlada e allowlisted por
`vena-ia.incident-drill/v1`, em artefato opcional fora do repositório com SHA-256.
Limiares são configuração limitada e calibrada exclusivamente por cenários
sintéticos; não derivam de comportamento individual nem constituem SLO.

### Impacto

R-010 pode ser encerrado como mitigado porque correlação, persistência, retenção e
drill estão comprovados. R-032 continua parcialmente mitigado e R-033 continua
monitorado: reinício, múltiplas réplicas, histórico e dependências externas exigem
gate futuro de infraestrutura. SaaS, webhook, exportador e dados reais continuam
fora do escopo.

---

## DEC-025 — Jobs duráveis e worker no mesmo Modular Monolith

**Data:** 2026-08-05
**Status:** Aprovada
**Tipo:** Arquitetura / Backend / Infraestrutura / Segurança
**Documentos relacionados:** `docs/adr/ADR-0024-asynchronous-job-foundation.md`,
`docs/runbooks/ASYNCHRONOUS_JOBS.md`, `docs/RISK_REGISTER.md`

### Contexto

Processamento PDF longo não deve ocupar o ciclo HTTP nem perder estado em reinícios.
A arquitetura oficial continua Modular Monolith e não autoriza microserviço.

### Decisão

Persistir `vena-ia.job/v1` no PostgreSQL, coordenar identificadores mínimos por Redis
e executar handlers allowlisted em processo worker operacional que compartilha os
módulos, banco, release e ownership da API. Usar transições compare-and-set, lease,
heartbeat, idempotência derivada, retry limitado, timeout e cancelamento cooperativo.

### Impacto

O fluxo PDF ganha durabilidade e recuperação fora do HTTP sem nova fronteira de
serviço. Redis/worker passam a integrar readiness. OCR e interrupção forçada de
bibliotecas síncronas permanecem fora e são riscos explícitos.

---

## DEC-026 — PostgreSQL reconcilia o transporte e OCR permanece adiado

**Data:** 2026-08-05
**Status:** Aprovada
**Tipo:** Arquitetura / Backend / Segurança / Operação
**Documentos relacionados:** `docs/adr/ADR-0025-job-recovery-and-ocr-gate.md`,
`docs/runbooks/JOB_RECOVERY.md`, `docs/OCR_SAFETY_EVALUATION.md`

### Contexto

Lease expirado podia reenfileirar a mensagem sem retirar o job de `RUNNING`, e
perda do Redis não reconstruía o transporte. OCR precisava de decisão formal.

### Decisão

Reconciliar jobs não terminais do PostgreSQL em todo ciclo seguro do worker,
preservando lease válido, cancelando pedido pendente e repondo somente jobs
recuperáveis no Redis. Tornar enqueue, abandono e acknowledge idempotentes/atômicos.
Manter documento `PROCESSING` até indexação completa. Adiar OCR (classe B) até
protótipo isolado, corpus autorizado e limites/qualidade aprovados.

### Impacto

Worker/API/Redis podem reiniciar sem perder a identidade lógica ou deixar lease
preso. Duplicação não inicia dois handlers e efeito parcial não vira sucesso.
R-016 avança parcialmente; R-017 continua aberto, R-033 residual e R-038 monitorado.
Nenhum OCR, microserviço, dependência externa, GPU ou deploy integra a decisão.

---

## DEC-027 — Manifesto executável de runtimes e imagens imutáveis

**Data:** 2026-08-05
**Status:** Aprovada
**Tipo:** Arquitetura / Infraestrutura / Segurança / Operação
**Documentos relacionados:** `docs/adr/ADR-0026-runtime-and-container-reproducibility.md`,
`docs/RUNTIME_SUPPORT_MATRIX.md`, `runtime-policy.json`

### Contexto

Runtimes por major/minor, imagens flutuantes e divergência npm/pnpm permitiam que
CI e containers resolvessem artefatos diferentes sem mudança no Git.

### Decisão

Python 3.13.11 é oficial e 3.14.6 experimental; Node 22.20.0, pnpm 11.9.0 e pip
26.1.2 são explícitos. Imagens externas exigem tag e digest, Actions exigem commit
SHA, frontend exige lockfile frozen. `runtime-policy.json` é validado em CI e o
procedimento de atualização sempre requer branch, regressão, revisão e rollback.

### Impacto

R-008 e R-009 são mitigados no Package 1. R-018/R-033/R-034/R-038 não são
reduzidos. Ausência de lock transitive Python e scanner dedicado permanece
limitação explícita. Não existe migration, deploy ou mudança de arquitetura.

---

## DEC-028 — Contrato executável de resiliência por operação

**Data:** 2026-08-05
**Status:** Aprovada
**Tipo:** Arquitetura / IA / Operação / Segurança
**Documentos relacionados:** `docs/adr/ADR-0027-resilience-budgets-and-degradation.md`,
`resilience-policy.json`, `docs/RESILIENCE_BUDGET_INVENTORY.md`

### Contexto

Timeouts/retries dispersos não distinguiam conexão, leitura, deadline total,
idempotência ou falhas permanentes. IA e jobs precisavam de limites observáveis.

### Decisão

Adotar policy por operação com attempts, deadline, backoff/teto/jitter,
classificação e concorrência limitados. Retry exige classe e operação allowlisted;
falha permanente, resposta inválida e efeito incerto não são repetidos. Estado
compartilhado continua em PostgreSQL/Redis; nenhum segundo provider é introduzido.

### Impacto

R-018 recebe mitigação adicional. R-033 e R-038 permanecem residuais; R-034 não
muda. Concorrência de IA é por processo e o pacote não declara capacidade/SLO.

---

## DEC-029 — Perfil sintético pequeno e evidência de capacidade

**Data:** 2026-08-06
**Status:** Aprovada como baseline; gate terminal substituído por DEC-030
**Tipo:** Operação / Arquitetura / Segurança
**Documentos relacionados:** `docs/adr/ADR-0028-controlled-capacity-profile.md`,
`capacity-profile.json`, `docs/capacity/CAPACITY_EVIDENCE.md`

### Decisão

Adotar perfil bounded e baseline unitário determinístico. Após revisão, APIs/workers
lógicos e soak de hash foram reclassificados como `HARNESS_ONLY_BASELINE`; DEC-030
define a evidência terminal com processos e dependências reais.

### Impacto

R-034 avança parcialmente. Não existe afirmação de capacidade produtiva, SLA/SLO,
piloto, deploy ou escalabilidade horizontal completa.

---

## DEC-030 — Gate de capacidade com processos e dependências reais

**Data:** 2026-08-06
**Status:** Aprovada
**Tipo:** Operação / Arquitetura / Segurança
**Documentos relacionados:** `docs/adr/ADR-0028-controlled-capacity-profile.md`,
`scripts/capacity_process_gate.py`, `docs/capacity/CAPACITY_EVIDENCE.md`

### Contexto

O baseline do DEC-029 representava a topologia em um processo e não comprovava os
serviços compartilhados descritos.

### Decisão

Reclassificar o resultado anterior como `HARNESS_ONLY_BASELINE` e exigir no gate
terminal API A/API B, Worker A/Worker B, PostgreSQL, Redis e MinIO reais e
descartáveis. Providers memory são proibidos nesse cenário. A jornada alterna
instâncias, mede soak HTTP de 30 segundos e publica evidência atômica allowlisted.

### Impacto

R-034 permanece parcialmente mitigado/monitorar. O gate aumenta a confiança em
processos compartilhados, mas não mede ambiente produtivo, não cria SLA/SLO e não
autoriza piloto ou deploy.

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
## DEC-031 — Recomendações de engenharia calculadas sob demanda

As recomendações v1.7 Package 2 são determinísticas e não persistidas. Somente
dados catalogados com fonte/versão participam; ausência resulta em `NOT_AVAILABLE`.
O catálogo permanece global autenticado nesta etapa, sem mudança implícita de
ownership. Toda saída exige revisão humana e não contém comando CNC executável.

## DEC-032 — Reconhecimento conservador separa primitiva de feature

**Data:** 2026-08-06
**Status:** Aprovada
**Tipo:** Arquitetura | Engenharia | Segurança

O recognizer v1.8 rule `1.0.0` consome a topologia OCCT já carregada e trata face
plana e cilíndrica como primitivas geométricas. `THROUGH_CYLINDRICAL_HOLE` somente
existe com boundary interno e atravessamento axial estrito do envelope. Furo cego
e slot ficam adiados. IDs topológicos são locais, confiança representa apenas
evidência geométrica, e revisão humana é obrigatória. Nenhum resultado ativa
engineering produtivo, CAM, toolpath, G-code ou afirma manufaturabilidade.

## DEC-033 — Planning candidate não é seleção de processo

**Data:** 2026-08-06
**Status:** Aprovada
**Tipo:** Arquitetura | Engenharia | Segurança

O bridge rule `1.0.0` consome somente feature rastreável de documento autorizado.
Through hole permite `DRILLING_CANDIDATE`; outras primitivas não permitem inferência.
Catálogos material/máquina/ferramenta devem ser explicitamente selecionados para
reutilizar a recommendation v1.7. Candidate e recommendation permanecem sob revisão
humana, sem saída executável, manufaturabilidade, CAM, toolpath ou código CNC.

## DEC-034 — Decomposição oficial da v1.9 em fundação e ensaio controlado

**Data:** 2026-08-06
**Status:** APROVADA — CTO
**Tipo:** Arquitetura | Segurança | Operação | Produto
**Documentos relacionados:** `docs/ROADMAP.md`, `docs/RISK_REGISTER.md`,
`docs/PERMANENT_OPERATIONAL_LIMITS.md`, `docs/AUTHORIZATION_MATRIX.md`

### Contexto

O roadmap define Controlled Pilot Readiness e suas entregas, mas não definia
Packages. Iniciar código sem decomposição inventaria escopo e colocaria validação de
piloto antes da identidade organizacional, isolamento e governança necessários.

### Decisão

Usar dois Packages. Package 1 formaliza Organization/Team, membership/papéis,
ownership, onboarding, contexto e checklist de piloto sob isolamento fail-closed.
Package 2 compõe runbooks, restore/incidente, proposta SLO, capacidade descartável,
privacidade, suporte, jornada E2E e validação virtual de plano CNC neutro. Package 3
não é criado porque não há dependência independente que justifique fragmentação.

O Package 1 está `APPROVED_FOR_IMPLEMENTATION` pela `TASK-V19-001`. A autorização
abrange a implementação funcional controlada e sua migration; piloto real e deploy
continuam proibidos.

### Justificativa

Separar governança de ensaio respeita a ordem das dependências e permite testar
isolamento antes de produzir evidência de piloto. Reutilizar contratos v1.2–v1.8
evita nova plataforma, microserviço, provider ou duplicação operacional.

### Impacto

O Package 1 implementa as entidades persistentes e a migration única
`d39a7b2c5e11`, conforme ADR-0029. R-042 permanece crítico e apenas parcialmente
mitigado/monitorado. Dados reais, convite externo, billing, SSO, SLO produtivo,
deploy, CAM/toolpath/G-code e máquina continuam fora.

Package 2 implementa a composição efêmera de metadados/referências de evidência sem
nova migration. Persistir bundles foi rejeitado por ampliar retenção sem necessidade;
auditoria existente registra as operações e SHA-256 apenas detecta alteração canônica.

A `TASK-V19-003` aprovou ambos os Packages como funcionalmente completos e definiu
que a v1.9 possui exatamente dois Packages. A Release v1.9.0 preserva R-042 e R-043
como riscos residuais/monitorados e não autoriza piloto real, deploy, publicação
comercial ou saída CNC executável. Qualquer progressão além da v2.0 exige extensão
formal do roadmap e aprovação do CTO; a meta operacional v3.0 não altera esse gate.

---

## DEC-035 — Decomposição da v2.0 Integrated Engineering Platform

**Data:** 2026-08-07
**Status:** APROVADA — CTO
**Tipo:** Arquitetura / Engenharia / IA / Pesquisa / Produto / Segurança
**Documentos relacionados:** `docs/ROADMAP.md`, `docs/RISK_REGISTER.md`,
`docs/PERMANENT_OPERATIONAL_LIMITS.md`, `PROJECT.md`

### Contexto

As v1.2–v1.9 entregaram segurança distribuída, recuperação, observabilidade, jobs,
resiliência/capacidade, catálogos/regras, CAD/features e piloto sintético. Os módulos
existem, mas CAD, planning, CNC neutro, Research e dashboard ainda não formam uma
cadeia única rastreável. O roadmap v2.0 não possuía Packages.

### Decisão

Usar três Packages dependentes: (1) workflow determinístico integrado CAD→relatório;
(2) assistência especializada e Research grounded sobre o núcleo aprovado; (3)
dashboard/evidence/E2E e consolidação do release. CAM preliminar significa somente
operation candidates, setup assumptions, compatibilidade e estimativas; nunca
toolpath ou código CNC.

O Package 1 deve reutilizar os contratos v1.x e criar apenas um aggregate aditivo
`vena-ia.integrated-engineering-workflow/v1` mais a formalização versionada do plano
CNC neutro já esperado pela validação v1.9. IA não pode alterar regras
determinísticas. O Package 1 está `APPROVED_FOR_IMPLEMENTATION` pela
`TASK-V20-001`; Packages 2 e 3 permanecem `NOT_STARTED` e dependem de ordem
posterior do CTO.

### Justificativa

As três fronteiras correspondem a dependências reais: núcleo determinístico,
assistência/grounding e experiência/evidência terminal. Unificá-las impediria revisão
segura; fragmentá-las mais duplicaria componentes existentes.

### Impacto

R-044–R-047 permanecem abertos/gate. Auth, Organization/Team, audit, backup,
observability, jobs, resilience, capacity e pilot evidence são reutilizados. Não há
migration presumida, deploy, piloto real, decisão científica autônoma, toolpath,
pós-processador, G/M-code, NC/DNC, transmissão ou controle CNC. Após v2.0, extensão
formal do roadmap até v3.0 exige aprovação antes de qualquer implementação.

A `TASK-V20-001` implementa somente o Package 1 sem persistência ou migration. O
workflow síncrono reutiliza uma única análise CAD, FeaturePlanningBridge, regras e
report builder existentes; o plano CNC neutro é uma extensão aditiva do preview.
R-044 avança para mitigação parcial/monitoramento e R-045 continua aberto/gate.
Catálogos Engineering permanecem globais autenticados, sem correção silenciosa de
tenancy; Packages 2 e 3 continuam `NOT_STARTED`.

A `TASK-V20-002` aprova o Package 1 e implementa o Package 2 na mesma Draft PR.
Perfis bounded reutilizam `AIService` sem tools, provider ou sistema de agentes novo;
o snapshot `integrated-engineering-workflow/v1` permanece autoridade imutável. O
bridge `grounded-research-assistance/v1` versiona apenas a fronteira comum necessária,
com citações e limites científicos explícitos. Não há persistência ou migration.
R-046 e R-047 avançam somente para mitigação parcial/monitoramento. Package 3 segue
`NOT_STARTED`.

A `TASK-V20-003` aprova o Package 2 e implementa o Package 3 como camada de
presentation/orchestration na mesma Draft PR #23. O dashboard usa o status do backend,
separa determinismo de IA e não cria authority, ledger, persistência ou migration.
Playwright valida caminho integrado, falhas, Research/CNC e acessibilidade em dois
viewports. A `TASK-V20-004` aprova os três Packages, confirma que não existe Package
4 e classifica v2.0 como `RELEASE_CANDIDATE`. R-044–R-047 permanecem mitigados
parcialmente/monitorados; publicação depende de Owner Release Gate direto.

### DEC-036 — Publicação da v2.0.0 e próximo gate exclusivamente documental

O Owner Release Gate direto autorizou a integração da PR #23, a tag anotada e a
GitHub Release `v2.0.0`. Os três Packages ficam `COMPLETE / RELEASED`; não existe
Package 4. R-044–R-047 e catalog tenancy continuam residuais/monitorados. Não houve
deploy e nenhuma implementação pós-v2.0 está autorizada. O próximo estágio é somente
a extensão documental do roadmap até v3.0, dependente de nova ordem formal do CTO.

## DEC-037 — Extensão do roadmap da Vena_IA Platform de v2.0 até v3.0

**Data:** 2026-08-07
**Status:** APROVADA — CTO
**Tipo:** Arquitetura / Engenharia / Dados / IA / Pesquisa / Segurança

### Contexto

A v2.0.0 consolidou a Integrated Engineering Platform, mas catálogos globais,
cobertura geométrica/planning limitada, ausência de simulation evidence e de digital
thread impedem evolução segura. Produção, CNC executável e decisão científica
autônoma permanecem limites intencionais, não backlog implícito.

### Alternativas consideradas

1. Salto direto v2.0→v3.0: rejeitado por misturar migration de tenancy, expansão
   determinística e consolidação arquitetural em um único gate.
2. v2.1/v2.2/v2.3/v3.0: rejeitado por separar simulation/digital thread antes de
   existir volume técnico suficiente, criando versionamento cosmético.
3. v2.1/v2.2/v3.0: proposta como menor sequência com dependências reais.

### Decisão proposta

Usar v2.1 para Enterprise Engineering Governance, v2.2 para Advanced Engineering
Planning & Verification e v3.0 para Manufacturing Intelligence & Digital Thread.
Cada versão tem dois Packages dependentes. IA continua bounded e separada de
deterministic authority; simulation continua evidence não produtiva; execução CNC
permanece fora.

### Trade-offs e riscos

A sequência adiciona dois gates antes da v3.0, mas isola a migration de segurança e
impede que planejamento/simulação cresçam sobre ownership ambíguo. R-048 cobre
vazamento de catálogos/dados Engineering entre organizações; R-049, falsa confiança
em simulação; R-050, escalada de autoridade em orchestration futura. R-044–R-047
continuam residuais e não são renomeados.

### Impacto arquitetural e limites

O Modular Monolith, contratos aditivos, auth, audit, jobs e evidence existentes são
reutilizados. Nenhum microserviço, migration, código, deploy, piloto real, toolpath,
postprocessor, G/M-code, machine connectivity ou agente autônomo é autorizado por
esta proposta. Implementação depende de aprovação explícita posterior do CTO e gates
reservados continuam dependentes do proprietário.

## DEC-038 — Ownership organizacional de catálogos Engineering

**Data:** 2026-08-07
**Status:** APROVADA — RELEASED v2.1.0
**Tipo:** Arquitetura / Dados / Segurança / Compatibilidade

Catalog items graváveis pertencem a uma Organization, sem Team scope. Membership
ativa lê; OWNER/ADMIN cria. `SYSTEM_REFERENCE` é read-only e linhas anteriores viram
`LEGACY_UNSCOPED` invisível até reconciliação confiável. Owner nunca é inferido pela
organização atual, primeira ou default.

A unicidade é por Organization para owned e global para system references. Schemas v1
recebem campos aditivos; exigir `organization_id` na criação elimina escrita global.
O downgrade preserva dados e não restaura constraint global incompatível com duplicatas
legítimas entre organizações. ADR-0030 registra consequências e limites.

### Extensão Package 2 — governance evidence

DEC-038 também adota read model efêmero/versionado por catálogo autorizado. Audit,
Organization e ownership existentes continuam autoridade. Reconciliation mutável,
delete/archive, retenção temporal e bulk export foram rejeitados nesta entrega por não
haver evidência segura ou requisito aprovado. R-048 segue parcialmente mitigado.

### Release v2.1.0

O CTO aprovou Packages 1–2 e confirmou que não existe Package 3. A release alinha
API/FastAPI/health/OpenAPI/frontend em `2.1.0`, preserva Alembic `e61c4f8a2b90` e
contratos v1. O Owner Release Gate direto autorizou o Squash Merge da PR #25, a tag
anotada e a GitHub Release. Não houve deploy; v2.2 segue `NOT_STARTED`.

## DEC-039 — General Geometry Topology Evidence v1

**Data:** 2026-08-10
**Status:** IMPLEMENTADA — AGUARDA REVISÃO DO CTO
**Tipo:** Arquitetura / CAD / Evidência / Segurança

A TASK-V22-001 adota `vena-ia.geometry-topology-evidence/v1` como contrato aditivo e
read model efêmero no módulo CAD. O shape é carregado pelo mesmo adapter OCCT; não há
segundo kernel, microserviço, repository ou migration. IDs canônicos são limitados
por versão do kernel/algoritmo e ambiguidades são declaradas.

Unidade ambígua e topologia inválida falham fechado. Kernel, modelagem e tolerância
de manufatura são campos separados; a última nunca é inferida. Classificação de
surface/curve é evidência geométrica, não feature ou manufacturing intent. R-019,
R-039 e R-040 avançam parcialmente; R-041/R-044/R-049 não são promovidos. Package 2,
toolpath, postprocessor, G/M-code e autoridade física permanecem fora.

## DEC-040 — Manufacturing Interpretation & Verified Process Planning

**Data:** 2026-08-10
**Status:** IMPLEMENTADA — AGUARDA REVISÃO DO CTO
**Tipo:** Arquitetura / Manufacturing / Planning / Segurança

Adotar os contratos `manufacturing-geometry-model/v1`, `verified-process-plan/v1` e
`planning-verification-evidence/v1`. Stock/intent/configuração são facts explícitos;
geometry não gera operação. Catálogos/autorização v2.1 são reutilizados sem paralelo.
Access/datum/WCS/setup são candidatos 3-axis/2.5D e verification não é simulação.

A Gap Analysis da PR #26 é preservada integralmente na linha v2.2/PR #27. Este
registro e ADR-0032 tornam a PR #27 a continuação oficial dos documentos de estado;
a PR #26 só pode ser fechada após comparar os blobs remotos. Sem migration ou v2.3.

## DEC-041 — Independent Level-2 Evidence and Sealed Blind Validation

**Data:** 2026-08-11
**Status:** IMPLEMENTADA — AGUARDA REVISÃO DO CTO
**Tipo:** Arquitetura / Verificação / CNC Safety

Adotar `vena-ia.level2-material-removal-evidence/v1` como verificador bounded que
reconstrói o candidato sem reutilizar o gerador nem o verificador Level-1. Ele cobre
stock factual, continuidade, coordenadas finitas, target coverage, sweep cilíndrico
simplificado, envelope protegido, rapid e fixture keep-out, sempre fail-closed.

Adotar `vena-ia.controlled-blind-validation/v1` como harness que recebe somente o
hash da referência selada e congela artifacts/replay para G0–G9. O conteúdo esperado
não entra no contrato de execução. G9 exige evidência humana real e, quando ausente,
fica `PENDING_REVIEW`; readiness não pode ser promovida. Level 2 não é B-Rep exato,
cinemática, validação física nem autorização produtiva. Não há migration ou novo
serviço arquitetural.

**Correção de authority TASK-V23-003A:** `human_review` não pertence ao request
público. `reviewer_ref`, `decision` e `evidence_ref` textuais não são autoridade e
falham como campos extras. G9 permanece `PENDING_REVIEW` por design até existir uma
fronteira separada, explicitamente autorizada e resolvida server-side a partir de
identidade e estado confiáveis. Nenhum registry, ledger, role ou assinatura foi
inventado para antecipar essa decisão.

## DEC-042 — Immutable Digital Thread and Bounded Intelligence

**Data:** 2026-08-11
**Status:** IMPLEMENTADA — RELEASED v3.0.0
**Tipo:** Arquitetura / Provenance / Tenancy / AI Safety

Adotar `vena-ia.digital-thread/v1` como manifesto efêmero, imutável e determinístico
para a cadeia CAD→report. O contrato registra hash canônico, schema, lifecycle,
ownership, upstream/downstream, provenance, generation/replay e verification refs.
Tenancy é autorizada por token e membership do banco; organization não é autoridade
autodeclarada. Hash/ref/version/stale/forged falham fechado.

Adotar `bounded-manufacturing-intelligence/v1` como leitura explicativa do manifesto.
Ela não possui tools, write capability, estado autônomo, acesso de máquina ou poder
para alterar evidence/G0–G9. Manifesto em existing storage é suficiente nesta fase;
ledger, event sourcing, tabela e migration foram rejeitados por ausência de requisito
real. G9 continua exclusivamente autoritativo e pendente.
