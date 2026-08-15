# CONTEXT.md — Contexto Operacional do Projeto Vena_IA Platform

**Status:** Documento Oficial
**Versão:** 2.5
**Última atualização:** 2026-08-15
**Documentos relacionados:** `PROJECT.md`, `AGENTS.md`, `.ai/ACP.md`, `docs/PERMANENT_OPERATIONAL_LIMITS.md`

---

## 1. Propósito deste documento

O `CONTEXT.md` existe para eliminar perda de contexto entre sessões de trabalho e entre diferentes agentes de IA (ChatGPT, Claude, Codex, GitHub Copilot, Gemini, agentes próprios).

Antes de qualquer IA iniciar uma tarefa neste repositório, ela deve ler este documento. Ele resume o estado atual do projeto de forma que qualquer agente — humano ou artificial — consiga retomar o trabalho sem depender de memória de conversas anteriores.

Este documento é atualizado sempre que uma mudança relevante de estado ocorre (nova fase concluída, nova decisão arquitetural, mudança de prioridade).

---

## 2. O que é a Vena_IA Platform

Plataforma de Inteligência Artificial aplicada à Engenharia Mecânica e Manufatura CNC, com três frentes simultâneas: produto de software comercial, base científica para pesquisa acadêmica e ativo estratégico de automação para o ecossistema Vena_IA.

Missão, visão e objetivos estratégicos completos estão em `PROJECT.md`.

---

## 3. Estado atual do projeto

* **TASK-V31-007B — TESTE_01 real browser path completed:** the verified public
  `TESTE_01_cube.stp` input completed authenticated browser orchestration through
  geometry/topology evidence, Manufacturing Geometry, verified Process Plan, bounded
  Toolpath, Level-2, G0–G8 and the immutable Digital Thread. The first controlled
  candidate was downloaded as `vena-ia-fd23a2b2dec85a45.candidate.nc` with SHA-256
  `fd23a2b2dec85a4522082e7992dfd5ab90171080fc736a28be9967387986cb49`.
  The API image includes the OpenGL runtime required by OCP, and only the controlled
  CAD call receives the longer bounded browser timeout. G9 remains pending;
  controlled-validation readiness and physical-use authority remain false.

* **TASK-V31-007B — STEP browser MIME compatibility:** the local v3.1 API accepts
  `application/octet-stream` only for `.step`/`.stp` after bounded-size, STEP header
  and terminal-marker validation, then stores the canonical `application/step`
  content type. Focused document tests, Ruff and mypy pass; PostgreSQL, Redis, MinIO,
  worker readiness and API `3.1.0` remain operational after an API-only rebuild.
  The real UI TESTE_01 must resume with the same verified cube input; G9 remains
  pending and controlled-validation/physical-use authority remain false.

* **TASK-V31-006 — First Controlled CAD-to-G-code Test Path:** the v3.1 line now
  verifies a runtime-generated STEP cylinder through real upload/storage/CAD services
  and the complete controlled API chain, without predeclaring expected features. The
  browser exposes Manufacturing Geometry, Process Plan, Toolpath, Level-2 and Digital
  Thread artifacts and requires an explicit non-production acknowledgement before
  download. No GitHub/Vercel deployment configuration or environment exists, so no
  external infrastructure was invented; the verified web target is the existing local
  controlled environment. G9/readiness/physical authority remain pending/false.

* **Release v3.1.0 — NON_PRODUCTION:** PR #30 was Squash Merged at `64ac3b8`; the
  annotated tag and GitHub Release `v3.1.0` are published. Post-merge Backend,
  Frontend and Runtime Policy CI passed. No deploy or v3.2 was started.

* **Release Candidate v3.1.0 — NON_PRODUCTION:** API/FastAPI/health/OpenAPI and
  frontend versions are aligned at `3.1.0`; release notes consolidate the Controlled
  Test Environment and deterministic G9 Review Package. Draft PR #30 remains the
  release gate. G9 is pending, readiness/physical authority are false and no deploy,
  external validation, machine interface or v3.2 is included.

* **TASK-V31-004 — G9 Review Package:** the existing controlled run now returns
  deterministic `vena-ia.g9-review-package/v1`, hash-bound to the candidate, Digital
  Thread, blind bundle, G0-G8, Level-1/Level-2 and exact contract/component versions.
  It consolidates human-review and external-validation protocols without accepting
  reviewer authority or external disposition. G9 remains pending; readiness and
  physical authority remain false. No persistence, migration, machine integration,
  deploy or v3.2 was introduced.

* **TASK-V31-003 — G9/external-validation preparation:** the v3.1 implementation was
  audited without creating a G9 transition. `docs/G9_EXTERNAL_VALIDATION_PREPARATION.md`
  separates automatic integrity evidence, authoritative human review evidence,
  independent external-simulation evidence and the separately authorized prerequisites
  for any physical test. Focused assurance covers body/query/header forgery, proof
  expiry, revoked membership, cross-Organization access and artifact tampering.
  G9 remains `PENDING_AUTHORITATIVE_REVIEW`; controlled-validation readiness and
  physical authority remain false.

