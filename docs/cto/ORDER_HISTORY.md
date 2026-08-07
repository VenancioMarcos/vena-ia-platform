# Histórico de ordens do CTO

## Política permanente — fluxo CTO ↔ Codex

O proprietário ativou execução contínua obrigatória: toda task termina com status
entregue ao CTO, estado `AWAITING_CTO_NEXT_ORDER`, captura integral da ordem
seguinte e retomada imediata. Somente `ENCERRAR FLUXO` encerra o ciclo.

## 2026-08-06 — TASK-V17-003

O CTO aprovou a TASK-V17-002 e ordenou concluir a v1.7 na mesma PR #18 com
relatório técnico reproduzível, rastreabilidade, incerteza e revisão humana.

## 2026-08-06 — TASK-V17-002

O CTO aprovou a TASK-V16-004 e ordenou continuar na mesma branch/PR #18 com regras
determinísticas, compatibilidade e estimativas preliminares rastreáveis, mantendo
revisão humana e proibindo qualquer saída CNC executável.

## 2026-07-30 — v0.4.1 Security Gate

Integração, tag e release autorizadas e concluídas.

## 2026-07-30 — v0.5 RAG

Conclusão do RAG, integração da PR #5 e publicação `v0.5.0` autorizadas e
concluídas.

## 2026-07-30 — v0.6 CAD Initial

Conclusão, validação, Squash Merge e publicação `v0.6.0` autorizadas e concluídas.
A ordem também autorizou iniciar a v0.7 e estabeleceu autorização global de
entrega até v1.0, respeitando o ROADMAP e os limites permanentes.

## 2026-07-30 — v0.7 Engenharia/CAM Inicial

Primeira fundação entregue na Draft PR #7 com CI aprovado, sem toolpaths, G-code
ou envio para máquina.

## 2026-07-30 — v0.8 CNC Inicial

PR #8 integrada e release `v0.8.0` publicada. A saída permanece neutra,
`executable_output=false`, sem G-code, toolpath, transmissão ou liberação para
máquina.

## 2026-07-30 — v0.9 Scientific Research Foundation

Missão oficial autorizou implementação, validação, PR, Squash Merge, tag e release
da v0.9. A v1.0 permanece proibida até nova ordem oficial posterior.

## 2026-07-30 — v1.0 MVP Integration

Nova ordem oficial posterior revogou a proibição temporária de iniciar v1.0 e
autorizou implementação, PR, Squash Merge, tag e release `v1.0.0`, sem deploy e
sem iniciar v1.1.

## 2026-07-30 — v1.0.0 publicada

A PR #10 foi aprovada pelos checks de backend e frontend, integrada por Squash
Merge e publicada como `v1.0.0`. A validação pós-merge e a validação direta da
tag foram aprovadas; o aceite formal foi registrado na etapa seguinte.

## 2026-07-30 — aceite formal da v1.0.0

O CTO declarou `VENA_IA_V1_0_RELEASED_AND_FULLY_VERIFIED`, aprovou a release e
encerrou a missão técnica. A próxima versão não está autorizada.

## 2026-08-01 — v1.1 Stabilization Package 1

A ordem `TASK-V11-001` autorizou auditoria integral do MVP, correções de
estabilização, testes, documentação, commits, push e Draft PR na branch
`release/v1.1.0-stabilization`. Merge, tag e release permanecem proibidos nesta
missão.

## 2026-08-01 — v1.1 Final Validation, Merge and Release

Após aprovação dos três pacotes de estabilização, a ordem `TASK-V11-004`
autorizou explicitamente versionamento `v1.1.0`, retirada da PR #11 de Draft,
Squash Merge, tag anotada, GitHub Release e validação direta da tag. Deploy e
início da v1.2 permanecem proibidos.

## 2026-08-01 — v1.1.0 publicada

A PR #11 foi integrada por Squash Merge em `1f5263f`. A main sincronizada passou
novamente por Ruff, mypy, 165 testes sem warnings, frontend, Docker, runtime com
47 rotas OpenAPI, migrations PostgreSQL e secret scan. A tag anotada `v1.1.0` e
a GitHub Release foram publicadas e validadas diretamente, sem deploy.

