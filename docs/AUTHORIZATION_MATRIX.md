# Matriz de Autorização — v0.4.1 Security Gate

**Status:** Implementada
**Data:** 2026-07-29

## Convenções

- `Permitido`: a operação pode ser executada.
- `Próprio`: permitido somente para o usuário ou proprietário autenticado.
- `Negado`: resposta `401`, `403` ou `404` segura.
- Recursos de projeto inacessíveis retornam `404` para não confirmar sua existência.
- O papel efetivo vem do banco após validação do token; headers e corpos enviados
  pelo cliente nunca definem identidade ou papel.

| Recurso | Ação | Usuário comum | Proprietário | Admin | Não autenticado |
|---|---|---|---|---|---|
| Autenticação | cadastrar conta member | Permitido, sujeito a `429` | Permitido, sujeito a `429` | Permitido, sujeito a `429` | Permitido, sujeito a `429` |
| Autenticação | login | Permitido, sujeito a `429` | Permitido, sujeito a `429` | Permitido, sujeito a `429` | Permitido, sujeito a `429` |
| Autenticação | logout e invalidação local do token apresentado | Permitido | Permitido | Permitido | Permitido e idempotente |
| Credencial legada | definir senha ausente de outro usuário | Negado (`403`) | Negado (`403`) | Permitido; nunca para si ou conta já credenciada | Negado (`401`) |
| Auditoria sensível | consultar eventos com filtros/limite | Negado (`403`) | Negado (`403`) | Permitido | Negado (`401`) |
| Métricas operacionais opt-in | consultar `/internal/metrics` | Negado (`403`) | Negado (`403`) | Permitido somente quando habilitado | Negado (`401`) |
| Evidência de incident drill | executar CLI local e gravar fora do repositório | Operador autorizado, sem endpoint público | Operador autorizado, sem endpoint público | Operador autorizado, sem endpoint público | Negado; não existe endpoint |
| Perfil | consultar próprio perfil | Próprio | Próprio | Permitido | Negado (`401`) |
| Perfis | listar usuários | Negado (`403`) | Negado (`403`) | Permitido | Negado (`401`) |
| Perfil | consultar outro usuário | Negado (`404`) | Negado (`404`) | Permitido | Negado (`401`) |
| Papel | definir `admin` no cadastro | Negado (`422`) | Negado (`422`) | Negado no endpoint público | Negado (`422`) |
| Projetos | criar | Permitido como proprietário | Permitido | Permitido como proprietário | Negado (`401`) |
| Projetos | listar/consultar | Próprio | Próprio | Permitido | Negado (`401`) |
| Projetos | informar `owner_id` no corpo | Negado (`422`) | Negado (`422`) | Negado (`422`) | Negado (`401`/`422`) |
| Metadados de arquivos | criar/listar | Próprio | Próprio | Permitido | Negado (`401`) |
| Documentos | upload/listagem/consulta/remoção | Próprio | Próprio | Permitido | Negado (`401`) |
| Documentos | iniciar processamento | Próprio | Próprio | Permitido | Negado (`401`) |
| Jobs de documento | criar/consultar/cancelar/repetir | Próprio | Próprio | Permitido para recurso acessível | Negado (`401`) |
| Recovery de jobs | reconciliar automaticamente no worker, sem endpoint | Operação interna; sem acesso público | Operação interna; sem acesso público | Operação interna; sem endpoint admin | Negado; endpoint inexistente |
| Política de runtimes/imagens | validar manifesto, pins, CI e rollback | Operação interna; sem endpoint | Operação interna; sem endpoint | Operação interna; sem endpoint | Negado; endpoint inexistente |
| Política de resiliência | validar budgets, classificação e drills | Operação interna; sem endpoint | Operação interna; sem endpoint | Operação interna; sem endpoint | Negado; endpoint inexistente |
| Perfil/carga sintética | validar guardrails e evidência sem dados reais | Operação interna; sem endpoint | Operação interna; sem endpoint | Operação interna; sem endpoint | Negado; endpoint inexistente |
| Catálogo de documentos | listar/status/estatísticas | Negado (`403`) | Negado (`403`) | Permitido | Negado (`401`) |
| Chat | consultar capacidade | Permitido | Permitido | Permitido | Negado (`401`) |
| Mensagens | criar/listar | Próprio | Próprio | Permitido | Negado (`401`) |
| IA | listar providers e executar operações | Permitido | Permitido | Permitido | Negado (`401`) |
| Biblioteca científica | criar/listar/consultar/alterar/excluir | Próprio | Próprio | Permitido | Negado (`401`) |
| Referências científicas | extrair/consultar | Próprio | Próprio | Permitido | Negado (`401`) |
| Síntese científica RAG | solicitar com fontes autorizadas | Próprio | Próprio | Permitido | Negado (`401`) |
| DOE/ANOVA/relatórios | criar/consultar rascunhos | Próprio | Próprio | Permitido | Negado (`401`) |
| Chat RAG/histórico | perguntar e consultar mensagens/fontes | Próprio | Próprio | Permitido | Negado (`401`) |
| Relatórios MVP | listar/reabrir por projeto | Próprio | Próprio | Permitido | Negado (`401`) |

