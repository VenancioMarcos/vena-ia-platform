# SECURITY.md — Política de Segurança

**Status:** Documento Oficial
**Versão:** 1.0
**Documento relacionado:** `GOVERNANCE.md`, `docs/DECISIONS.md` (`DEC-009`)

---

## 1. Princípio

Segurança é tratada desde a fundação do projeto (`DEC-009`), não como etapa posterior. Este documento define o que nunca deve ser versionado ou exposto neste repositório, que é **público**.

---

## 2. Nunca Publicar Neste Repositório

* API Keys e tokens de qualquer provedor (OpenAI, GitHub, serviços de nuvem etc.).
* Arquivos `.env` reais (apenas `.env.example`, com placeholders, é permitido).
* Credenciais de banco de dados, MinIO, Redis ou qualquer serviço de infraestrutura.
* Dados de clientes, leads ou usuários reais, de qualquer produto do ecossistema Vena_IA.
* Prompts proprietários usados em produção (ex.: prompts do agente "Gabriel" ou de outros agentes comerciais do ecossistema Vena_IA).
* Modelos internos treinados ou ajustados especificamente para o negócio.
* Estratégias de RAG (estrutura de chunking, prompts de recuperação, pesos de re-ranking) consideradas vantagem competitiva.
* Dumps de banco de dados, mesmo anonimizados, sem revisão explícita.

---

## 3. Prevenção

* `.gitignore` bloqueia `.env`, artefatos de build, caches e dependências (ver arquivo `.gitignore` na raiz).
* `.env.example` deve conter apenas nomes de variáveis com valores de exemplo (`change_me`), nunca valores reais.
* Antes de qualquer commit que adicione arquivos de configuração, revisar manualmente se não há segredo embutido.

---

## 4. Se um Segredo For Commitado Acidentalmente

1. Revogar/rotacionar a credencial exposta imediatamente no provedor correspondente — antes de qualquer limpeza de histórico.
2. Remover o segredo do histórico do Git (ex.: `git filter-repo` ou ferramenta equivalente).
3. Registrar o incidente em `docs/DECISIONS.md` como decisão do tipo `Segurança`, com o que foi exposto, por quanto tempo e as ações tomadas.
4. Se o repositório for público no momento da exposição, tratar a credencial como comprometida permanentemente, independentemente da limpeza de histórico.

---

## 5. Autenticação e Sessão

A v0.4.1 adota:

* senha com PBKDF2-HMAC-SHA256, salt aleatório e 600.000 iterações;
* JWT HS256 assinado com `AUTH_SECRET_KEY` de pelo menos 32 bytes;
* expiração configurável, limitada entre 1 e 1.440 minutos;
* identidade extraída somente do token validado;
* cookie HttpOnly, `SameSite=Strict` e `Secure` configurável para o frontend;
* Bearer token para clientes de API;
* respostas e logs sem senha, hash ou token completo.

`AUTH_SECRET_KEY` nunca possui valor padrão utilizável e deve ser fornecido por
ambiente seguro. `X-User-ID` não é fonte de identidade.

### 5.1 Rate limiting de autenticação

`POST /auth/login`, `POST /auth/register` e a rota compatível `POST /users`
possuem limite configurável por cliente da conexão. Exceder o limite retorna
`429 Too Many Requests` com `Retry-After`. As duas rotas de cadastro compartilham
a mesma cota para impedir bypass por alias.

Cabeçalhos `X-Forwarded-For` são ignorados até existir uma fronteira de proxy
confiável configurada; `X-User-ID` nunca participa da identidade nem da chave do
limite. Redis aplica incremento e expiração atomicamente e compartilha a cota
entre réplicas. A origem é representada por SHA-256 na chave com namespace e TTL.
O modo em memória é permitido somente quando configurado explicitamente para
desenvolvimento/testes.

### 5.2 Invalidação de sessão

O logout remove o cookie e registra no Redis somente uma chave derivada por
SHA-256 do fingerprint do token, com TTL até sua expiração. Cookie, Bearer ou
ambos são revogados para todas as réplicas. Tokens emitidos no futuro também são
rejeitados; token inválido ou expirado mantém o logout idempotente.