## 2026-08-01 — aceite v1.1.0 e roadmap até v2.0

O CTO declarou `VENA_IA_V1_1_RELEASED_AND_FULLY_VERIFIED` e emitiu a
`TASK-ROADMAP-V2-001`: consolidar v1.2–v2.0, integrar o roadmap e iniciar sem
nova parada somente o primeiro pacote da v1.2. Deploy, v1.3, compra, publicação
comercial, G-code executável e transmissão CNC permanecem proibidos.

## 2026-08-01 — roadmap integrado e v1.2 Package 1 iniciado

O proprietário autorizou explicitamente o Squash Merge da PR #12, a sincronização
da `main` e o início imediato do primeiro pacote v1.2. A PR #12 foi integrada em
`6e1065d`; a branch `codex/v1.2-auth-rate-limiting` implementa somente rate
limiting de cadastro/login e deve permanecer em Draft PR para revisão do CTO.

A implementação foi publicada na Draft PR #13 com 172 testes locais, Ruff,
mypy, frontend, Docker e Backend CI aprovados, sem bloqueadores e sem iniciar
entregas posteriores da v1.2.

## 2026-08-02 — v1.2 Security Package 2

O CTO aprovou o Package 1 e emitiu `TASK-V12-002` para auditar exclusivamente
autenticação e sessão, corrigir falhas comprovadas e continuar na Draft PR #13.
Nova PR, merge, tag, release, deploy, migration e novos módulos permanecem
proibidos.

O Package 2 corrigiu reutilização de JWT após logout, validou emissão temporal e
melhorou o erro `429` no frontend. A validação aprovou 177 testes e os CI de
backend/frontend na PR #13; o risco distribuído R-013 permanece explícito.

## 2026-08-02 — v1.2 Security Package 3

O CTO aprovou o Package 2 e emitiu `TASK-V12-003` para credenciais legadas e
auditoria persistente de eventos sensíveis na mesma Draft PR #13. Migration é
autorizada; merge, tag, release, deploy, nova PR e v1.3 permanecem proibidos.

O Package 3 foi publicado na PR #13 com 182 testes, migration PostgreSQL
upgrade/downgrade/upgrade, OpenAPI e CI backend/frontend aprovados. O cliente
Docker local excedeu o tempo durante build de imagem; configuração Docker e o
build do CI foram aprovados, sem tornar o limite local um bloqueio do código.

## 2026-08-02 — v1.2 Security Package 4

O CTO aprovou o Package 3 e emitiu `TASK-V12-004` para distribuir rate limiting
e revogação usando o Redis existente, manter `auth_version`, falhar fechado e
continuar exclusivamente na Draft PR #13. Merge, tag, release, deploy, nova PR,
gateway externo, recuperação pública e v1.3 permanecem proibidos.

O Package 4 foi publicado na PR #13 com 190 testes locais, integração Redis real,
Ruff, mypy e frontend aprovados. Backend CI (com PostgreSQL e Redis) e Frontend CI
passaram. O build local da API compilou todas as camadas, mas o Docker Desktop
falhou ao exportar a imagem com EOF/500 e permaneceu indisponível após reinício;
nenhuma falha de código ou CI foi observada.

## 2026-08-02 — v1.2 Release e v1.3 Package 1

O CTO aprovou o Package 4 e emitiu `TASK-V12-005`, autorizando explicitamente a
validação final, Squash Merge da PR #13, tag e Release `v1.2.0`. Após validar a
tag, a execução deve iniciar somente backup/restore PostgreSQL verificável no
Package 1 da v1.3, em branch e Draft PR próprias. Deploy, dados reais, storage
externo e v1.4 permanecem proibidos.

A PR #13 foi retirada de Draft e integrada por Squash Merge em `0e386802`. A
`main` sincronizada aprovou Ruff, mypy, 193 testes locais, frontend e OpenAPI
1.2.0. A integração Redis permanece comprovada pelo Backend CI; o Docker Desktop
local continuou indisponível por erro de daemon/exportação, sem falha de código.