## Quebras de contrato necessárias

- `X-User-ID` deixou de autenticar qualquer rota.
- Rotas protegidas exigem cookie de sessão HttpOnly ou
  `Authorization: Bearer <token>`.
- `POST /users` e `POST /auth/register` exigem `password` e rejeitam `role`.
- `POST /users` e `POST /auth/register` compartilham o limite de cadastro;
  `POST /auth/login` possui limite próprio. Todos retornam `429` com
  `Retry-After` quando a cota local do cliente da conexão é excedida.
- `POST /auth/logout` remove o cookie e invalida localmente o token apresentado;
  repetir logout ou apresentar token inválido continua retornando `204`.
- `PUT /users/{user_id}/credentials` aceita somente `password`, não altera papel,
  nunca retorna senha/hash e invalida tokens anteriores via `auth_version`.
- `POST /projects` não aceita mais `owner_id`; o proprietário é extraído do token.
- Listagens de projetos e arquivos são limitadas ao proprietário, salvo admin.
- `POST /chat/{project_id}/messages` aceita somente papel `user`; o cliente não
  pode persistir uma mensagem falsa como `assistant`.

Essas quebras removem vulnerabilidades críticas e são registradas também em
`CHANGELOG.md` e `CONTEXT.md`.

## Fronteira organizacional v1.9.0

Os papéis abaixo são memberships persistidas e não substituem o papel global legado.
Toda operação exige JWT válido e usuário do banco; `X-User-ID`, body, query e headers
arbitrários nunca fornecem identidade, organização, equipe ou papel.

| Capacidade | OWNER | ADMIN | MEMBER | Sem membership |
|---|---|---|---|---|
| Organization read | Permitido | Permitido | Permitido na própria organização | `404` |
| Organization update | Permitido | Permitido | `404` | `404` |
| Team create/update | Permitido | Permitido | `404` | `404` |
| Team read | Todas da organização | Todas da organização | Somente Team vinculada | `404` |
| Membership read | Permitido | Permitido | Negado (`404`) | `404` |
| Membership create | ADMIN ou MEMBER | Somente MEMBER | Negado (`404`) | `404` |
| Role change | Permitido, exceto OWNER | Negado | Negado; self-promotion impossível | `404` |
| Revogação | ADMIN/MEMBER; nunca OWNER | Somente MEMBER | Negado | `404` |
| Pilot Context | Permitido no escopo autorizado | Permitido no escopo autorizado | Própria Team | `404` |
| Readiness checklist | Permitido no escopo autorizado | Permitido no escopo autorizado | Própria Team | `404` |
| Iniciar rehearsal / validar CNC virtual | Permitido | Permitido na própria Organization | Negado (`404`) | `404` |
| Verificar evidence / executar rollback sintético | Permitido | Permitido na própria Organization | Negado (`404`) | `404` |

Negativas explícitas: não existe transferência de OWNER; `MEMBER` exige `team_id`;
`ADMIN`/`OWNER` são organizacionais; status sintético nunca equivale a piloto,
deploy, produção ou CNC aprovados.

Gate terminal: `TOKEN + DATABASE = AUTHORITY`. Request body, query, `X-User-ID`,
`X-Role` e demais headers nunca concedem identidade, membership ou papel.

## Catálogos Engineering — v2.1 Package 1

`organization_id` identifica o recurso solicitado, mas não concede autoridade.

| Recurso/ação | OWNER | ADMIN | MEMBER ativo | Sem membership | Não autenticado |
|---|---|---|---|---|---|
| Catálogo da organização — READ | Permitido | Permitido | Permitido | `404` | `401` |
| Catálogo da organização — CREATE | Permitido | Permitido | `404` | `404` | `401` |
| Catálogo — UPDATE/DELETE | Não exposto | Não exposto | Não exposto | Não exposto | Não exposto |
| Referência de sistema — READ | Permitido | Permitido | Permitido | Permitido autenticado | `401` |
| Referência de sistema — mutação | Sem endpoint público | Sem endpoint público | Negado | Negado | Negado |
| Legado sem owner — qualquer acesso | Negado/oculto | Negado/oculto | Negado/oculto | Negado/oculto | Negado |
| Governance evidence da organização — READ | Permitido | Permitido | Permitido | `404` | `401` |
| Governance evidence de system reference — READ | Permitido | Permitido | Permitido | Permitido autenticado | `401` |
| Governance evidence — mutação/bulk export | Não exposto | Não exposto | Não exposto | Não exposto | Não exposto |

Body fields de escopo/owner/role são rejeitados. `X-User-ID`/`X-Role` não alteram a
decisão. Misturar itens de organizações distintas falha como `404`.

Release Candidate v2.1.0: matriz revalidada sem novos papéis ou mutações públicas;
`TOKEN + DATABASE = AUTHORITY` permanece o gate terminal.
