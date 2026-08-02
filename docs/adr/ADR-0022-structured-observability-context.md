# ADR-0022 — Contexto estruturado e redigido de observabilidade

**Status:** Aprovada
**Data:** 2026-08-02
**Decisão relacionada:** `DEC-022`

## Contexto

A API possuía health e auditoria de segurança, mas requisições e falhas não
compartilhavam identificadores seguros nem um schema de evento estável.

## Decisão

Adotar `vena-ia.observability/v1` como schema JSON allowlisted. Cada requisição
recebe UUIDs de request e correlação; UUIDs válidos são preservados, valores
inválidos são substituídos e ambos retornam em headers. `ContextVar` propaga o
contexto sem alterar contratos de domínio.

Registrar somente método, rota normalizada, status, duração, versão, ambiente e
tipo de erro controlado. Headers, query/body, conteúdo documental/IA, tokens,
cookies, senhas, chaves, hashes completos e credenciais não são coletados. A
redaction defensiva precede a allowlist. Erros internos retornam mensagem genérica
e IDs, nunca stack trace.

`GET /ready` verifica PostgreSQL, Redis e MinIO e revela somente `ready` ou
`unavailable`; `GET /health` permanece leve e compatível.

## Consequências

Nenhum SaaS, telemetria externa, tracing ou perfil de usuário é introduzido.
Readiness usa os timeouts existentes e não substitui métricas, alertas ou SLOs.
