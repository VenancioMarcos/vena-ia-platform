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

## 5. Controle de Acesso e Upload (Aplicação)

Quando os módulos de upload e autenticação forem implementados (`docs/ROADMAP.md`, v0.3–v0.4):

* Validação obrigatória de tipo e tamanho de arquivo em todo upload.
* Autenticação e autorização antes de qualquer acesso a arquivos ou dados de projeto.
* Logs de acesso a dados sensíveis, sem registrar o conteúdo sensível em si.

---

## 6. Reportar uma Vulnerabilidade

Como o projeto está em fase de fundação e ainda não possui usuários externos em produção, vulnerabilidades identificadas devem ser reportadas diretamente ao mantenedor do repositório via issue privada ou contato direto, evitando detalhar a vulnerabilidade em uma issue pública antes de uma correção estar disponível.
