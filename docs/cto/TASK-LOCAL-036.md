# TASK-LOCAL-036 — Auditoria dos checks remotos do PR #31

## Objetivo

Monitorar os workflows do PR Draft #31 até o estado terminal e registrar a
evidência remota, sem merge ou correção preventiva.

## Escopo

Leitura dos checks e do log da etapa com falha. Nenhum código, workflow,
infraestrutura, dependência ou estado do PR foi alterado nesta missão.

## Arquivos Criados

Este registro.

## Arquivos Modificados

`CONTEXT.md`, `docs/cto/CURRENT_ORDER.md`, `EXECUTION_STATUS.md`,
`ORDER_HISTORY.md` e `TASK-LOCAL-035.md`.

## Resultados Remotos

| Workflow | Job | Resultado | Duração |
| --- | --- | --- | --- |
| Frontend CI | build | SUCCESS | 1m24s |
| Runtime Policy CI | policy-and-builds | SUCCESS | 2m05s |
| Backend CI | test | FAILURE | 2m36s |

Run Backend: `34651729970`; job `103435193047`; HEAD remoto
`08cabbe5077c0899059ab0d3ce9a378f777e7df2`.

No Backend CI, setup, serviços iniciais, checkout, Python 3.13.11, instalação,
Ruff, mypy, migrations e pytest concluíram com SUCCESS. A falha ocorreu depois
dos testes, exclusivamente na etapa `Start disposable MinIO service`.

Comando registrado no runner:
`docker run ... minio/minio:RELEASE.2025-09-07T16-13-09Z@sha256:14cea493... server /data`.
O daemon respondeu que não encontrou a imagem local e que o pull foi negado:
`pull access denied for minio/minio, repository does not exist or may require
'docker login': denied: requested access to the resource is denied`.
O passo terminou com código 125; o teste PostgreSQL/MinIO foi ignorado pelo
workflow em consequência.

A mesma referência está em `.github/workflows/backend-ci.yml`,
`.github/workflows/controlled-capacity-ci.yml` e `docs/RUNTIME_SUPPORT_MATRIX.md`.
Ambiente remoto: Python 3.13.11. Ambiente local anteriormente validado: Python
3.14.6 experimental e Node 24.19.0; Frontend CI usou Node 22.20.0 e passou.
A evidência não aponta regressão do código Python: a suíte do job passou antes
da falha do pull da imagem. Também não prova se a causa é remoção/indisponibilidade
da tag, digest incorreto, política do registry ou autenticação; isso exige missão
corretiva delimitada e nova verificação da fonte oficial da imagem.

## Critérios de Aceitação

Estados terminais e log exato registrados; causa isolada sem alteração preventiva.
O estado `READY_FOR_MAINTAINER_PR_REVIEW` não foi alcançado.

## Próximos Passos

Solicitar ao CTO uma ordem corretiva limitada à referência/obtenção da imagem
MinIO e sua documentação. Manter PR Draft, sem merge, rerun ou push adicional
até autorização. G9 e autoridade física permanecem bloqueados.

## Parecer e ordem corretiva

O CTO acolheu o resultado como R por falha de infraestrutura externa e emitiu
TASK-LOCAL-037, autorizando corrigir estritamente a referência oficial do MinIO,
criar commit, fazer push da branch e monitorar a nova execução. Sem merge.
