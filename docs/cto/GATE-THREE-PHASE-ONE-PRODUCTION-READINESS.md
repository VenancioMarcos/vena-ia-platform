# GATE: TRÊS — PREPARAÇÃO PARA PRODUÇÃO (FASE 1)

**STATUS:** `BLOCKED_REAL`
**Data:** 2026-09-21
**Branch:** `codex/gate-two-public-flow-integration`
**Pull Request:** #84 (Draft)

## 1. OBJETIVO

Homologar upstream e runtimes oficiais, validar a migração em PostgreSQL real e
preparar a infraestrutura candidata do Beta 1 sem contratar serviços, alterar DNS,
criar credenciais externas ou executar deploy.

## 2. O QUE FOI VERIFICADO

Histórico da branch e da `main`, três workflows remotos, cadeia Alembic, imagens e
runtimes fixados, Compose, variáveis, health/readiness, CORS, cookies, rate limits,
backup/restore e dependências externas para cinco clientes iniciais.

## 3. O QUE FOI EXECUTADO

A branch foi publicada e o Draft PR #84 aberto. O conflito causado pela relação
pré-squash/squash da Rota 34 foi resolvido por merge após comprovar árvores-base
idênticas. As três CIs passaram. Em PostgreSQL 17 descartável, a cadeia foi elevada
até `a71c9e4d2b80`, revertida para `e61c4f8a2b90` e elevada novamente à head. Foi
criado um candidato de produção com isolamento de rede, healthchecks, template sem
segredos, build Web parametrizado e validações de startup fail-closed.

## 4. ARQUIVOS ALTERADOS

Configuração: `.env.production.example`, `docker-compose.production.yml`,
`.gitignore`, Dockerfile Web, configuração API, manifesto e validador de runtime,
workflow Runtime Policy CI e teste de segurança. Documentação: runbook Beta 1,
matriz de runtimes, contexto e registros CTO.

## 5. COMMITS

- `0d6713205a5892d3785a465d87636d9fd86226fa`: fluxo público controlado.
- `16c4125ca301be8d374c0b759016e4e7d8117b5c`: reconciliação histórica com `main`.
- `aa46d3f`: preparação do runtime candidato de produção.

## 6. TESTES EXECUTADOS

Backend CI, Frontend CI, Runtime Policy CI, Alembic em PostgreSQL 17 descartável,
Compose de produção, runtime policy local, Ruff, mypy e testes focados de
configuração/runtime.

## 7. RESULTADOS DOS TESTES

Backend CI: `SUCCESS` em 4m01s. Frontend CI: `SUCCESS` em 1m49s. Runtime Policy CI:
`SUCCESS` em 1m53s. Alembic: `a71c9e4d2b80 → e61c4f8a2b90 → a71c9e4d2b80`.
Testes focados: 13 passed/1 skipped e 3 passed. Compose, Ruff, mypy, policy e diff:
aprovados.

## 8. EVIDÊNCIAS

PR #84 está Draft, `OPEN`, `MERGEABLE/CLEAN`. O banco descartável terminou na head
e continha `controlled_result_records` e `result_feedback`; foi removido após o
teste. O Compose não publica PostgreSQL, Redis ou MinIO e vincula API/Web apenas a
loopback. A CI executa Python 3.13.11, Node 22.20.0 e pnpm 11.9.0.

## 9. ITENS JÁ PRONTOS

Branch e PR, CIs oficiais, migração reversível, imagens fixadas, health/readiness,
cookie `HttpOnly/Secure/SameSite=Strict`, Redis para rate limit e revogação,
backup/restore versionado, candidato Compose e checklist operacional.

## 10. ITENS QUE PRECISAM SER INTEGRADOS

TLS/reverse proxy, DNS, host, SMTP, secret manager, storage externo de backup,
monitoramento/alertas e conta produtiva do provedor de IA após decisão do
proprietário.

## 11. ITENS QUE PRECISAM SER DESENVOLVIDOS

O E2E de navegador contra API/banco reais no ambiente alvo e a integração com os
serviços externos escolhidos. Nenhum desses itens foi iniciado sem a autoridade e
os destinos necessários.

## 12. BLOQUEIOS

`BLOCKED_REAL`: domínio/DNS, VPS/região/sizing, TLS, SMTP, gestão de segredos,
destino/política de backup, conta/budget de IA e canal operacional de alertas
dependem de escolha, contratação ou credencial do proprietário.

## 13. RISCOS

Não houve E2E Web+API real; o candidato Compose ainda não foi exercitado em host
externo; RPO/RTO produtivos não estão aprovados; defaults de rate limit precisam
ser calibrados; monitoramento permanece local e efêmero; exposição sem reverse
proxy/TLS seria insegura.

## 14. PENDÊNCIAS

Parecer do CTO sobre a Fase 1, decisão do proprietário sobre os oito itens externos,
CI remota do commit de prontidão, smoke integrado no ambiente escolhido e drill de
restore antes da admissão de clientes.

## 15. ALTERAÇÕES EXTERNAS NECESSÁRIAS

Contratação/provisionamento do host, DNS, TLS, SMTP, secret manager, backup externo,
conta de IA e destino de alertas. Nenhuma alteração externa foi feita.

## 16. AUTORIZAÇÕES NECESSÁRIAS

Decisão explícita do proprietário para cada item externo, para qualquer gasto,
credencial, concessão de acesso, alteração DNS, merge, release ou deploy. Gate
Quatro requer nova validação formal.

## 17. CRITÉRIO DE ACEITE

Fase 1 aceita quando PR/CIs, migração reversível, Compose candidato, segurança de
configuração e mapa de bloqueios forem homologados. Produção/Beta só pode ser
aceita após resolver bloqueios, executar E2E real, readiness e restore comprovado.

## 18. DECLARAÇÃO FINAL

A homologação upstream e a preparação local do Gate Três Fase 1 foram concluídas;
o avanço operacional está `BLOCKED_REAL`. `PHYSICAL_USE_AUTHORIZED=FALSE`,
`G9=PENDING_AUTHORITATIVE_REVIEW`, `NO_HUMAN_REVIEW_BYPASS=TRUE`,
`MACHINE_SEND=FALSE`, `DNC=FALSE`, `NC_TRANSFER=FALSE`, `CYCLE_START=FALSE`,
`emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.
Nenhum merge, release, deploy ou Gate Quatro foi executado.

## Registro de Entrega — PROJECT.md §19

**Objetivo:** homologar upstream, migração e prontidão de infraestrutura.

**Escopo:** PR/CI, PostgreSQL, Compose, segurança de configuração e checklist
externo.

**Arquivos criados/modificados:** descritos na seção 4.

**Testes e critérios de aceitação:** descritos nas seções 6, 7 e 17.

**Próximos passos:** solicitar parecer do CTO e aguardar nova ordem, sem iniciar
Gate Quatro.
