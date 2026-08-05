# Runbook — atualização de runtimes e imagens

## Objetivo

Atualizar `runtime-policy.json`, Dockerfiles, Compose e CI sem deriva, upgrade
silencioso, perda de dados ou merge automático.

## Procedimento

1. Criar branch dedicada a partir da `main` limpa.
2. Consultar release notes e política de suporte na fonte oficial.
3. Confirmar origem, licença, arquitetura e existência do artefato.
4. Resolver a tag explícita e o digest do índice multi-arquitetura no registry.
5. Alterar primeiro `runtime-policy.json`; alinhar Dockerfiles, Compose, CI e matriz.
6. Executar `python scripts/runtime_policy.py` e os testes da policy.
7. Instalar runtimes limpos e executar Ruff, mypy, pytest, Alembic, operações,
   worker/jobs/recovery, frontend frozen/typecheck/build e Compose config.
8. Construir API/Web e validar serviços reais no CI; para banco/storage, executar
   migrations, backup/restore e compatibilidade de dados descartáveis.
9. Registrar fonte, digest, data, comandos, resultados, licença e limitações.
10. Submeter Draft PR; nenhuma automação pode fazer merge sem revisão.

Revisão programada: trimestral. Advisory crítico, revogação de imagem ou fim de
suporte antecipam a revisão, mas nunca dispensam os gates.

## Comandos mínimos

```text
docker buildx imagetools inspect <imagem:tag>
python scripts/runtime_policy.py
python -m ruff check .
python -m mypy apps/api/app packages/ai scripts
python -m pytest apps/api
python -m pytest tests/operations
docker compose config --no-env-resolution
docker build -f apps/api/Dockerfile .
docker build -f apps/web/Dockerfile apps/web
```

Nunca copiar `.env`, token, cookie ou credencial para evidência ou camada Docker.

## Rollback

1. Interromper a promoção; não mover tag nem sobrescrever imagem publicada.
2. Restaurar em nova alteração os valores anteriores de `runtime-policy.json` e
   arquivos alinhados, usando os digests imutáveis registrados no Git.
3. Para PostgreSQL/MinIO, não reutilizar volume após upgrade incompatível: criar
   alvo descartável e restaurar backup verificado conforme os runbooks oficiais.
4. Reexecutar policy, regressão, migrations, readiness e backup/restore.
5. Documentar causa, impacto e decisão. Merge continua sujeito a revisão humana.

Volumes persistentes e nomes do Compose não são removidos por este runbook.
