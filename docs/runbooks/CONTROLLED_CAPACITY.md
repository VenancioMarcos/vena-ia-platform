# Runbook — capacidade controlada R1

Contrato: `vena-ia.capacity-profile/v1`.

## Execução

1. Valide `python scripts/capacity_policy.py`.
2. Inicie PostgreSQL/pgvector, Redis e MinIO descartáveis usando as referências
   fixadas em `runtime-policy.json`.
3. Aplique `alembic upgrade head`.
4. Configure exclusivamente credenciais descartáveis, providers Redis e
   `APP_ENV=capacity-ci`.
5. Execute `python scripts/capacity_process_gate.py --output <diretório-temporário>/capacity-evidence.json --commit <sha>`.
6. Confirme `GUARDRAIL_RESULT=PASS`, SHA-256, dois processos de API, dois workers,
   fila final zero, jobs terminais, cleanup e ausência de claim duplicado.
7. Encerre processos e remova o container/dados descartáveis mesmo após falha.

O output deve estar fora do repositório, em diretório existente e sem symlink. A
publicação usa arquivo temporário exclusivo, flush/fsync, hard-link atômico sem
overwrite e cleanup do temporário. Concorrência, ancestral symlink, traversal,
arquivo existente e falha de escrita são testes obrigatórios.

## Interpretação

`HARNESS_ONLY_BASELINE` é teste unitário, não carga da plataforma. Somente
`process_integration_*` representa HTTP/processos reais, ainda assim em CI
descartável. Campos indisponíveis são `NOT_MEASURED`. Nunca declarar capacidade
produtiva, SLA, SLO, autoscaling, piloto ou deploy a partir deste gate.

## Falha

Preserve logs somente no runner, não no artifact. O artifact contém apenas a
evidência allowlisted. Em falha, sempre destrave MinIO, termine APIs/workers e remova
o container. Não reduza Redis para memory para fazer o gate passar.