* **TASK-V31-002 — Controlled Test Environment implementada:** a branch
  `codex/v3.1-controlled-test-environment` compõe a cadeia autorizada
  CAD→evidências→Manufacturing Geometry→Process Plan→Toolpath bounded→postprocessor
  sintético→Level-1/Level-2→blind evidence→Digital Thread→download controlado. Token,
  membership ativa e escopo organizacional são autoridade; prova HMAC curta vincula
  usuário/organização/hashes e o download revalida integridade. G0–G8 passam somente
  com evidence; G9 segue `PENDING_AUTHORITATIVE_REVIEW`.
  `PHYSICAL_USE_AUTHORIZED=false`; não existem machine-send, DNC/NC transfer, cycle
  start, controle direto ou bypass de human review. Não há migration, merge, release,
  deploy ou início de v3.2 nesta missão.

* **Release v3.0.0 publicada:** a PR #29 foi integrada em `f2ffe5c`; tag anotada e
  GitHub Release publicam Manufacturing Intelligence & Digital Thread.
  `vena-ia.digital-thread/v1` encadeia artifacts
  imutáveis/versionados com ownership organizacional, hashes, refs, provenance,
  lifecycle e replay, sem banco/ledger/migration nova. A inteligência bounded é
  read-only, sem tools, não altera evidence nem gates. Cross-org, hash/ref/version
  divergentes, stale e forged artifacts falham fechado. G9 continua
  `PENDING_AUTHORITATIVE_REVIEW`; readiness e physical authority continuam false.
* **Release v2.3.0 publicada:** PR #28 integrada em `91d20f4`; tag anotada e GitHub
  Release publicam a fronteira técnica controlada com G9 pendente e zero autoridade
  física.

* **Release Candidate v2.3.0:** Packages 1–3 e a correção de authority G9 estão
  aprovados pelo CTO na Draft PR #28. API/health/OpenAPI/frontend estão alinhados em
  2.3.0; release notes registram a fronteira técnica não produtiva. G9 permanece
  `PENDING_REVIEW`, readiness e physical authority permanecem false. A publicação
  técnica não concede machine-send, NC/DNC, cycle start ou controle CNC.

* **TASK-V23 Package 3 pronta para revisão:** a branch
  `codex/v2.3-controlled-cad-gcode-validation` e a Draft PR #28 acrescentam
  `level2-material-removal-evidence/v1` e o harness
  `controlled-blind-validation/v1`. O verificador Level-2 reconstrói a trajetória
  sem chamar gerador/verificador Level-1 e falha fechado para stock/evidence,
  cobertura, continuidade, gouge, rapid e fixture keep-out. O harness congela
  hashes e G0–G9; G9 real permanece `PENDING_REVIEW`, portanto
  `CAD_TO_GCODE_CONTROLLED_VALIDATION_READY=FALSE` e
  `PHYSICAL_USE_AUTHORIZED=FALSE`. A API pública não aceita `human_review` nem pode
  derivar reviewer/decision/evidence authority do body; qualquer futura promoção de
  G9 exige estado autoritativo resolvido no servidor. Não há migration, merge,
  release ou v3.0.

* **Release v2.2.0:** PR #27 integrada por Squash Merge em `28d592c`; versões
  API/FastAPI/health/OpenAPI/frontend estão alinhadas em `2.2.0`, sem migration
  nova (head `e61c4f8a2b90`). A release mantém planning determinístico e não
  produtivo; v2.3 é a próxima fronteira formal de toolpath/G-code candidato.
* **Integração documental PR #26/#27 concluída:** a PR #26 foi encerrada como
  substituída somente após o blob da Gap Analysis ser comprovado byte a byte na
  PR #27 (`27cb85167c22aca6e9719c872d202981b387b75d`).

* **TASK-V22-002 — v2.2 Package 2 pronta para revisão:** a mesma branch/PR #27
  adiciona `manufacturing-geometry-model/v1`, `verified-process-plan/v1` e
  `planning-verification-evidence/v1`. Stock é obrigatório/provenanced, regiões
  externas ao envelope são decompostas sem sobreposição, superfícies finais ficam
  protegidas e material interno desconhecido não é inventado. Acesso/datum/WCS/setup
  são somente candidatos 3-axis/2.5D. Intent e recursos autorizados são gates; não
  há toolpath, postprocessor, G/M-code ou simulação física.
* **Integração documental PR #26/#27:** a Gap Analysis histórica foi portada
  integralmente para `docs/CAD_TO_GCODE_GAP_ANALYSIS_v1.md` na linha v2.2. Os
  documentos de estado da PR #27 são a continuação oficial; a PR #26 pode ser
  encerrada como redundante somente após confirmar o blob remoto preservado.

* **TASK-V22-001 — v2.2 Package 1 pronta para revisão:** a branch
  `codex/v2.2-general-geometry-evidence` adiciona
  `vena-ia.geometry-topology-evidence/v1` ao endpoint CAD autorizado. O read model
  efêmero reutiliza o mesmo carregamento OCCT, registra hash/provenance, unidades,
  transformação, tolerâncias e topologia geral com IDs canônicos/replay. Unidade
  ambígua, topologia inválida e limite excedido falham fechado. Package 2 não foi
  iniciada; não há migration, manufacturing intent ou output CNC executável.