A tag anotada `v1.2.0` foi publicada apontando para `663dbc2`, junto da GitHub
Release “Vena_IA Platform v1.2.0 — Security and Data Protection”, sem deploy. A
execução iniciou imediatamente a branch `codex/v1.3-backup-recovery`, limitada
ao Package 1 de backup/restore PostgreSQL.

O Package 1 foi publicado na Draft PR #14. Ruff, mypy e 200 testes locais foram
aprovados; o Backend CI executou PostgreSQL/Redis, backup custom-format, checksum,
restore em banco descartável, migration head e prova de integridade em 1m54s.
Uma falha inicial de import do runner Linux foi corrigida sem alterar o contrato.

## 2026-08-02 — v1.3 Backup Package 2

O CTO aprovou o Package 1 e emitiu `TASK-V13-002` para continuar exclusivamente
na Draft PR #14 com backup/restore MinIO, manifesto compartilhado de backup-set,
detecção de inconsistência entre metadados e objetos, round trip combinado real,
retenção/RPO/RTO documentados e avaliação de criptografia. Merge, tag, release,
deploy, nova PR, v1.4, dados reais e CNC permanecem fora desta missão.

O Package 2 foi publicado na mesma Draft PR #14. Ruff, mypy, 215 testes locais,
frontend e Docker Compose passaram. O Backend CI executou PostgreSQL/pgvector e
MinIO reais, perda simulada, restore combinado, checksums, Alembic head e prova
de integridade. Uma asserção de teste sensível a maiúsculas no Linux foi
corrigida e a execução final passou em 1m57s. Não houve merge, tag ou deploy.

## 2026-08-02 — v1.3 Backup Package 3

O CTO aprovou o Package 2 e emitiu `TASK-V13-003` para concluir na mesma Draft
PR #14 retenção executável, agendamento controlado, criptografia autenticada com
chave externa, rotação, recovery drill e métricas técnicas de RPO/RTO. Merge,
tag, release, deploy, dados reais, nuvem, KMS pago, agendamento real e v1.4
permanecem proibidos.

O Package 3 foi publicado na mesma Draft PR #14. Os gates locais aprovaram Ruff,
mypy, 232 testes (5 integrações condicionais), frontend e Docker Compose. O
Backend CI aprovou 194 testes de API e 43 operacionais, incluindo o round trip
criptografado real. O probe descartável mediu backup 0,409 s, restore 0,415 s e
RPO técnico 1,262 s para 1 objeto/27 bytes, sem declaração produtiva.

## 2026-08-02 — v1.3 final e início da v1.4

O CTO aprovou o Package 3 e emitiu `TASK-V13-004`, autorizando retirar a PR #14
de Draft, Squash Merge, versionar/publicar `v1.3.0`, validar diretamente a tag e
iniciar somente o Package 1 da v1.4 em branch e Draft PR próprias. Deploy, v1.5,
telemetria externa, dados reais e CNC permanecem proibidos.

A PR #14 foi integrada por Squash Merge em `24c1919`. A main sincronizada passou
por Ruff, mypy, 232 testes locais, frontend typecheck/build, Docker Compose,
OpenAPI 1.3.0 e Alembic head antes da criação da tag.

A tag anotada `v1.3.0` foi publicada apontando para `e075657`, junto da GitHub
Release “Vena_IA Platform v1.3.0 — Backup, Recovery and Retention”. A validação
direta da tag aprovou health/runtime 1.3.0, OpenAPI com 49 paths e 40 testes de
health/operações; nenhum deploy foi realizado.

A branch `codex/v1.4-observability-auditability` foi criada a partir da main com
a evidência da release. O Package 1 limita-se a logging estruturado, correlação,
redaction e readiness; métricas/tracing externos e v1.5 não foram iniciados.

O Package 1 foi publicado na Draft PR #15. Localmente, Ruff, mypy, 240 testes,
frontend e Compose passaram. O Backend CI aprovou 202 testes de API e 44
operacionais, incluindo readiness real simultânea de PostgreSQL, Redis e MinIO.
Uma falha inicial por bucket descartável ainda não criado foi corrigida no setup
do teste, preservando a semântica fail-closed do endpoint.

