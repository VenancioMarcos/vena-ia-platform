# Evidência reproduzível — v1.6 Package 1

**Schema:** `vena-ia.runtime-evidence/v1`
**Data:** 2026-08-05
**Ambiente:** local controlado + GitHub Actions
**Dados:** somente versões, comandos e resultados agregados

## Proveniência

Os digests foram resolvidos com `docker buildx imagetools inspect` diretamente no
registry oficial. Tags de GitHub Actions foram resolvidas pela API oficial e os
workflows usam os SHAs completos. O manifesto versionado é `runtime-policy.json`.

## Avaliação Python

* 3.13.11: oficial, container e gate principal do Backend CI.
* 3.14.6: experimental; venv descartável com instalação limpa, imports binários,
  Ruff, mypy, 251 testes de API e 49 testes operacionais locais passaram. Isso não
  amplia suporte e não substitui o CI 3.13.11 com PostgreSQL/pgvector, Redis e
  MinIO reais.

## Comandos reproduzíveis

```text
python scripts/runtime_policy.py
python -m pytest tests/operations/test_runtime_policy.py
python -m ruff check .
python -m mypy apps/api/app packages/ai scripts
python -m pytest apps/api
python -m pytest tests/operations
pnpm --dir apps/web install --frozen-lockfile
pnpm --dir apps/web run typecheck
pnpm --dir apps/web run build
docker compose config --no-env-resolution --quiet
```

O Runtime Policy CI também constrói as imagens API e Web diretamente dos
Dockerfiles fixados. O Backend CI permanece a evidência definitiva para serviços
reais e backup/restore quando o daemon local estiver indisponível.

## Limitações

O ambiente local usa Node 24.14.0 fornecido pelo executor, fora da versão oficial;
o gate Node 22.20.0 ocorre no CI e no container. O daemon Docker local não estava
disponível, portanto nenhum build ou start local é declarado PASS. Não existe
scanner dedicado de vulnerabilidades/SBOM nem lock transitive Python
multiplataforma. Nenhuma evidência contém caminho pessoal, e-mail, segredo ou dado
real.
