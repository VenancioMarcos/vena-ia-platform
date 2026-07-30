# ADR-0009 — Security Gate de Autenticação e Autorização

**Status:** Aprovado
**Data:** 2026-07-29
**Responsável:** CTO / Backend Engineer

## Contexto

A auditoria da v0.4.0 identificou identidade falsificável por `X-User-ID`,
autoatribuição pública de `admin`, ausência de autorização uniforme e upload
baseado somente em metadados controlados pelo cliente.

## Decisão

1. Armazenar senhas com PBKDF2-HMAC-SHA256, salt aleatório e 600.000 iterações.
2. Emitir tokens JWT HS256 assinados, com `sub`, emissor, emissão e expiração.
3. Aceitar o token por Bearer para clientes de API e por cookie HttpOnly,
   `SameSite=Strict`, para o frontend.
4. Carregar identidade e papel do banco após validar o token.
5. Centralizar políticas de usuário, administrador e propriedade de projeto.
6. Forçar papel `member` no cadastro público; não expor promoção pública.
7. Permitir upload somente de PDF nesta versão, validando extensão, MIME e `%PDF-`.
8. Manter `password_hash` anulável na migration para preservar usuários legados;
   contas legadas sem hash não podem autenticar até receberem credencial por fluxo
   administrativo futuro.

## Alternativas consideradas

- Confiar em headers internos: rejeitado, pois o cliente pode falsificá-los.
- Adicionar bibliotecas externas de JWT e senha: adiado; a implementação usa
  primitivas criptográficas da biblioteca padrão para não ampliar dependências.
- Liberar formatos CAD antecipadamente: rejeitado, pois parsers e validação ainda
  não existem.

## Consequências

- Há quebra necessária dos contratos de cadastro, criação de projeto e autenticação.
- `AUTH_SECRET_KEY` deve possuir pelo menos 32 bytes e ser gerenciado fora do Git.
- Tokens são stateless e expiram; revogação imediata ainda não foi implementada.
- A v0.5 RAG permanece bloqueada até revisão e integração deste Security Gate.
