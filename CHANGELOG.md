# CHANGELOG.md

Todas as mudanças relevantes do Vena_IA Platform são registradas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/) e versionamento [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Adicionado
* Contrato `vena-ia.postgresql-backup/v1` com dump custom-format, manifesto,
  SHA-256, migration head e identificação do conjunto.
* Scripts seguros de backup e restore PostgreSQL: artefatos fora do repositório,
  senha somente por ambiente, alvo vazio e confirmação/allowlist explícitas.
* Testes de contrato e round trip descartável para backup, perda simulada,
  restore e verificação mínima de integridade sem dados reais.

## [1.2.0] — 2026-08-02 — Security and Data Protection

### Adicionado
* Rate limiting de janela fixa, configurável e seguro para concorrência protege
  cadastro e login por cliente da conexão, com resposta `429` e `Retry-After`.
* As rotas compatíveis `POST /auth/register` e `POST /users` compartilham o mesmo
  limite de cadastro; cabeçalhos encaminhados e `X-User-ID` não alteram a chave.
* Fluxo administrativo restrito para definir credencial somente em conta legada
  sem senha, com versão de autenticação e invalidação das sessões anteriores.
* Trilha persistente de eventos sensíveis com consulta administrativa paginada
  e filtrável, sem senha, hash, JWT, cookie ou corpo de requisição.
* Migration `f42a1b7c9d30` adiciona `users.auth_version` e a tabela indexada
  `security_audit_events`.

### Segurança
* Redis passa a compartilhar rate limiting e revogação de JWT entre réplicas,
  com operações atômicas, namespace, TTL e chaves derivadas por SHA-256.
* Falhas do Redis bloqueiam autenticação pública, validação de sessão e logout
  com `503` auditável; o modo em memória exige configuração explícita de teste ou
  desenvolvimento e não é fallback silencioso.
* Primeiro controle de aplicação para tentativas públicas de autenticação. A
  origem vem da conexão e ignora `X-Forwarded-For` e `X-User-ID`.
* Logout invalida o token apresentado em uma denylist local até sua expiração,
  agora substituída pela denylist Redis distribuída; tokens com emissão futura
  são rejeitados e logout permanece idempotente sem revelar validade do token.
* A tela de autenticação apresenta mensagem específica para excesso de
  tentativas (`429`) em vez de expor o detalhe técnico da API.

### Documentação
* Roadmap pós-v1.1 consolidado de v1.2 a v2.0 por gates de segurança,
  recuperação, observabilidade, processamento assíncrono, confiabilidade,
  engenharia, CAD, piloto e consolidação da plataforma.
* Primeiro pacote da v1.2 definido como rate limiting configurável e testável
  para cadastro/login, sem substituir o gate distribuído exigido para produção.

## [1.1.0] — 2026-08-01 — Stabilization and Professionalization

### Corrigido
* Criação de projeto, upload, processamento/indexação, falha de chat e criação de
  relatório deixam de recarregar indiscriminadamente projeto, documentos,
  histórico e relatórios; cada operação atualiza somente o estado afetado.
* Carregamentos iniciais de dashboard e projeto agora cancelam requests ao
  desmontar o componente, evitando atualizações obsoletas e trabalho de rede sem
  consumidor.
* A suíte migra do cliente HTTP legado para HTTPX2, removendo o warning de
  depreciação do `TestClient` sem alterar contratos públicos da API.
* Requisições do frontend agora compartilham um único cliente, normalizam também
  os detalhes estruturados de validação do FastAPI e encerram carregamentos após
  30 segundos quando a API não responde.
* Dashboard e autenticação deixam de ocultar falhas de logout e apresentam
  mensagens consistentes para credenciais, conflitos e indisponibilidade.
* A tela de projeto mantém o fluxo principal disponível quando somente a listagem
  de relatórios falha e expõe no histórico o erro persistido de perguntas sem
  resposta, sem criar resposta falsa.
* Controles sem ação foram removidos da navegação inicial; o acesso ao MVP aponta
  somente para o fluxo operacional existente.
* Documentos em `FAILED` podem ser reprocessados com substituição idempotente
  dos chunks, permitindo recuperação após falhas transitórias de extração ou
  armazenamento.
* A tela de projeto atualiza o estado após falhas e permite tentar novamente o
  processamento ou a indexação quando o provedor de IA voltar a responder.
* Relatórios rejeitam evidências fora de `document_ids`, coordenadas inválidas,
  scores fora do intervalo e trechos que não correspondem ao chunk persistido.

### Testes
* Suíte integral preservada em 165 testes aprovados e sem warnings no pacote 3.
* Cobertura do contrato de erro persistido no chat e nova validação integral do
  pacote 2 com 165 testes, frontend, Docker, PostgreSQL e OpenAPI.
* Cobertura de regressão para reprocessamento de documentos `FAILED` e para
  rejeição de evidências fabricadas ou não declaradas em relatórios.

## [1.0.0] — 2026-07-30 — Vena_IA Platform MVP

### Adicionado
* Fluxo frontend integrado para projeto, PDF, processamento/indexação, pergunta
  fundamentada, fontes, histórico e relatório técnico inicial.
* `ChatService` conecta RAG e histórico persistente, incluindo estado, autoria,
  erro controlado e evidências por documento, página, chunk, score e trecho.
* Listagem de relatórios por projeto e migration `e15a7c9d4f20`.
* Teste E2E determinístico do MVP e isolamento entre dois usuários, sem API paga.
* Guias de instalação, uso, smoke test e matriz de auditoria do MVP.

### Alterado
* API e frontend avançam para `1.0.0`.
* Envio público de mensagens não permite mais falsificar o papel `assistant`;
  respostas do assistente são persistidas somente pela orquestração interna.

## [0.9.0] — 2026-07-30 — Scientific Research Foundation

### Adicionado
* Fundação científica v0.9 com biblioteca de artigos vinculada a projetos e
  documentos PDF existentes, metadados bibliográficos conservadores e autorização
  por proprietário.
* Extração preliminar e rastreável de referências, preservando texto bruto, página,
  método, DOI/ano quando encontrados e estado explícito de ausência.
* Sínteses assistidas por IA restritas ao RAG autorizado, com evidências por
  documento/página/chunk e proteção contra instruções contidas nos PDFs.
* Planos DOE preliminares, preparação descritiva de datasets para futura ANOVA e
  relatórios em rascunho, todos com revisão humana obrigatória.
* Migration `d04f6b8a3c19` para artigos, referências, estudos DOE, datasets ANOVA e
  relatórios científicos.

### Alterado
* API avança para `0.9.0`.

## [0.8.0] — 2026-07-30 — CNC Initial

### Adicionado
* Fundação v0.8 com estrutura neutra e não executável de operações CNC.
* Preview autenticado para estratégia futura Fanuc Oi e compatibilidade planejada
  Romi D1250, sempre `SIMULATION_ONLY_REQUIRES_HUMAN_REVIEW`.

### Alterado
* API avança para `0.8.0`.

## [0.7.0] — 2026-07-30 — Engineering / CAM Initial

### Adicionado
* Fundação v0.7 para recomendação preliminar de fresamento baseada em família de
  material, ferramenta e limites da máquina.
* Cálculos determinísticos de rotação, avanço e tempo de corte, sempre marcados
  `PRELIMINARY_REQUIRES_HUMAN_REVIEW`.
* Endpoint autenticado `POST /manufacturing/milling/recommendation`.

### Alterado
* API avança para `0.7.0`.

## [0.6.0] — 2026-07-30 — CAD Initial

### Adicionado
* v0.6 CAD Inicial com upload seguro de STEP Part 21 (`.step`/`.stp`).
* Parser conservador de metadados STEP, schema, entidades, pontos cartesianos,
  unidade e envelope dimensional preliminar.
* Endpoint autenticado `POST /cad/documents/{document_id}/analysis` com relatório
  técnico rastreável e limitações explícitas.

### Alterado
* API avança para `0.6.0`.

## [0.5.0] — 2026-07-30 — RAG

### Adicionado
* Fundação RAG v0.5 com extração segura de texto de PDFs por página.
* Fragmentação configurável com rastreabilidade por documento, página, índice e
  offsets no texto extraído.
* Modelo `DocumentChunk`, contratos de extractor/chunker/repository/service e
  migration `b7f3c9d2e614`.
* Endpoints autenticados `POST /documents/{document_id}/processing` e
  `GET /documents/{document_id}/chunks`, incluindo filtro por página.
* Geração de embeddings por documento e armazenamento vetorial em PostgreSQL
  com pgvector e índice HNSW para similaridade por cosseno.
* Busca semântica rastreável por projeto e respostas fundamentadas exclusivamente
  nos trechos recuperados, com proteção explícita contra instruções nos documentos.
* Endpoints `POST /documents/{document_id}/embeddings`,
  `POST /projects/{project_id}/knowledge/search` e
  `POST /projects/{project_id}/knowledge/ask`.
* Migration `c91e5a4f2d08` para extensão pgvector, embeddings e índice vetorial.
* Testes unitários e de integração para extração, chunking, persistência, estados,
  indexação, recuperação, grounding, rastreabilidade, autorização e respostas de erro.

### Alterado
* Metadados e pacote da API avançam para `0.5.0`.
* Processamento documental passa por `UPLOADED → PROCESSING → READY`; falhas de
  storage ou extração terminam em `FAILED` sem reduzir os controles da v0.4.1.

## [0.4.1] — 2026-07-30 — Security Gate

### Adicionado
* Foundation Pack v1.0 — governança, protocolo de colaboração entre IAs (`.ai/`), 7 novos ADRs (`ADR-0002` a `ADR-0008`) e documentação institucional completa (`GOVERNANCE.md`, `AGENTS.md`, `CONTEXT.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`).
* v0.4.1 Security Gate com cadastro seguro, login, JWT HS256 assinado, expiração,
  cookie HttpOnly, autorização centralizada e matriz de acesso.
* Migration `8a1c4e2f9b30` para armazenar hash de senha preservando usuários existentes.
* Login frontend e lockfile pnpm reproduzível.
* Validação de upload PDF por extensão, MIME e assinatura `%PDF-`.

### Segurança
* `X-User-ID` não autentica mais usuários.
* Cadastro público força o papel `member` e rejeita `role`.
* Criação de projeto deriva `owner_id` exclusivamente do token validado.
* Rotas de usuários, projetos, arquivos, documentos, chats e IA exigem autenticação
  e aplicam regras de papel/propriedade.

### Alterado
* **Breaking:** `POST /users` exige `password` e não aceita `role`.
* **Breaking:** `POST /projects` não aceita `owner_id`.
* **Breaking:** rotas protegidas exigem cookie de sessão ou
  `Authorization: Bearer <token>`.
* CI frontend passa a usar pnpm com `--frozen-lockfile`.
* Recursos documentais de projetos inacessíveis retornam `404`, em alinhamento
  com a matriz de autorização e sem confirmar a existência do recurso.
* Relacionamentos ORM usam imports protegidos por `TYPE_CHECKING`, permitindo
  validação mypy integral da aplicação.
* O contexto Docker do frontend exclui `node_modules`, `.next`, ambientes e logs.

---

## [0.4.0] — 2026-07-17 — Upload & Base de Conhecimento

### Adicionado
* Infraestrutura base do módulo Documents, com modelo SQLAlchemy, schemas Pydantic, repository, service e Dependency Injection request-scoped.
* CRUD lógico de Documents e migration Alembic `4c3d8f1a2b7e`.
* Armazenamento físico de Documents no MinIO, com upload multipart, download, remoção e verificação de existência na camada Storage, sem processamento ou IA.
* Gerenciamento de Documents por projeto, com relacionamento ORM `Project (1) — (N) Documents`, contagem, validação de pertencimento e exclusão coordenada entre banco e MinIO.
* Proteções de upload para sanitização de nomes, limite real de tamanho, Content-Type, isolamento por proprietário e respostas HTTP seguras para falhas de storage.
* Infraestrutura do pipeline de Documents com estados `UPLOADED`, `PROCESSING`, `READY` e `FAILED`, sem leitura ou processamento de conteúdo.
* Catálogo administrativo de Documents com filtros por estado e estatísticas agregadas de quantidade e armazenamento, sem busca ou processamento de conteúdo.

### Alterado
* Metadados da API atualizados para `0.4.0`.
* Engine SQLAlchemy e Alembic alinhados à variável oficial `DATABASE_URL`, permitindo conexão correta da API no Docker Compose.

---

## [0.3.0] — 2026-07-16 — IA Base

### Adicionado
* AI abstraction layer em `packages/ai`, com contratos tipados para providers, factory e service sem registry global.
* Provider OpenAI com suporte a chat, embeddings e completion.
* Rotas FastAPI `GET /ai/providers` e `POST /ai/{provider}/{chat|embeddings|completion}` com Dependency Injection.
* Mapeamento de erros de provider para HTTP 400, 404, 502 e 503.
* Testes automatizados da AI Layer, totalizando 21 testes aprovados na API.

### Alterado
* AI Layer formalizada como pacote Python instalável na versão `0.3.0` e incluída no runtime Docker da API.
* Backend CI ampliado para mudanças em `packages/ai`, com `ruff`, `mypy` e `pytest` em Python 3.13.
* Metadados da API atualizados para `0.3.0`.

---

## [0.1.0] — 2026-07-10 — Foundation

### Adicionado
* Documentação fundadora: `PROJECT.md`, `docs/adr/ADR-001.md`, `docs/ROADMAP.md`, `docs/DECISIONS.md`.
* Estrutura inicial do monorepo: `apps/`, `packages/`, `services/`, `docs/`, `tests/`, `docker/`, `scripts/`, `.github/`.
* Scaffold de backend (`apps/api`, FastAPI) com endpoint `/health` e rotas iniciais de usuários, projetos, arquivos e chat.
* Scaffold de frontend (`apps/web`, Next.js) com tela inicial em formato de console técnico.
* `docker-compose.yml` com PostgreSQL + pgvector, Redis, MinIO, API e Web.
* Templates de issue e Pull Request, workflows iniciais de CI.
* Repositório publicado publicamente em `github.com/VenancioMarcos/vena-ia-platform`.

### Decidido
* Arquitetura Modular Monolith (`ADR-001`).
* Organização em monorepo (`DEC-004`).
* Stack tecnológica inicial (`DEC-005`).
* Escopo do MVP v1.0 (`DEC-006`).

---

## Convenção de Versão

* **MAJOR** — mudança incompatível na plataforma ou na arquitetura fundamental.
* **MINOR** — nova versão executiva do roadmap (v0.2 Core, v0.3 IA Base etc.) ou funcionalidade relevante.
* **PATCH** — correções e ajustes que não alteram escopo funcional.