## 2026-08-02 — v1.4 Observability Package 2

O CTO aprovou o Package 1 e emitiu `TASK-V14-002` para continuar exclusivamente
na Draft PR #15 com métricas agregadas, auditoria correlacionada, alert contracts
e tracing local. Merge, tag, release, deploy, SaaS, webhook, telemetria externa,
dados reais e v1.5 permanecem proibidos.

O código adiciona `vena-ia.metrics/v1`, endpoint admin opt-in, migration dos IDs
de correlação, eventos de mutação sem conteúdo, providers no-op/local e controles
de redaction/cardinalidade. Os gates locais aprovaram Ruff, mypy, 212 testes de
API, 39 testes operacionais condicionais, frontend, Compose e OpenAPI com 51
paths. O daemon Docker local não respondeu; integrações reais e ciclo PostgreSQL
da migration permanecem como gates explícitos do Backend CI.

O primeiro Backend CI do Package 2 aprovou Ruff, mypy, o ciclo completo da nova
migration e 214 testes de API. Dois round trips falharam somente porque os testes
comparavam o banco restaurado a um head histórico fixo. A correção `2ce8f54`
passa a derivar o head único do grafo oficial, exige que o manifesto o registre e
compara o restore ao manifesto; um teste com grafo temporário prova que a
expectativa avança automaticamente quando uma migration sucessora é adicionada.

O Backend CI final no head `d588ece` concluiu em 2m04s: Ruff, mypy, Alembic
upgrade/downgrade/upgrade, 214 testes de API e 46 testes operacionais passaram.
PostgreSQL/pgvector, Redis e MinIO reais validaram readiness, backup/restore
PostgreSQL e round trip criptografado combinado. O probe descartável registrou
backup 0,397 s, restore 0,404 s e RPO técnico 1,248 s para 1 objeto/27 bytes,
sem SLO ou afirmação produtiva. A PR #15 permanece Draft, sem merge ou deploy.

## 2026-08-04 — v1.4 Observability Package 3

O CTO aprovou o Package 2 e emitiu `TASK-V14-003` para concluir exclusivamente na
Draft PR #15 o incident drill ponta a ponta, contrato/bundle de evidência,
retenção/backend, calibração de limiares e riscos R-010/R-032/R-033. Merge, tag,
release, deploy, nova PR, backend/telemetria externos, transporte real de alertas,
dados reais e v1.5 permanecem proibidos.

O Package 3 implementa onze cenários controlados com recuperação das três
dependências, `vena-ia.incident-drill/v1`, JSON determinístico e SHA-256 fora do
repositório. Auditoria continua persistente por 90 dias; métricas/tracing são
efêmeros. R-010 foi mitigado; R-032/R-033 continuam monitorados. Os gates locais
aprovaram Ruff, mypy, 215 testes de API, 46 operacionais, frontend, Compose,
OpenAPI 51 e secret scan; integrações reais permanecem reservadas ao Backend CI.

O Backend CI final no head `22f224b` concluiu em 1m55s: Ruff, mypy, Alembic
upgrade/downgrade/upgrade, 216 testes de API e 52 testes operacionais passaram.
PostgreSQL/pgvector, Redis e MinIO reais validaram readiness e os round trips de
backup/restore. O probe de 1 objeto/27 bytes registrou backup 0,426 s, restore
0,418 s e RPO técnico 1,247 s, sem SLO ou alegação produtiva.

## 2026-08-04 — finalização v1.4.0 e início v1.5 Package 1

O CTO aprovou formalmente a `TASK-V14-003` e emitiu `TASK-V14-004`, autorizando
retirar a PR #15 de Draft, realizar Squash Merge, publicar/validar `v1.4.0` e,
somente após a release, iniciar a fundação de jobs assíncronos da v1.5 em branch
e Draft PR próprias. Merge da v1.5, OCR, deploy, SaaS e v1.6 permanecem proibidos.