Redis é obrigatório por padrão. Indisponibilidade não permite bypass: rotas
públicas de autenticação, consulta da denylist e escrita do logout retornam `503`
e registram `SECURITY_STORE_UNAVAILABLE` sem segredo. O logout não informa sucesso
se não puder persistir uma revogação válida. `auth_version` no banco continua
invalidando em todas as réplicas os tokens anteriores à definição de credencial.

### 5.3 Credenciais legadas e auditoria

Somente admin pode usar `PUT /users/{user_id}/credentials`, e apenas para uma
conta com `password_hash` ausente. O fluxo rejeita autoatendimento, redefinição
de credencial existente, mass assignment e senhas fora de 12–128 caracteres.
O papel não muda, senha/hash nunca são retornados e `auth_version` invalida todos
os tokens anteriores da conta de forma verificável no banco.

Eventos `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `RATE_LIMIT_EXCEEDED`, `LOGOUT`,
`TOKEN_REJECTED`, `LEGACY_CREDENTIAL_SET`, `LEGACY_CREDENTIAL_RESET_DENIED` e
`ADMIN_OPERATION_DENIED` são persistidos com IDs, horário, ator/alvo quando
aplicável, resultado, motivo categorizado e origem da conexão. Nunca armazenam
senha, hash, JWT, cookie, segredo, corpo integral, prompt ou documento.

Somente admin consulta `GET /audit/security-events`, com filtros e limite máximo
de 100 itens. A retenção padrão é 90 dias (`SECURITY_AUDIT_RETENTION_DAYS`); a
limpeza é responsabilidade operacional controlada nesta entrega, sem exclusão
automática. Logs gerais, métricas e tracing continuam fora deste pacote.

## 6. Autorização

* cadastro público cria somente papel `member`;
* não existe endpoint público de promoção para `admin`;
* o papel efetivo é lido do banco após a validação do token;
* usuários comuns acessam apenas recursos próprios;
* administradores seguem regras explícitas em `docs/AUTHORIZATION_MATRIX.md`;
* recursos de projeto inacessíveis retornam resposta segura sem vazar conteúdo.

## 7. Upload

Na v0.4.1, somente PDF é aceito. A API valida:

* tamanho máximo;
* nome normalizado e caminho interno com UUID;
* extensão `.pdf`;
* MIME `application/pdf`;
* assinatura `%PDF-`;
* prevenção de path traversal.

Formatos CAD/CAM/CNC permanecem bloqueados até existirem parsers e validações
específicos.

## 7.1 Isolamento organizacional para preparação sintética

A v1.9 adiciona memberships allowlisted consultadas no banco a cada operação.
Organization/Team/papel informados pelo cliente não concedem autoridade. OWNER
inicial é o usuário autenticado e é criado atomicamente; MEMBER exige Team;
cross-organization/cross-team falha como `404`; schemas rejeitam mass assignment.
Revogação bloqueia a próxima autorização por membership, sem prometer invalidação
além das garantias atuais do JWT registradas em R-013. O contexto de piloto é apenas
sintético e nunca autoriza deploy, cliente, produção ou CNC.

Evidence de rehearsal não recebe autoridade do payload. Somente OWNER/ADMIN com
membership ativa pode gerar/verificar/rollback; cross-org/team e membership revogada
falham como `404`. Validação CNC aceita contrato neutro estrito e não possui campo
para G/M-code, toolpath, transmissão ou payload executável.

Na release v1.9.0, SHA-256 é exclusivamente checksum de integridade:
não prova autoria, identidade, assinatura, não repúdio ou confiança externa.
Evidence incompleta, falha, indisponível, com checksum divergente, rollback falho ou
validação CNC inválida bloqueia prontidão. Todo material permanece sintético e não
produtivo, com revisão humana obrigatória.

## 7.2 Assistência especializada e Research grounded

A assistência v2.0 Package 2 usa somente perfis allowlisted e contexto minimizado.
O snapshot determinístico é imutável e vive separado da resposta generativa; o
provider não recebe credenciais, tokens, logs internos, authority fields ou targets
de máquina. Documentos/chunks recuperados são dados não confiáveis e nunca instruções.

Ausência de grounding bloqueia geração. Falha do provider preserva o workflow.
Validação de saída rejeita sintaxe potencial de G/M-code e claims de aprovação
produtiva/científica. Todos os outputs fixam revisão humana, não produção,
`simulation_only=true` e `executable_output=false`. Não existem tools de escrita,
execução, transmissão CNC ou persistência adicional de prompts/respostas.

## 7.3 Dashboard operacional v2.0

O navegador não envia identidade, papel, Organization ou Team como autoridade. A
visão integrada usa somente contratos autorizados do backend e mantém status de cada
domínio sem promoção cruzada. Resultado determinístico e assistência de IA são
separados; erro, ausência e bloqueio permanecem visíveis.

Não existem controles de produção, machine-send, download NC, postprocessor,
toolpath ou G/M-code. `REVIEW ACKNOWLEDGED` é somente confirmação visual local e não
constitui aprovação, assinatura, certificação ou autorização de fabricação.

## 7.4 Ownership de catálogos Engineering v2.1

Catálogos graváveis pertencem a uma Organization. `organization_id` apenas identifica
o recurso; autorização deriva de JWT, usuário persistido e membership ativa. OWNER e
ADMIN escrevem; memberships ativas leem; cross-org falha como `404`. Schemas rejeitam
campos extras e headers de identidade/papel não concedem autoridade.

`SYSTEM_REFERENCE` não possui owner e é read-only. Registros anteriores à migration
são `LEGACY_UNSCOPED` e ficam invisíveis até reconciliação por evidência confiável;
nunca são atribuídos à primeira, atual ou default Organization. A FK usa `RESTRICT`,
sem cascade destrutivo.

O Package 2 expõe somente evidence de um catálogo já autorizado. Não retorna lista de
memberships, roles de terceiros, tokens, raw logs ou payloads. O JSON individual não é
bulk export nem production readiness. Legacy segue `404`; membership revogada perde
acesso na próxima autorização do banco. Retenção temporal e exclusão não foram
inventadas. Checksum não é usado porque não há artefato persistido a verificar.

No Release Candidate v2.1.0, os mesmos controles foram revalidados sem novo papel,
endpoint de mutação ou authority client-side. Enterprise governance continua
`NON_PRODUCTION`; publicação e deploy permanecem gates separados.

## 7.5 Download controlado de candidato v3.1

As rotas do ambiente controlado exigem identidade autenticada e membership ativa no
banco. Organization, role, reviewer e G9 enviados por body/header/frontend não são
autoridade. Catálogos organization-owned devem pertencer ao mesmo escopo.

O download usa prova HMAC curta vinculada a user, organization e hashes canônicos dos
artifacts completos de candidato, blind evidence e Digital Thread. Assinatura, expiração, hash/manifest G-code, parser
RS274 independente, bundle/replay blind, G0–G8, G9 pendente e replay/ownership do
thread são revalidados. Respostas usam `no-store` e classificação explícita.

O arquivo é candidato não produtivo. Não existe machine-send, DNC/NC transfer, cycle
start, controle direto, autoridade física ou aprovação G9 nessa fronteira.

## 7.6 G9 Review Package v3.1

`vena-ia.g9-review-package/v1` é produzido somente pelo backend a partir de candidate,
Digital Thread, blind validation e Level-1/Level-2 já validados. O hash do pacote,
artifact hashes, versions e replay refs são evidence de integridade, nunca autoridade.

O contrato é output-only, estrito e não possui reviewer, decision ou evidence-authority
input. Campos extras, lifecycle stale, versão divergente, hash/replay adulterado,
candidate/thread/blind mismatch ou G9 diferente de pending falham fechado. O pacote
descreve protocolos humano/externo, mas não os executa e não aceita retorno externo.

Identity/membership atuais continuam sendo autorizadas antes da execução controlada.
Não existe endpoint de aprovação, registry de reviewer, integração de simulador,
machine-send, DNC/NC, cycle start, controle físico ou bypass de revisão.

---

## 8. Reportar uma Vulnerabilidade

Como o projeto está em fase de fundação e ainda não possui usuários externos em produção, vulnerabilidades identificadas devem ser reportadas diretamente ao mantenedor do repositório via issue privada ou contato direto, evitando detalhar a vulnerabilidade em uma issue pública antes de uma correção estar disponível.

---

## 9. Limites operacionais permanentes

`SECURITY.md` é a política de segurança oficial e substitui a criação de uma
política duplicada em `docs/SECURITY_POLICY.md`.

```text
PERMANENT_OPERATIONAL_LIMITS_SOURCE=docs/PERMANENT_OPERATIONAL_LIMITS.md
PERMANENT_OPERATIONAL_LIMITS_ACTIVE=true
```
