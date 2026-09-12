# TASK-LOCAL-037 — Referência oficial do MinIO no CI

## Objetivo

Corrigir a obtenção da imagem MinIO nos workflows após a falha isolada em036,
preservando a mesma release e o mesmo digest imutável.

## Escopo

Alteração exclusiva do host da imagem, de `minio/minio` para
`quay.io/minio/minio`, em Backend CI, Controlled Capacity CI e matriz de suporte.
Nenhuma lógica de produto ou configuração do serviço MinIO foi modificada.

## Evidência da Referência

A release `RELEASE.2025-09-07T16-13-09Z` existe no repositório oficial MinIO.
O manifesto público no Quay foi consultado sem executar a imagem. O índice
multi-plataforma retorna o mesmo digest já fixado:
`sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e`.
Plataformas anunciadas: linux/amd64, linux/arm64 e linux/ppc64le.

## Arquivos Criados

Este registro.

## Arquivos Modificados

`.github/workflows/backend-ci.yml`, `.github/workflows/controlled-capacity-ci.yml`,
`docs/RUNTIME_SUPPORT_MATRIX.md` e os registros de continuidade CTO. Inclui a
documentação local ainda não commitada da TASK-LOCAL-036.

## Testes Realizados

Validação YAML PASS nos dois workflows; `git diff --check` PASS; manifesto Quay
resolvido com o mesmo digest. Commit/push `748cd1c2dc0164e23b5bb03fc83c7e6264eb1a07`;
local, upstream e `ls-remote` idênticos. Nenhuma imagem foi executada localmente.

Checks remotos no HEAD `748cd1c`:

| Workflow | Resultado | Duração | Run/job |
| --- | --- | --- | --- |
| Frontend CI | SUCCESS | 1m15s | 34652440555/103437424587 |
| Runtime Policy CI | SUCCESS | 2m01s | 34652440427/103437424229 |
| Controlled Capacity CI | SUCCESS | 2m06s | 34652440501/103437424051 |
| Backend CI | SUCCESS | 3m23s | 34652440537/103437424455 |

PR #31: OPEN, Draft, MERGEABLE, `mergeStateStatus=CLEAN`. A passagem de
Controlled Capacity além dos três checks originais fornece evidência adicional
de que o registry Quay e a imagem fixada são acessíveis no runner.

## Critérios de Aceitação

Workflows válidos, referência pública resolvível com pinning preservado e quatro
checks do PR #31 concluídos com SUCCESS. Critérios atendidos.

## Próximos Passos

Encaminhar VTP ao CTO e aguardar parecer. PR pronto para revisão do mantenedor,
mas permanece Draft. Sem merge, fechamento do Draft, tag, release ou deploy.

## Parecer e transição

O CTO aprovou integralmente (A) a entrega em `748cd1c` e emitiu TASK-LOCAL-038.
Estado: `PR_31_CI_GREEN_AWAITING_MAINTAINER_REVIEW`. Os cinco documentos de
fechamento permanecem na working tree local, sem commit/push, conforme ordem.
PR #31 continua Draft; aguardar decisão formal do proprietário/mantenedor.