A PR #15 foi retirada de Draft e integrada por Squash Merge em `1380156`. Main e
tag anotada `v1.4.0` foram validadas por Ruff, mypy, 215 testes de API, 46 testes
operacionais, frontend e Compose. A GitHub Release “Vena_IA Platform v1.4.0 —
Observability and Auditability” foi publicada sem deploy.

Na branch `codex/v1.5-asynchronous-processing`, o Package 1 implementou o contrato
durável `vena-ia.job/v1`, migration `b18e4c7d2a91`, fila Redis com lease/heartbeat,
worker allowlisted, processamento/indexação PDF, API autenticada e frontend mínimo.
Os gates locais aprovaram Ruff, mypy, 236 testes de API, 46 operacionais, frontend,
Compose e OpenAPI 1.5.0-dev/55 paths. A Draft PR #16 foi aberta; integrações reais
PostgreSQL/Redis/MinIO permanecem como gate do CI antes da revisão do CTO.

O Backend CI no head `0f57c57` concluiu em 2m04s: Ruff, mypy, ciclo Alembic,
238 testes de API e 52 operacionais passaram, incluindo Redis real, readiness do
worker e os round trips PostgreSQL/pgvector e MinIO. Frontend CI/build também
passou. A PR #16 permanece Draft, limpa e mergeável, sem merge ou deploy.

## 2026-08-05 — v1.5 Asynchronous Processing Package 2

O CTO aprovou a `TASK-V14-004`/Package 1 e emitiu `TASK-V15-002` para continuar
exclusivamente na branch `codex/v1.5-asynchronous-processing` e Draft PR #16.
O escopo cobre recovery/restart, concorrência, leases, efeitos parciais, PDFs
sintéticos extensos, falhas de dependências e avaliação formal de OCR. Merge, tag,
Release, deploy, OCR, motor OCR, serviço externo, GPU, nova PR e v1.6 permanecem
proibidos.

O Package 2 comprovou localmente recovery PostgreSQL→Redis, lease renovável,
concorrência/idempotência, efeitos parciais seguros e corpus de 500 páginas. Ruff,
mypy, 251 testes de API, 46 operacionais, frontend e Compose passaram. A avaliação
OCR decidiu B — adiado, sem instalação ou envio externo. O daemon Docker local
estava ausente; PostgreSQL/Redis/MinIO reais e os dois recoverers permanecem como
gate obrigatório do Backend CI antes do status terminal.

O Backend CI final `31051848806` concluiu em 1m57s: Ruff, mypy, Alembic
upgrade/downgrade/upgrade, 253 testes de API e 52 operacionais passaram com
PostgreSQL/pgvector, Redis e MinIO reais. Dois consumidores e dois recoverers
validaram exclusividade/idempotência no Redis. O round trip descartável registrou
backup 0,425 s, restore 0,408 s e RPO técnico 1,382 s para 1 objeto/27 bytes, sem
SLO produtivo. Frontend CI `31051848820` também passou. A PR #16 permanece Draft.

## 2026-08-05 — finalização e Release v1.5.0

O proprietário aprovou diretamente os Packages 1 e 2 e emitiu a `TASK-V15-003`.
A ordem encerra a v1.5 sem Package 3 e autoriza preparar a versão final 1.5.0,
revalidar integralmente, retirar a PR #16 de Draft, realizar Squash Merge, publicar
a tag anotada e a GitHub Release e validar diretamente a tag. Deploy, OCR, novos
tipos de job, microserviço, serviços externos e início da v1.6 permanecem proibidos.

A preparação final 1.5.0 foi validada localmente e no CI dos runs backend
`31053239113` e frontend `31053244413`. A PR #16 saiu de Draft limpa/mergeável e
foi integrada por Squash Merge em `a3c2f6b`. A main pós-merge aprovou Ruff, mypy,
251 testes de API, 46 operacionais, frontend e Compose. A tag anotada `v1.5.0`
aponta ao commit deste registro de release e a GitHub Release foi publicada em
`https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.5.0`, sem deploy.
A validação direta da tag repetiu os gates locais; PostgreSQL/Redis/MinIO reais
permanecem comprovados pelo CI final. A v1.6 não foi iniciada.

