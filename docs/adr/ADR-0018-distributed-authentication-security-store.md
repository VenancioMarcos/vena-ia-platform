# ADR-0018 — Armazenamento distribuído para controles de autenticação

**Status:** Aprovada
**Data:** 2026-08-02
**Decisão relacionada:** `DEC-018`

## Contexto

Rate limiting e revogação de JWT eram locais ao processo. Réplicas diferentes e
reinícios permitiam cotas independentes ou reutilização de sessão encerrada.

## Decisão

Usar a infraestrutura Redis existente como padrão único para os dois controles.
O rate limit usa incremento e expiração atômicos; a revogação guarda somente uma
chave derivada por SHA-256, com TTL até a expiração do JWT. Todas as chaves têm
namespace configurável. Origem, JWT, cookie, PII e fingerprint não são persistidos
em texto puro.

Falha do Redis é fechada: cadastro/login, consulta de revogação e logout não
prosseguem sem o controle obrigatório e registram evento categorizado. O modo em
memória depende de `AUTH_SECURITY_STORE=memory` explícito e é restrito a
desenvolvimento/testes. `auth_version` permanece a invalidação persistente por
usuário.

## Consequências

Redis torna-se dependência de disponibilidade da autenticação e deve ser
monitorado. A biblioteca Python `redis` usa licença MIT compatível com o projeto.
Um gateway/proxy ainda precisa de fronteira confiável antes que cabeçalhos
encaminhados possam representar a origem real.
