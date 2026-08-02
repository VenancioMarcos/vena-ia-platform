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
limite. O limitador atual é local ao processo e deve ser complementado por um
controle distribuído/gateway antes de exposição pública horizontal.

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
