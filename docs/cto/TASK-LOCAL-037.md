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

Validação YAML, `git diff --check`, inspeção do manifesto Quay, commit/push e
checks remotos serão registrados ao concluir. Nenhuma imagem foi executada localmente.

## Critérios de Aceitação

Workflows válidos, referência pública resolvível com pinning preservado e nova
execução do PR #31 monitorada até estado terminal.

## Próximos Passos

Validar, criar commit atômico, enviar a branch autorizada e monitorar CI.
Sem merge, fechamento do Draft, tag, release ou deploy.
