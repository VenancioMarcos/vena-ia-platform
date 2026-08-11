# Vena_IA Platform v2.2.0 — Advanced Engineering Planning & Verification

## Release

v2.2.0 fecha a cadeia determinística de evidência de geometria geral e interpretação
de manufatura com plano verificável. Esta release é estritamente `NON_PRODUCTION` e
mantém revisão humana obrigatória.

## General Geometry Evidence

`vena-ia.geometry-topology-evidence/v1` registra B-Rep, hashes, unidades,
transformação, tolerâncias, topologia e classificações geométricas sem inferir
feature, intenção de manufatura ou ferramenta.

## Manufacturing Planning

`vena-ia.manufacturing-geometry-model/v1` e
`vena-ia.verified-process-plan/v1` exigem stock com provenance, mantêm regiões de
remoção/protegidas/desconhecidas explícitas e produzem somente candidatos 3-axis/2.5D
de acessibilidade, datum, WCS, setup e operação. Recursos permanecem
organization-scoped e falham fechado.

`vena-ia.planning-verification-evidence/v1` comprova coerência, coverage lógica,
recursos, precedência, setup preliminar e replay. Não equivale a material removal,
colisão ou cinemática.

## Evidência de validação

- Ruff e mypy aprovados;
- API: `376 passed, 2 skipped`;
- regressão CAD/Engineering: `109 passed`;
- focal Package 2: `19 passed`;
- OpenAPI `2.2.0`, 80 paths;
- Alembic single head `e61c4f8a2b90`;
- Docker Compose config e Backend CI aprovados.

## Limites absolutos

`CAD_TO_GCODE_CONTROLLED_VALIDATION_READY = FALSE`.
`PHYSICAL_USE_AUTHORIZED = FALSE`.

Não há toolpath, cutter location, postprocessor, RS274, G-code, M-code, NC/DNC,
machine-send, cycle start, controle de máquina, deploy ou produção.
