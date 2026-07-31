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
| Autenticação | cadastrar conta member | Permitido | Permitido | Permitido | Permitido |
| Autenticação | login | Permitido | Permitido | Permitido | Permitido |
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
- `POST /projects` não aceita mais `owner_id`; o proprietário é extraído do token.
- Listagens de projetos e arquivos são limitadas ao proprietário, salvo admin.
- `POST /chat/{project_id}/messages` aceita somente papel `user`; o cliente não
  pode persistir uma mensagem falsa como `assistant`.

Essas quebras removem vulnerabilidades críticas e são registradas também em
`CHANGELOG.md` e `CONTEXT.md`.
