# Histórico de ordens do CTO

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
