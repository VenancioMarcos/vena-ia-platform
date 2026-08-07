# CHANGELOG.md

Todas as mudanças relevantes do Vena_IA Platform são registradas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/) e versionamento [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Adicionado — v1.8 Package 3
* Contrato `vena-ia.geometry-features/v1` e recognizer OCCT rule `1.0.0`
  distinguem primitivas planares/cilíndricas de furo cilíndrico passante estrito.
* Corpus sintético reproduzível valida dimensões, determinismo, falsos positivos,
  falso negativo suportado, topologia inválida e erro seguro, sempre com revisão humana.
* Furo cego, slot, CAM, toolpath, G-code e inferência de manufaturabilidade permanecem adiados.

### Adicionado — v1.8 Package 2
* Gate `GO_CONTROLLED_INTEGRATION` fixa cadquery-ocp 7.9.3.1.1/OCCT 7.9.3,
  com import lazy, limites, erros seguros e autoridade geométrica separada do parser textual.
* STEP real passa a fornecer bounding box topológica, área, volume somente sólido,
  validade e shape básico, validados por corpus analítico; tolerância industrial permanece indisponível.

### Adicionado — v1.8 Package 1
* ADR-0015 aprova OpenCascade para integração controlada com restrições, sem
  instalar dependência pesada antes dos gates multiplataforma.
* Contrato `vena-ia.geometry-analysis/v1` representa resultados indisponíveis
  explicitamente, sem inventar área, volume, topologia ou tolerância.

## [1.7.0] — 2026-08-06 — Engineering Catalogs and CAM

### Adicionado — v1.7 Package 3
* Relatório `vena-ia.engineering-review-report/v1` reutiliza a recomendação do
  Package 2 e consolida conclusão fechada, incerteza informacional, ausências,
  rastreabilidade e checklist humano sem autorizar processo ou máquina.

### Adicionado — v1.7 Package 2
* Contrato `vena-ia.engineering-recommendation/v1` e rota autenticada para regras
  determinísticas allowlisted de milling, drilling e turning.
* Compatibilidade preliminar, RPM/feed, tempo e custo retornam fonte, versões,
  fórmulas, unidades, hipóteses, limitações e `NOT_AVAILABLE` quando faltam dados.
* Nenhuma recomendação contém toolpath, coordenadas, G-code, M-code ou comando CNC.

### Adicionado — v1.7 Package 1
* Contratos versionados `vena-ia.engineering-catalog/v1` e
  `vena-ia.engineering-selection/v1` para materiais, máquinas e ferramentas.
* Catálogo persistente com fonte, versão e propriedades rastreáveis, repository,
  service e APIs autenticadas de cadastro, consulta e seleção preliminar.
* Toda seleção usa `PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW`; não há
  toolpath, G-code executável, envio ou controle de máquina.

## [1.6.0] — 2026-08-06 — Reliability and Scalability

### Corrigido — v1.6 Package 3 R1
* Evidência anterior reclassificada como `HARNESS_ONLY_BASELINE`; o gate terminal
  agora inicia API A/API B e Worker A/Worker B como processos independentes com
  PostgreSQL/pgvector, Redis e MinIO compartilhados.
* Controlled Capacity CI proíbe providers memory, aplica Alembic e comprova por HTTP
  auth/revogação/rate limit/idempotência, jobs/claims/leases, MinIO, RAG,
  cancelamento/retry, isolamento, backpressure e soak integrado de 30 segundos.
* Bundle de evidência recebe criação exclusiva/atômica, recusa de overwrite,
  proteção contra symlink/traversal, flush/fsync, checksum e cleanup em falha.
* O entrypoint independente do worker agora registra todos os modelos ORM antes do
  reconciliador. Isso elimina o `InvalidRequestError` que permitia heartbeat, mas
  bloqueava a primeira consulta PostgreSQL e, consequentemente, todos os claims.
  O CI preserva diagnóstico allowlisted e só publica evidence PASS após sucesso.
* O Controlled Capacity CI passa a observar mudanças no worker/jobs; Backend,
  Frontend e Runtime Policy recebem disparo manual para revalidação explícita de um
  mesmo HEAD sem alterar os gates executados.

### Adicionado — v1.6 Package 3
* Perfil `vena-ia.capacity-profile/v1`, harness bounded e evidência
  `vena-ia.capacity-evidence/v1` checksummed fora do repositório.
* Controlled Capacity CI executa carga/soak curtos, E2E determinístico e guardrails
  com dados sintéticos, provider local e serviços fixados.
* Relatório de gargalos documenta worker unitário, limite IA por processo, serviços
  compartilhados, telemetria efêmera e timeout cooperativo sem alegação produtiva.

### Adicionado — v1.6 Package 2
* Contrato executável `vena-ia.resilience-policy/v1`, inventário e policy check
  fail-closed para budgets de API, PostgreSQL, Redis, MinIO, IA, worker e backup.
* Classificação reutilizável de falhas, deadline global, attempts limitados,
  backoff exponencial com teto/jitter e suporte bounded a `Retry-After`.
* Limite de concorrência de IA por processo sem fila ilimitada, resposta 503 segura
  e drill determinístico com vinte cenários de falha, saturação e recuperação.

### Alterado — v1.6 Package 2
* Provider OpenAI valida resposta vazia/malformada e vetores não finitos; somente
  falhas temporárias allowlisted recebem retry e nenhum provider alternativo é usado.
* PostgreSQL e MinIO recebem budgets explícitos; jobs ganham teto de backoff e jitter.
  O timeout do worker continua cooperativo e a migração permanece inalterada.

### Adicionado — v1.6 Package 1
* Manifesto executável `vena-ia.runtime-policy/v1`, matriz oficial e policy check
  fail-closed alinham Python, Node, pnpm, Dockerfiles, Compose, CI e lockfile.
* Runtime Policy CI valida configuração e constrói API/Web a partir de imagens-base
  fixadas por versão e digest imutável.
* Runbook versionado define revisão, proveniência, licença, compatibilidade de dados
  e rollback sem merge ou atualização automática.

### Alterado — v1.6 Package 1
* Python 3.13.11 é oficial; Python 3.14.6 permanece experimental após regressão
  local. Node 22.20.0, pnpm 11.9.0 e pip 26.1.2 passam a ser explícitos.
* PostgreSQL/pgvector, Redis, MinIO, Python e Node deixam de usar referências
  flutuantes; GitHub Actions são fixadas por commit.
* Dockerfile Web usa pnpm frozen e build/start de produção; API/Web executam como
  usuários não privilegiados, com healthchecks, e o worker reutiliza a imagem API.

### Segurança — v1.6 Package 1
* `latest` é proibido por teste; `.env`/segredos não entram em contextos ou
  evidências. A ausência de scanner/SBOM e lock Python transitive permanece
  documentada, sem alegação de ausência completa de vulnerabilidades.
* Scripts de instalação frontend ficam bloqueados por padrão; somente `sharp` e
  `unrs-resolver`, exigidos pelo build validado, integram a allowlist pnpm.

## [1.5.0] — 2026-08-05 — Asynchronous Processing

### Adicionado — Package 2
* Reconciliador automático reconstrói o transporte Redis a partir dos jobs não
  terminais no PostgreSQL e recupera `RUNNING` sem lease, retry vencido,
  cancelamento pendente e fila perdida após reinício.
* Enqueue, recuperação de lease e acknowledge passam a ser atômicos/idempotentes;
  renovação periódica mantém o lease durante bibliotecas síncronas longas.
* Extração PDF reporta progresso por página e admite cancelamento cooperativo entre
  páginas. O documento só fica `READY` depois da persistência e indexação completas.
* Códigos seguros distinguem PDF criptografado, sem texto ou inválido, recurso
  removido, dependência indisponível, timeout, cancelamento, lease perdido e retry
  esgotado, sem stack, caminho, conteúdo ou detalhe de infraestrutura.
* Drills e testes sintéticos cobrem reinício, concorrência, duplicação, efeitos
  parciais, 500 páginas, Redis real e falhas controladas de dependências.
* Avaliação formal de OCR classifica a tecnologia como adiada; nenhum motor,
  serviço, dependência, GPU ou envio externo foi introduzido.

### Adicionado — Package 1
* Contrato durável `vena-ia.job/v1` com proprietário, projeto, recurso, progresso,
  tentativas, timeout, idempotência derivada, correlação, erros seguros e estados
  terminais protegidos por transições atômicas.
* Migration `b18e4c7d2a91` cria jobs e índices bounded para autorização, operação,
  disponibilidade e unicidade idempotente no PostgreSQL.
* Fila Redis com claim exclusivo, ack, delayed retry/backoff, lease, recuperação de
  abandono e heartbeat; o modo em memória é exclusivo de desenvolvimento/teste.
* Worker do Modular Monolith para extração/chunking PDF allowlisted, com progresso,
  cancelamento cooperativo, timeout, graceful shutdown e falha segura.
* Endpoints autenticados para iniciar processamento assíncrono, consultar, cancelar
  e repetir jobs; a interface mostra estado, progresso e controles mínimos.
* Logs correlacionados, métricas de cardinalidade fechada, alertas, spans, auditoria
  persistente e readiness do worker sem conteúdo ou IDs de domínio em labels.

### Segurança
* A fila não transporta documento, prompt, resposta, embedding, segredo ou código;
  `X-User-ID` permanece sem função de identidade e acesso cruzado retorna `404`.
* OCR continua ausente. PDFs sem texto falham explicitamente, sem resposta inventada.

## [1.4.0] — 2026-08-04 — Observability and Auditability

### Adicionado
* Drill operacional controlado para onze cenários de incidente e recuperação,
  com contrato `vena-ia.incident-drill/v1`, request/correlation IDs, métricas,
  alertas locais, spans, eventos de auditoria aplicáveis e respostas seguras.
* Bundle opcional de evidência JSON determinístico, armazenado fora do repositório,
  com SHA-256, recusa de overwrite, traversal e symlink, sem logs brutos ou dados
  de usuário.
* Limiares configuráveis e validados para falhas repetidas de autenticação,
  rate limit, processamento, readiness, dependências e erros internos.
* Contrato `vena-ia.metrics/v1` com counters, gauge de readiness, histogramas,
  labels/buckets fechados, reset de testes e coletor local thread-safe/fail-open.
* Endpoint administrativo `GET /internal/metrics`, desabilitado por padrão e
  exposto somente por configuração explícita e autenticação/autorização admin.
* `request_id` e `correlation_id` persistidos nos eventos de auditoria, com
  correlação de autenticação e mutações de projeto, documento, processamento,
  indexação, chat, relatório e administração.
* Contratos locais substituíveis de alertas com severidade, cooldown,
  deduplicação e contexto allowlisted, sem transporte externo.
* Fundação de tracing local com spans pai/filho, duração, estado e erro controlado,
  usando providers no-op/local e sem exportação.
* Middleware com schema `vena-ia.observability/v1`, eventos JSON allowlisted,
  duração, rota normalizada, request ID e correlation ID.
* Headers `X-Request-ID` e `X-Correlation-ID` validados/gerados e propagados em
  respostas, contexto de serviço e erros internos genéricos.
* `GET /ready` verifica PostgreSQL, Redis e MinIO sem expor diagnóstico sensível;
  `/health` preserva o contrato existente.

### Segurança
* A evidência do drill usa allowlist e rejeita credenciais, IDs de domínio,
  conteúdo documental/IA e stack traces; artefatos gerados permanecem ignorados.
* Labels de alta cardinalidade e dados sensíveis são recusadas nas métricas;
  alertas e spans não aceitam conteúdo de usuário, credenciais ou IDs de domínio.

### Corrigido
* Testes reais de backup/restore deixam de fixar um Alembic head histórico:
  derivam o head único do grafo oficial, exigem que o manifesto o capture e
  confirmam que o banco restaurado preserva exatamente o schema manifestado.
* Redaction e allowlist proíbem Authorization, Cookie, JWT, senha, segredo,
  conteúdo documental, prompts, respostas e embeddings nos eventos.

## [1.3.0] — 2026-08-02 — Backup, Recovery and Retention

### Adicionado
* Bundle `vena-ia.encrypted-backup-set/v1` com AES-256-GCM autenticado, chave
  externa, `key_id` não sensível, streaming, recusa de algoritmo desconhecido e
  cleanup de plaintext temporário após sucesso ou falha.
* Retenção executável por quantidade/idade e classes diária, semanal e mensal,
  com dry-run padrão, proteção, validação integral e preservação do último set.
* Job operacional com lock exclusivo, timeout e worker interno idempotente para
  cron/Task Scheduler, sem daemon próprio ou agendamento real automático.
* Recovery drill criptografado mede backup, restore, RPO técnico do cenário e
  RTO observado usando PostgreSQL/pgvector e MinIO descartáveis no CI.
* Contrato `vena-ia.minio-backup/v1` com exportação determinística de objetos,
  metadados seguros, SHA-256 por conteúdo e restauração controlada em destino vazio.
* Contrato `vena-ia.backup-set/v1` que relaciona PostgreSQL e MinIO pelo mesmo
  identificador, instante, versão e validação de objetos ausentes, órfãos e isolamento.
* Round trip descartável combinado no CI, incluindo perda simulada, restauração
  dos dois stores, migration head e prova de integridade dos metadados e conteúdos.
* Contrato `vena-ia.postgresql-backup/v1` com dump custom-format, manifesto,
  SHA-256, migration head e identificação do conjunto.
* Scripts seguros de backup e restore PostgreSQL: artefatos fora do repositório,
  senha somente por ambiente, alvo vazio e confirmação/allowlist explícitas.
* Testes de contrato e round trip descartável para backup, perda simulada,
  restore e verificação mínima de integridade sem dados reais.

### Segurança
* `cryptography==49.0.0` fornece AES-256-GCM; a chave permanece exclusivamente em
  ambiente/arquivo protegido e nenhum valor padrão ou material de chave é versionado.
* Restore MinIO valida contrato, paths, tamanho e checksum de todos os artefatos
  antes de mutar o destino; exige confirmação/allowlist e remove escrita parcial.
* Credenciais MinIO permanecem exclusivamente no ambiente e nunca integram
  argumentos, manifestos, logs ou artefatos versionados.

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