* **Roadmap aprovado pelo Owner:** v2.2 → v2.3 → v3.0. A prioridade operacional é
  `FIRST_CONTROLLED_CAD_TO_GCODE_VALIDATION > VERSION_NUMBER`; cada Package ainda
  exige sua missão técnica e seus gates. Autoridade física continua inexistente.

* **Fase:** v0.1–v2.0 concluídas e publicadas. Os três Packages oficiais da v2.0
  foram aprovados, integrados e publicados como v2.0.0 após o Owner Release Gate.
* **Roadmap pós-v2.0:** `DEC-037` foi ampliada pela autorização direta do Owner para
  v2.1 → v2.2 → v2.3 → v3.0. A v2.2 Package 1 está implementada; Packages seguintes
  permanecem fora desta missão.
* **v2.1 Package 1 implementado:** catálogos Engineering agora são organization-scoped;
  membership ativa lê e OWNER/ADMIN cria. `SYSTEM_REFERENCE` é read-only e dados
  preexistentes viram `LEGACY_UNSCOPED` oculto, sem atribuição arbitrária. A migration
  head é `e61c4f8a2b90`; Package 2, v2.2 e v3.0 permanecem `NOT_STARTED`.
* **v2.1 Package 2 implementado:** governance evidence read-only compõe metadados
  autorizados e políticas técnicas de lifecycle/retention/deletion/reconciliation.
  Sem ledger, persistência, migration, bulk export ou frontend. v2.1 está funcionalmente
  completa, pendente de revisão/Release Candidate; v2.2 e v3.0 seguem `NOT_STARTED`.
* **Release v2.1.0:** Packages 1–2 aprovados; não existe Package 3. Versões
  API/FastAPI/health/OpenAPI/frontend estão alinhadas em `2.1.0`, migration permanece
  `e61c4f8a2b90` e release notes estão publicadas. A PR #25 foi integrada por Squash
  Merge em `f5d6775`; tag e GitHub Release `v2.1.0` encerram a versão sem deploy.
  A v2.2 Package 1 está implementada em branch separada e aguarda revisão do CTO.
* **Fluxo operacional:** `AUTONOMOUS_CTO_CODEX_OPERATION = ACTIVE` para operações
  técnicas rotineiras formalmente aprovadas pelo CTO. Ações materialmente não
  delegáveis e limites permanentes continuam exigindo o gate aplicável.
* **v1.9 Package 1 implementado:** branch
  `codex/v1.9-controlled-pilot-readiness` adiciona Organization/Team,
  memberships `OWNER`/`ADMIN`/`MEMBER`, bootstrap owner transacional, revogação,
  contexto sintético e readiness/privacy. JWT + banco são a única autoridade;
  cross-org/team, mass assignment, papel/body/header forjados e `X-User-ID` falham
  fechados. Migration head `d39a7b2c5e11`; deploy e piloto real continuam proibidos.
* **v1.9 Package 2 implementado:** a mesma Draft PR #21 orquestra evidência
  sintética allowlisted, false-readiness fail-closed, rollback explícito e validação
  CNC virtual não executável. Checksum prova somente integridade canônica; Package 2
  exige revisão humana e não representa piloto, produção, SLA ou deploy.
* **Release v1.9.0:** a PR #21 foi integrada por Squash Merge em `b149ac1`; o
  fechamento de release `1d3c383`, a tag anotada e a
  [GitHub Release](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.9.0)
  registram Packages 1–2 completos, versões
  API/FastAPI/health/OpenAPI/frontend `1.9.0` e Alembic `d39a7b2c5e11`. R-042 e
  R-043 continuam residuais/monitorados; nenhum deploy ou piloto real foi realizado.
* **v2.0 TASK-V20-001:** o CTO aprovou a decomposição em três Packages e a DEC-035.
  O Package 1, workflow determinístico integrado, está `APPROVED_FOR_IMPLEMENTATION`;
  assistência especializada/Research grounded e dashboard/evidence/E2E permanecem
  `NOT_STARTED`. A PR documental #22 deve ser integrada antes da branch funcional.
  Migration, deploy e CNC executável não estão autorizados.
* **v2.0 Package 1 implementado:** a branch
  `codex/v2.0-integrated-engineering-platform` adiciona o aggregate
  `vena-ia.integrated-engineering-workflow/v1`, formaliza
  `vena-ia.cnc-neutral-plan/v1` e reutiliza CAD/features, Engineering,
  FeaturePlanningBridge, CNC preview e report builder. O fluxo analisa STEP uma vez,
  mantém missing inputs/unsupported/incompatibility explícitos, exige revisão humana
  e nunca produz output executável. Não há nova persistência ou migration; catálogos
  continuam globais autenticados. A Draft PR #23 está aberta; o Backend CI do head
  funcional/documental `394786e` aprovou lint, mypy, ciclo Alembic, 341 testes da
  API e 76 testes operacionais reais. Packages 2 e 3 permanecem `NOT_STARTED`.
