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

O Package 2 acrescenta `vena-ia.metrics/v1`: contador por método/rota template e
classe HTTP, histograma de duração com buckets fixos, erros, readiness/falhas por
dependência, falhas controladas de IA, processamento, retry e rate limit. Nomes,
labels e valores operacionais são fechados; `user_id`, `project_id`, `document_id`,
query, body e conteúdo são proibidos. A coleta é local, thread-safe e fail-open.

`GET /internal/metrics` permanece desabilitado por padrão e, quando explicitamente
habilitado, exige autenticação e papel admin. A infraestrutura não deve publicar
essa rota sem gate próprio. A auditoria persiste request/correlation ID em campos
nullable para compatibilidade e permite filtro administrativo por ambos.

Alertas usam códigos fechados, severidade, cooldown e provider no-op/local.
Tracing cria spans locais pai/filho com operação normalizada, duração e erro
controlado. Nenhum webhook, SaaS, OpenTelemetry ou exportação é configurado.

## Consequências

Nenhum SaaS, telemetria externa ou perfil de usuário é introduzido. Métricas e
spans são efêmeros por processo e não substituem backend histórico, SLO, capacidade
ou gate de infraestrutura. Readiness mantém os timeouts existentes.
