# Registro de entrega — CTO-CODEX-IMPL-004

## Objetivo

Implementar o incremento mínimo de schemas e verificação preliminar de eixo comum,
conforme ordem recebida do Gemini após revisão AR da SPEC-003 em 2026-09-08.

## Escopo

Schemas Pydantic estritos e helper CAD isolado, testes sintéticos e BRep real.
Não integrar endpoints, extrator de perfil, CAM, pós ou fresamento. Commit local
na branch atual; sem push/merge/publicação. ADR-0037 aprovado tecnicamente apenas
para esta fundação; contratos completos e controlador ainda pendentes.

Os cinco schemas da missão são um subconjunto preliminar do ADR, sem claim de
proveniência/stock/ferramenta completos. ControllerProfileRequirement declara modo
DIAMETER ou RADIUS, mas não homologa nenhum deles nem emite NC. O modo programado
proposto continua DIAMETER. Campos desconhecidos, coerções e NaN/Inf falham fechado.

O verificador diferencia coincidência de direções de coincidência de retas,
aceita sentido invertido e deslocamento ao longo da reta, compara todos os pares
com tolerâncias explícitas e limites de recursos. Adapter BRep verifica todas as
faces, tipo/topologia, planos normais e cobertura angular analítica completa.
Sucesso é apenas AXISYMMETRY_PRELIMINARY_PASS, nunca perfil extraído, prova global
de torneabilidade ou autorização física; furos concêntricos ainda exigem extrator.

## Arquivos criados

- [turning_schemas.py](../../apps/api/app/modules/engineering/turning_schemas.py)
- [axisymmetry.py](../../apps/api/app/modules/cad/axisymmetry.py)
- [test_turning_schemas.py](../../apps/api/tests/modules/engineering/test_turning_schemas.py)
- [test_axisymmetry.py](../../apps/api/tests/modules/cad/test_axisymmetry.py)
- Este registro.

## Arquivos modificados

ADR-0037/DEC-047 e índice, CONTEXT, CHANGELOG, handoff SPEC-003 e
CURRENT_ORDER/ORDER_HISTORY/EXECUTION_STATUS para continuidade sem ordem obsoleta.

## Testes realizados

**455 passed, 2 skipped, 0 failed em 134.88 s**: 402 legados + 53 novos.
Skips inalterados de Redis real (auth/jobs); sem resumo de warnings. Ruff PASS;
mypy PASS em 187 fontes; diff check PASS. Python 3.14.6 local experimental,
sem novo CI remoto. Log ignorado `.pytest_cache/impl004-pytest.log`.

Casos: coerção/extras/NaN/Inf; stock sem comprimento restante; direção unitária;
fechamento declarado e roundtrip JSON; raio versus diâmetro; controlador nunca
resolvido; todos os pares de retas, sentido inverso/deslocamento axial, offset
lateral/inclinação, tolerâncias e overflow. OCCT real: cilindro/cone orientados,
furos excêntricos, esfera/caixa/cilindro parcial, compound/null/objeto inválido e
mesmas coordenadas com tolerância em mm versus polegadas. Nenhum endpoint alterado.

## Critérios de aceitação

Rejeitar dimensões/valores inválidos; rejeitar eixos deslocados/inclinados e faces
não suportadas; preservar contratos de fresamento e todos os limites físicos.

## Próximos passos

Validação concluída; registrar commit local e enviar resultado ao CTO, pedir e
aguardar nova ordem, mantendo o ciclo autorizado sem depender de novo comando
do usuário. Sem extrator de perfil ou validação global de revolução nesta entrega.