* **v2.0 Package 2 implementado:** a mesma branch/PR #23 adiciona assistência
  especializada bounded sobre o snapshot imutável do Package 1 e bridge Research
  `vena-ia.grounded-research-assistance/v1`. Quatro perfis allowlisted usam
  `AIService`, Documents/RAG e Research existentes; contexto é minimizado, citações
  preservam documento/página/chunk/método, ausência falha fechado e output do modelo
  não pode mutar fatos ou produzir CNC executável. R-046/R-047 estão mitigados
  parcialmente/monitorados. O Backend CI do head `04cf56a` aprovou lint, mypy em
  168 arquivos, ciclo Alembic, 349 testes API e 76 operacionais. Sem persistence,
  migration ou frontend; Package 3 permanece `NOT_STARTED` e v2.0 não está encerrada.
* **v2.0 Package 3 implementado:** a mesma Draft PR #23 adiciona dashboard
  operacional tipado para workflow/assistance/Research, estados explícitos, evidence,
  citações e checklist humano sem autoridade produtiva. Playwright cobre desktop e
  largura reduzida, caminho integrado e falhas controladas. Versões API/FastAPI/
  health/OpenAPI/frontend estão em `2.0.0`; Alembic permanece `d39a7b2c5e11`.
  Packages 1–3 estão aprovados. A PR #23 foi integrada por Squash Merge em
  `67714d4`; a tag anotada e a GitHub Release `v2.0.0` registram a versão como
  `RELEASED`. Deploy não foi realizado.
* **v1.8 Package 2:** integração controlada cadquery-ocp/OCCT atrás de adapter
  valida STEP real contra box sintético. Parser textual preserva metadados; kernel
  é autoridade apenas para propriedades calculadas. R-019/R-038 seguem monitorados.
* **v1.8 Package 3:** rule `1.0.0` consome a topologia já carregada e expõe
  `vena-ia.geometry-features/v1`. Faces planares/cilíndricas são primitivas; furo
  passante exige boundary interno e atravessamento axial estrito. Furo cego e slot
  foram adiados para evitar falsos positivos. Toda saída exige revisão humana e não
  alimenta seleção de máquina/ferramenta, CAM, toolpath ou G-code.
* **v1.8 Package 4:** `vena-ia.feature-planning/v1` conecta feature pertencente ao
  usuário a candidato preliminar. Apenas through hole produz
  `DRILLING_CANDIDATE`; demais primitivas falham fechadas. Material/máquina/ferramenta
  explícitos reutilizam a recommendation v1.7, ainda não executável e sob revisão humana.
