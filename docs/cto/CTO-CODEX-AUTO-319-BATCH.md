# Registro de Entrega — CTO-CODEX-AUTO-314 a AUTO-319

**Data:** 2026-09-14
**Estado:** `CNC_TOOL_WEAR_GEOMETRY_AUDITOR_COMPLETED_LOCAL`
**Branch:** `codex/v8.5-cnc-tool-wear-compensation-geometry-auditor`
**Baseline:** `dd099b0deb29a11dd96deb827ca9a540ae76c50a`
**Publicação:** pendente da AUTO-320

## Objetivo e escopo entregue

A Rota 24 implementa o auditor determinístico de desgaste geométrico da ferramenta.
O serviço consome o percentual Taylor, calcula `VB = VBmax·sqrt(consumo/100)`,
projeta o desvio radial pelo ângulo de folga, o desvio axial pelo ângulo de posição
e deriva o raio de ponta efetivo. O ângulo de posição aceita insertos com geometria
suplementar, como CNMG a 95°, mas rejeita limites, 90° e valores não finitos.

O manifesto v1 incorpora o contrato Pydantic v2 e valida o vínculo integral ao
snapshot Taylor. O laudo TEXT e o painel Web exibem VB, desvio radial, raio de
ponta efetivo, percentual da tolerância e badges. O warning é acionado quando o
desvio radial consome mais de 50% da tolerância declarada.

## Arquivos criados e modificados

- Criado: `apps/api/app/modules/cnc/services/tool_wear_geometry_auditor.py`.
- Modificados: contratos CNC, compilador de laudo e exportador TEXT em `apps/api`.
- Modificados: viewer e testes do laudo técnico em `apps/web`.
- Atualizados: testes unitários, integração, `CONTEXT.md` e este registro.

## Testes e critérios de aceitação

- `247 passed` na suíte CNC; `41 passed` nos testes focados do contrato e laudo.
- `28 passed` no viewer Web.
- Ruff, mypy em 211 fontes, TypeScript, Next lint e `git diff --check` aprovados.
- Fontes transplantadas, cálculos adulterados, ângulos inválidos e valores não
  finitos falham fechado.
- Nota mandatória presente no JSON/TEXT/Web; nenhum controle de compensação física.

## Limites e próximos passos

`PHYSICAL_USE_AUTHORIZED=FALSE`; `G9=PENDING_AUTHORITATIVE_REVIEW`;
`NO_HUMAN_REVIEW_BYPASS=TRUE`; `MACHINE_SEND=FALSE`; `DNC=FALSE`;
`NC_TRANSFER=FALSE`; `CYCLE_START=FALSE`;
`emission_status=CONTROLLER_PROFILE_UNRESOLVED`; `executable_output=false`.

Publicar a branch, abrir o Draft PR #72, acompanhar CI e integrar por squash após
os gates exigidos nas AUTO-320 a AUTO-322.
