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