* **Release v1.8.0:** a PR [#19](https://github.com/VenancioMarcos/vena-ia-platform/pull/19)
  foi integrada por Squash Merge em `a066c1c`. A tag anotada e a
  [GitHub Release](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.8.0)
  foram publicadas sem deploy. O release preserva revisão humana e não contém saída CNC executável.
* **Repositório:** público, em `github.com/VenancioMarcos/vena-ia-platform`.
* **Arquitetura:** Modular Monolith (`docs/adr/ADR-001.md`), com organização em `apps/`, `packages/`, `services/`.
* **Backend:** `apps/api` v1.8.0 com persistência SQLAlchemy, senha PBKDF2, JWT HS256 assinado, cookie HttpOnly/Bearer, expiração, autorização centralizada e controles distribuídos por Redis. `X-User-ID` não autentica. A migration head oficial é `c27f6d9e4a10`.
* **AI Layer:** `packages/ai` fornece contratos tipados, factory, service e provider OpenAI. Os endpoints de chat, embeddings e completion exigem usuário autenticado.
* **Documents/RAG:** upload e catálogo no MinIO continuam protegidos por proprietário/papel e restritos a PDFs validados. A v0.5 extrai texto por página com `pypdf`, cria chunks configuráveis, gera embeddings via AI Layer, persiste vetores em pgvector, recupera contexto por similaridade e produz respostas fundamentadas com rastreabilidade até documento, página e chunk.
* **CAD:** STEP Part 21 possui allowlist de extensão/MIME/assinatura e análise autenticada. O parser preserva metadados; cadquery-ocp/OCCT fornece propriedades topológicas controladas, features conservadoras e planning candidate não executável conforme ADR-0015.
* **Frontend:** `apps/web` possui cadastro/login, sessão por cookie HttpOnly, logout, tratamento consistente de erros e dashboard que cria projetos usando exclusivamente a identidade autenticada. Um cliente HTTP único normaliza erros FastAPI, aplica timeout de 30 segundos, não oculta falha de logout e mantém projeto/chat utilizáveis quando somente relatórios falham. Typecheck e build de produção foram aprovados.
* **Testes:** o release candidate v1.8.0 possui 370 testes aprovados e 9 skips condicionais na regressão local, cobrindo autenticação, ownership, infraestrutura, CAD/kernel/features/planning, Engineering e controles operacionais. O `TestClient` usa HTTPX2; Ruff e mypy integrais estão aprovados. Persistência unitária usa SQLite em memória (`DEC-011`); PostgreSQL continua oficial (`DEC-005`).
* **Infraestrutura e CI:** Docker Compose mantém PostgreSQL/pgvector, Redis, MinIO, API e Web. As imagens locais de API e Web foram construídas na revisão final; o frontend possui contexto Docker isolado de artefatos locais. CI backend executa Ruff, mypy e Pytest. CI frontend usa pnpm com lockfile congelado, typecheck e build.
* **Governança documental:** Foundation Pack v1.0 formaliza como múltiplas IAs colaboram no repositório.
* **Security Gate 2026-07-30:** riscos críticos R-001 a R-004 mitigados. A PR [#4](https://github.com/VenancioMarcos/vena-ia-platform/pull/4) foi integrada por squash e a release [v0.4.1](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v0.4.1) foi publicada. A matriz oficial está em `docs/AUTHORIZATION_MATRIX.md`; decisão em `docs/adr/ADR-0009-security-gate-authentication.md`.
* **RAG v0.5 2026-07-30:** extração textual de PDF, chunks rastreáveis, embeddings, pgvector, busca semântica e respostas fundamentadas foram integrados pela PR [#5](https://github.com/VenancioMarcos/vena-ia-platform/pull/5), conforme `docs/adr/ADR-0010-rag-foundation.md`. A validação pós-merge aprovou Ruff, mypy, 118 testes, frontend e Docker.
* **CAD Initial v0.6 2026-07-30:** upload STEP seguro e análise geométrica preliminar foram integrados pela PR [#6](https://github.com/VenancioMarcos/vena-ia-platform/pull/6), conforme ADR-0011. O parser não é kernel geométrico e mantém volume indisponível.
* **Engenharia/CAM v0.7:** primeira fundação calcula parâmetros preliminares de fresamento e tempo de corte a partir de material, ferramenta e limites de máquina. Saídas exigem revisão humana e não contêm toolpath ou G-code.
* **CNC v0.8:** primeira fundação representa planos neutros não executáveis. Fanuc Oi e Romi D1250 permanecem estratégias planejadas; não há G-code, transmissão ou liberação para máquina.
* **Pesquisa v0.9:** a fundação científica reutiliza documentos, chunks, RAG e autorização existentes. Artigos guardam apenas metadados; referências são heurísticas e auditáveis; sínteses permanecem fundamentadas; DOE exige revisão estatística; ANOVA é somente preparação descritiva; relatórios são rascunhos.
* **MVP v1.0:** cadastro/login, dashboard, projeto, upload PDF, processamento, embeddings, pergunta RAG, histórico persistente e relatório inicial formam um fluxo único no frontend e na API. Respostas do assistente guardam fontes e falhas não criam resposta falsa.
* **Release v1.0 2026-07-30:** a PR [#10](https://github.com/VenancioMarcos/vena-ia-platform/pull/10) foi integrada por squash após aprovação dos checks de backend e frontend. A validação pós-merge aprovou Ruff, mypy, 163 testes, frontend, migrations PostgreSQL e Docker. A release [v1.0.0](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.0.0) foi publicada e validada diretamente a partir da tag.
* **v1.1 Stabilization Package 1:** `TASK-V11-001` autorizou auditoria completa do fluxo principal. A Draft PR [#11](https://github.com/VenancioMarcos/vena-ia-platform/pull/11) corrige recuperação de documentos `FAILED`, retry de indexação no frontend e integridade verificável das evidências de relatórios; merge, tag e release permanecem fora desta missão.
* **v1.1 Stabilization Package 2:** `TASK-V11-002` mantém a mesma Draft PR #11 e corrige falhas operacionais reais do frontend: timeout contra carregamento infinito, cliente API duplicado, logout silencioso, erro de chat oculto, dependência indevida da listagem de relatórios para abrir o projeto e controles de navegação sem ação. Nenhuma arquitetura, migration ou funcionalidade estratégica foi adicionada.
* **v1.1 Stabilization Package 3:** `TASK-V11-003` reduz chamadas redundantes no fluxo principal: operações bem-sucedidas atualizam somente projetos, documentos, mensagens ou relatórios afetados; falhas sincronizam apenas o recurso necessário; requests iniciais são canceladas no unmount. A suíte substitui HTTPX legado por HTTPX2 e passa sem warnings. Contratos públicos, migrations e arquitetura permanecem inalterados.
* **Release v1.1.0 2026-08-01:** os três pacotes da PR [#11](https://github.com/VenancioMarcos/vena-ia-platform/pull/11) foram aprovados nos gates locais e no CI e integrados por Squash Merge em `1f5263f`. A release [v1.1.0](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.1.0) foi publicada sem deploy; a validação pós-merge e diretamente da tag aprovou 165 testes sem warnings, API/OpenAPI 1.1.0 com 47 rotas, frontend, Docker e migrations PostgreSQL.
* **Roadmap pós-v1.1:** `TASK-ROADMAP-V2-001` define v1.2–v2.0 por gates de risco em `docs/ROADMAP.md` e `DEC-016`. A v1.2 inicia somente pelo primeiro pacote de rate limiting para cadastro/login; v1.3 não pode iniciar antes da revisão da v1.2.
* **v1.2 Security Package 1:** a Draft PR [#13](https://github.com/VenancioMarcos/vena-ia-platform/pull/13) adiciona rate limiting configurável por cliente da conexão para cadastro e login, com janela fixa local, `429` e `Retry-After`. `POST /auth/register` e a compatibilidade `POST /users` compartilham o limite; `X-Forwarded-For` permanece ignorado sem fronteira de proxy confiável e `X-User-ID` nunca é usado. O controle local não elimina a exigência de gateway/limite distribuído para produção horizontal.
* **v1.2 Security Package 2:** a mesma Draft PR #13 passa a invalidar no processo os tokens apresentados no logout, rejeita reutilização posterior e tokens emitidos no futuro, preserva logout idempotente e melhora a mensagem frontend para `429`. Os 177 testes e os CI de backend/frontend estão aprovados. A denylist não é compartilhada entre réplicas nem persiste em reinício; revogação distribuída continua pendente antes de produção horizontal.
* **v1.2 Security Package 3:** contas legadas com `password_hash` nulo recebem credencial somente por admin, uma única vez e sem autoatendimento; `auth_version` invalida tokens anteriores após a definição. Eventos de login, limite, logout, token e operação administrativa são persistidos sem segredos e consultados apenas por admin. A retenção padrão documentada é 90 dias e a limpeza permanece operacional/manual nesta entrega.
  A Draft PR #13 está limpa e os CI finais de backend/frontend foram aprovados.
* **v1.2 Security Package 4:** Redis substitui os controles locais como padrão para rate limiting e revogação, compartilhando estado entre réplicas com operações atômicas e TTL. Origem e fingerprint não aparecem em texto puro nas chaves. Indisponibilidade falha fechada com `503` e auditoria; memória é modo explícito de desenvolvimento/teste. A validação inclui integração com Redis real e preserva `auth_version`.
  A Draft PR #13 aprovou Backend CI com PostgreSQL/Redis e Frontend CI/build.
* **Integração v1.2.0:** a PR [#13](https://github.com/VenancioMarcos/vena-ia-platform/pull/13) foi integrada por Squash Merge em `0e386802`. A `main` pós-merge aprovou Ruff, mypy, 193 testes locais, frontend e OpenAPI 1.2.0; a integração Redis foi aprovada no Backend CI. O Docker Desktop local permaneceu indisponível por erro de daemon/exportação, sem falha de código.
* **Release v1.2.0:** a tag anotada aponta para `663dbc2` e a [GitHub Release](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.2.0) foi publicada sem deploy.
* **v1.3 Backup Package 1:** branch `codex/v1.3-backup-recovery` adiciona contrato versionado, manifesto/checksum, backup PostgreSQL custom-format, restore somente em alvo vazio explicitamente confirmado e teste descartável de round trip. MinIO, nuvem, criptografia, agendamento e retenção automática permanecem fora do pacote.
  A Draft PR [#14](https://github.com/VenancioMarcos/vena-ia-platform/pull/14) aprovou o Backend CI com backup → restore real em PostgreSQL/pgvector descartável.
* **v1.3 Backup Package 2:** a mesma Draft PR #14 adiciona backup e restore MinIO
  verificáveis, manifesto de backup-set compartilhado com PostgreSQL e detecção
  fail-closed de objeto ausente, órfão ou fora do projeto/documento esperado. O CI
  executa round trip real combinado em PostgreSQL/pgvector e MinIO descartáveis.
  Retenção continua operacional/manual; criptografia deve usar controles nativos
  do storage/infraestrutura após decisão de chaves, sem criptografia improvisada.
* **v1.3 Backup Package 3:** a Draft PR #14 passa a empacotar os dois stores com
  AES-256-GCM autenticado da PyCA `cryptography`, chave externa e rotação por
  `key_id`; adiciona retenção fail-closed com dry-run, job com lock/timeout e drill
  que mede apenas RPO/RTO técnicos do cenário descartável. Nenhum agendamento real,
  KMS, nuvem, dado real, SLO de produção ou deploy integra este pacote.
  O Backend CI aprovou 194 testes de API e 43 testes operacionais. No probe de 1
  objeto/27 bytes, registrou backup 0,409 s, restore 0,415 s e RPO técnico 1,262 s;
  esses valores não representam capacidade ou compromisso de produção.
* **Integração v1.3.0:** a PR [#14](https://github.com/VenancioMarcos/vena-ia-platform/pull/14)
  foi integrada por Squash Merge em `24c1919`. A main pós-merge aprovou Ruff,
  mypy, 232 testes locais, frontend, Compose, OpenAPI 1.3.0 e Alembic head. Os
  round trips reais PostgreSQL/MinIO e criptografado permanecem comprovados pelo CI.
* **Release v1.3.0:** a tag anotada aponta para `e075657` e a
  [GitHub Release](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.3.0)
  foi publicada sem deploy. A validação direta aprovou health/runtime 1.3.0,
  49 paths OpenAPI e 40 testes de operações/health (4 integrações locais omitidas).
* **v1.4 Observability Package 1:** branch `codex/v1.4-observability-auditability`
  adiciona eventos estruturados allowlisted, request/correlation IDs, respostas
  de erro correlacionadas e readiness preliminar de PostgreSQL, Redis e MinIO.
  Nenhum conteúdo de usuário/IA, credencial ou telemetria externa é coletado.
* **v1.4 Observability Package 2:** a mesma Draft PR #15 adiciona métricas locais
  agregadas `vena-ia.metrics/v1`, endpoint admin desabilitado por padrão,
  correlação persistente da auditoria, alertas no-op/local com cooldown e tracing
  interno substituível. Labels dinâmicas/PII são proibidas; nenhum SaaS, webhook,
  transporte ou exportador externo foi introduzido.
  O primeiro Backend CI aprovou lint, mypy, migrations e 214 testes de API, mas
  revelou dois asserts operacionais presos ao head histórico `f42a1b7c9d30`.
  A correção deriva o head único do grafo Alembic, compara-o ao manifesto e exige
  que o restore preserve esse valor, sem enfraquecer checksum ou integridade.
  O Backend CI final aprovou 214 testes de API, 46 testes operacionais, o ciclo
  Alembic completo e integrações reais PostgreSQL/Redis/MinIO. O round trip
  criptografado descartável mediu backup 0,397 s, restore 0,404 s e RPO técnico
  1,248 s para 1 objeto/27 bytes; não são SLOs de produção.
* **v1.4 Observability Package 3:** o drill controlado cobre indisponibilidade e
  recuperação de PostgreSQL, Redis e MinIO, provedor de IA, readiness, rate limit,
  autenticação, processamento, backup, restore e erro interno. O contrato
  `vena-ia.incident-drill/v1` gera JSON determinístico e checksum fora do
  repositório, sem logs brutos, segredos, IDs de domínio ou conteúdo. Limiares são
  explícitos, validados e calibrados apenas com cenários sintéticos. Auditoria
  sensível continua persistente no PostgreSQL por política de 90 dias; métricas e
  tracing continuam efêmeros por processo, sem SaaS, backend externo ou transporte
  real de alertas. R-010 é mitigado; R-032 e R-033 permanecem residuais/monitorados.
  O Backend CI no head `22f224b` aprovou Ruff, mypy, o ciclo Alembic completo,
  216 testes de API e 52 testes operacionais com PostgreSQL/pgvector, Redis e
  MinIO reais. O round trip criptografado descartável mediu backup 0,426 s,
  restore 0,418 s e RPO técnico 1,247 s para 1 objeto/27 bytes, sem SLO produtivo.
* **Release v1.4.0:** a PR [#15](https://github.com/VenancioMarcos/vena-ia-platform/pull/15)
  foi integrada por Squash Merge em `1380156`; a tag anotada e a
  [GitHub Release](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.4.0)
  foram publicadas e validadas diretamente, sem deploy.
* **v1.5 Asynchronous Processing Package 1:** branch
  `codex/v1.5-asynchronous-processing` e Draft PR
  [#16](https://github.com/VenancioMarcos/vena-ia-platform/pull/16) adicionam
  `vena-ia.job/v1`, migration,
  fila Redis com claim/lease/heartbeat, worker no mesmo Modular Monolith,
  idempotência, progresso, retry/backoff, timeout, cancelamento e recuperação.
  O primeiro handler processa e indexa PDF em background; fila e logs não contêm conteúdo,
  segredos ou IDs de domínio em labels. OCR permanece ausente e PDF sem texto falha.
  Os gates locais aprovaram Ruff, mypy, 236 testes de API, 46 operacionais,
  frontend, Compose, OpenAPI 1.5.0/55 paths e Alembic head único.
  O CI final no head `0f57c57` aprovou 238 testes de API e 52 operacionais com
  PostgreSQL/pgvector, Redis e MinIO reais; Backend e Frontend CI estão verdes.
* **v1.5 Asynchronous Processing Package 2:** a mesma Draft PR #16 fortalece
  recovery após reinício/interrupção, recompõe Redis pela fonte PostgreSQL, renova
  leases, fecha duplicação concorrente e mantém documento `PROCESSING` até a
  indexação completa. Testes sintéticos cobrem 500 páginas, cancelamento entre
  páginas, progresso e erros PDF seguros. OCR foi avaliado e adiado (classe B), sem
  motor/dependência/serviço externo; R-017 continua aberto e R-038 monitorado. Os
  gates locais aprovaram Ruff, mypy, 251 testes de API, 46 operacionais, frontend,
  Compose, runtime/OpenAPI 1.5.0/55 paths e Alembic head único. O daemon Docker
  local está ausente; integrações reais permanecem como gate do Backend CI.
  O Backend CI do Package 2 no head `2086399` aprovou Ruff, mypy, ciclo Alembic,
  253 testes de API (incluindo Redis real) e 52 operacionais com PostgreSQL/pgvector,
  MinIO e round trip criptografado; Frontend CI/build também passou.
* **Release v1.5.0:** a PR [#16](https://github.com/VenancioMarcos/vena-ia-platform/pull/16)
  foi integrada por Squash Merge em `a3c2f6b`. A versão final 1.5.0 preserva o
  Alembic head `b18e4c7d2a91`; a tag anotada e a
  [GitHub Release](https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.5.0)
  foram publicadas sem deploy. Ruff, mypy, 251 testes locais de API, 46 testes
  operacionais, frontend, Compose, runtime/health/OpenAPI e validação direta da tag
  foram executados; integrações reais PostgreSQL/Redis/MinIO permanecem comprovadas
  pelo Backend CI final.
* **v1.6 Reliability Package 1:** `runtime-policy.json` passa a ser o manifesto
  executável de Python 3.13.11, Node 22.20.0, pnpm 11.9.0, pip 26.1.2, imagens e
  Actions. Python 3.14.6 é experimental. Bases API/Web, PostgreSQL/pgvector, Redis
  e MinIO usam tag explícita + digest; CI aplica policy e builds. Não há migration,
  mudança de dados, capacidade medida, deploy ou início dos packages seguintes.
* **v1.6 Reliability Package 2:** `resilience-policy.json` centraliza budgets
  operacionais e o policy check detecta deriva entre manifesto, settings, ambiente,
  código e runbooks. IA aplica classificação, deadline global, retry/backoff/jitter
  bounded e concorrência por processo sem fila ilimitada. PostgreSQL/MinIO e jobs
  recebem budgets explícitos; o drill cobre vinte cenários sintéticos. R-018 recebe
  mitigação adicional, R-033/R-038 permanecem residuais e R-034 não muda. Não há
  migration, carga/capacidade, merge, tag, Release ou deploy.
* **v1.6 Reliability Package 3 R1:** a evidência lógica inicial foi preservada como
  `HARNESS_ONLY_BASELINE`. O gate terminal inicia duas APIs e dois workers reais,
  PostgreSQL/pgvector, Redis e MinIO descartáveis, usa providers Redis, alterna a
  jornada HTTP entre instâncias e mede claims/leases, fault recovery, backpressure,
  RAG, isolamento e soak de 30 s. O bundle é atômico/checksummed e marca coleta
  ausente como `NOT_MEASURED`. R-034 permanece parcialmente mitigado/monitorar; não
  há capacidade produtiva, SLO/SLA, piloto, merge, tag, Release ou deploy.
  A primeira execução real revelou que o entrypoint do worker não registrava todos
  os modelos ORM: havia heartbeat, mas `list_recoverable()` falhava antes do claim.
  O import do registro oficial e um teste em subprocesso limpo corrigiram a causa.
  No head `4c35100`, Backend, Frontend, Runtime Policy e Controlled Capacity CI
  passaram; a PR #17 permanece Draft e mergeável.
* **Release v1.6.0:** a PR #17 foi integrada por Squash Merge em `5efe95a`; a tag
  anotada e a GitHub Release foram publicadas a partir do commit de preparação
  `f8dbe15`, sem deploy.
* **v1.7 Engineering Catalogs Package 1:** contratos versionados, catálogo
  persistente de materiais/máquinas/ferramentas e seleção rastreável usam APIs
  autenticadas. Toda saída é `PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW` e
  não gera toolpath, G-code nem comando para máquina.
* **v1.7 Engineering Rules Package 2:** regras sob demanda para milling, drilling
  e turning validam compatibilidade declarada e calculam somente parâmetros,
  tempo e custo preliminares rastreáveis. Dado ausente produz `NOT_AVAILABLE`;
  toda saída exige revisão humana e permanece não executável.
* **v1.7 Engineering Review Package 3:** relatório sob demanda reutiliza a mesma
  recomendação determinística e consolida ausências, incerteza informacional,
  rastreabilidade e checklist obrigatório sem persistência ou liberação CNC.
* **Limites operacionais permanentes:** o controle oficial está ativo em `docs/PERMANENT_OPERATIONAL_LIMITS.md`.

```text
PERMANENT_OPERATIONAL_LIMITS_SOURCE=docs/PERMANENT_OPERATIONAL_LIMITS.md
PERMANENT_OPERATIONAL_LIMITS_ACTIVE=true
```

---

## 4. O que NÃO está implementado ainda

* Gateway externo confiável e fluxo público de recuperação de senha; controles distribuídos internos de autenticação já usam Redis.
* OCR para PDFs sem camada textual; o Package 1 mantém falha explícita.
* Kernel geométrico CAD, propriedades topológicas, volume/área robustos, CAM, CNC ou simulação.
* Capacidade, timeout preemptivo de bibliotecas síncronas e backend histórico de telemetria validados para piloto/produção.
* Deploy/CD automatizado; os workflows atuais cobrem CI de backend e frontend, sem publicação automática.
* `packages/database` como pacote real (os modelos vivem em `apps/api` por decisão deliberada — `DEC-011`).

Nenhuma IA deve assumir que essas funcionalidades existem só porque estão documentadas no roadmap.

---

## 5. Como este documento deve ser usado por agentes de IA

1. Ler `CONTEXT.md` antes de propor ou executar qualquer tarefa.
2. Verificar se a tarefa está alinhada com a fase atual (`ROADMAP.md`).
3. Verificar se existe decisão registrada em `DECISIONS.md` ou ADR que restrinja a abordagem.
4. Ao concluir uma tarefa relevante, propor a atualização deste documento (Seção 3) como parte da entrega.

---

## 6. Fonte de verdade

Em caso de conflito entre este documento e qualquer conversa, memória de sessão ou instrução informal, prevalece o conteúdo versionado no repositório. Ver `GOVERNANCE.md`, Seção 2.