## 2026-08-05 — v1.6 Package 1 Runtime and Container Reproducibility

O CTO aprovou a Release v1.5.0 e emitiu `TASK-V16-001`, exclusivamente para
eliminar deriva de runtimes, imagens, Dockerfiles, Compose e CI. A branch
`codex/v1.6-reliability-scalability` parte de `f6b6399`. O escopo autoriza matriz,
manifesto/policy, pins, builds, testes, documentação, commits, push e Draft PR.
Merge, tag, Release, deploy, carga, capacidade, escalabilidade e packages seguintes
permanecem proibidos.

A entrega foi concluída na Draft PR #17. O head `84c219a` passou no Backend CI
`31057602795` (Ruff, mypy em 135 arquivos, ciclo Alembic, 253 testes de API e 55
operacionais), Frontend CI `31057602796` e Runtime Policy CI `31057602808`. As
imagens fixadas da API e Web foram construídas no CI; a PR permanece Draft,
mergeável e sem merge, tag, Release ou deploy.

## 2026-08-05 — v1.6 Package 2 Resilience Budgets

O CTO aprovou a TASK-V16-001 e emitiu `TASK-V16-002` para continuar exclusivamente
na branch e Draft PR #17. O escopo cobre inventário/policy de budgets, classificação,
timeouts, retries, backoff/jitter, IA/embeddings, concorrência, backpressure,
degradação, readiness, observabilidade e drill. Merge, tag, Release, deploy,
capacidade formal, v1.7 e packages posteriores permanecem proibidos.

O head de código `1905884` aprovou localmente duas policies, Ruff, mypy em 138
arquivos, 266 testes de API, 55 operacionais, frontend, Compose e Alembic. O CI
aprovou Backend `31059513786` (268 API, 61 operacionais e serviços reais), Frontend
`31059513849` e Runtime Policy `31059513794` com builds API/Web. A PR #17 permanece
Draft, mergeável e sem merge, tag, Release, deploy ou teste formal de capacidade.

## 2026-08-06 — v1.6 Package 3 Controlled Capacity

O CTO aprovou a TASK-V16-002 e emitiu `TASK-V16-003` para perfil sintético,
carga controlada, soak curto, E2E, duas APIs/workers, estado compartilhado,
backpressure, evidência, gargalos e guardrails na mesma Draft PR #17. Merge, tag,
Release, deploy, piloto real, SLO/SLA, API paga, dados reais e v1.7 são proibidos.

O head de código `500c94f` aprovou três policies, Ruff, mypy em 140 arquivos, 266
testes de API, 65 operacionais, frontend e harness local. No CI, Backend
`31060952153`, Frontend `31060952144`, Runtime Policy `31060952139` e Controlled
Capacity `31060952197` passaram. A evidence externa/checksummed foi publicada como
artifact `8952091174`; a PR permanece Draft, sem merge, tag, Release ou deploy.

## 2026-08-06 — v1.6 Package 3 R1 worker recovery correction

O gate real R1 revelou workers com heartbeat, mas sem claim. Diagnóstico allowlisted
confirmou `InvalidRequestError` na primeira consulta do reconciliador: o entrypoint
do worker não registrava todos os modelos ORM carregados pela API. O head `4c35100`
importa o registro oficial e adiciona regressão em subprocesso limpo. Backend
`31131271003`, Frontend `31131271784`, Runtime Policy `31131271162` e Controlled
Capacity `31131271390` passaram no mesmo head. A PR #17 segue Draft e mergeável;
merge, tag, Release e deploy não foram realizados.

## 2026-08-06 — TASK-V18-003

O CTO aprovou a TASK-V18-002 no head técnico `54f353c` e preservou o commit de
política `1148f85`. A ordem autoriza reconhecimento inicial, conservador,
determinístico e rastreável de features na branch
`codex/v1.8-cad-interoperability` e Draft PR #19. Proíbe merge, tag, Release,
deploy, v1.9, CAM, toolpath, G-code e transmissão CNC. Package 3 implementa apenas
faces planares/cilíndricas e furo passante sob evidência estrita; closed hole e
slot permanecem adiados.
