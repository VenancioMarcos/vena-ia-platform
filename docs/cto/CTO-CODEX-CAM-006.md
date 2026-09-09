# Registro de execução — CTO-CODEX-CAM-006

**Missão vigente:** CTO-CODEX-CAM-006A (substitui CAM-006).
**Estado:** commit d3785d3 entregue ao CTO; aguardando parecer e próxima ordem.

## Objetivo

Planejar passes matemáticos de faceamento/cilindramento em raio/Z, conforme ordem
Gemini recebida em 2026-09-09 após aprovação AR de STEP-005 por relatório.

## Escopo e dependências identificadas antes de implementar

A ordem solicita schemas de movimentos RAPID/CUTTING/RETRACT e operações imutáveis,
planner consumindo TurningProfile2D/StockCylinder/ToolDefinition, testes de stock,
sobremetal e undercut. Sem NC/pós/fresamento/push; commit local apenas.

O ADR-0037 exige fixação e corpo não cortante para validar toolpath. Os modelos
mínimos IMPL-004 não os contêm. Também faltam datum do stock, limites/folgas,
avanço/depth-of-cut fundamentados, ponto de referência/orientação/compensação da
pastilha. O campo pedido `is_collision_free` não pode ser verdadeiro por inferência.

## Proposta concreta encaminhada ao CTO

Delimitar este incremento como plano matemático sintético de ponto ideal, isolado
do runtime e sem compensação de ponta. Todos os parâmetros numéricos de passes,
sobremetais e folgas explícitos, sem default de material/máquina. Stock frontal
em Z=face_allowance e fundo=face_allowance-length conforme convenção documentada.
Validar envelope final e stock, monotonicidade não decrescente do raio exterior
ao avançar em Z negativo (sem undercut), finitude, limites de recursos e comprimento
geométrico de corte. `is_collision_free` fixo false, estado de colisão NOT_VALIDATED;
sem autorização física ou ponte para pós. Testes usam somente dados sintéticos.

Se o CTO exigir toolpath com geometria real da ferramenta ou garantia de ausência
de colisão, primeiro fornecer schemas/entradas de setup, fixação, orientação e
envelope e verificador independente; não preencher lacunas automaticamente.

## Arquivos criados/modificados

Após resolução CAM-006A:
- [turning_toolpath_schemas.py](../../apps/api/app/modules/engineering/turning_toolpath_schemas.py)
- [turning_planner.py](../../apps/api/app/modules/engineering/turning_planner.py)
- [test_turning_planner.py](../../apps/api/tests/modules/engineering/test_turning_planner.py)
- Registro, ADR/DEC-047, CONTEXT/CHANGELOG e continuidade CTO.

## Testes realizados

Primeiros 15 testes específicos PASS em 3.18 s. Revisão acrescentou alvo exato
em cada diâmetro escalonado; suíte completa em execução. Ruff PASS; mypy PASS em
190 fontes. Baseline STEP-005: 469 passed/2 skipped, commit local 57a0fcf.
Sem máquina, publicação ou CI remoto. Testes sintéticos com STEP do corpus.

Cobertura: faceamento, degraus, ap máximo e último passe fracionário, raio e
sobremetais radial/axial, sequência contínua, comprimento e replay; stock estreito/
curto, undercut/taper, raio negativo, coerções/NaN/Inf, autoridade verdadeira
rejeitada, stock sem remoção e orçamento de passes.

## Critérios de aceitação e próximos passos

Ordem CAM-006A confirmada e implementada. Concluir validação, documentar, commit
local, enviar resultado e aguardar próxima ordem. Sem colisão validada ou NC.


## Resolução recebida — CAM-006A

Gemini acolheu o conflito e aprovou a Variante A explicitamente, emitindo a
CAM-006A em substituição à CAM-006. Somente modelo sintético de ponto ideal.
Não consumir nem inventar geometria de ferramenta; todos os campos de autoridade
permanecem falsos e colisão NOT_VALIDATED. Esta exceção técnica ao ADR será
registrada em DEC-047 e não libera uso do planner em runtime ou no pós.

Parâmetros explícitos: profundidade axial/radial máxima por passe, sobremetal
radial/axial e folga de retração; modo de avanço sem valor de processo físico.
O último passe pode ser menor que ap para preservar a cota de acabamento; nunca
arredondar para cortar abaixo do envelope. Sobremetal axial preserva a frente e
os ombros acessíveis, sem usinar a face traseira. Comprimento é comprimento dos
segmentos CUTTING do ponto ideal, incluindo trecho no ar, não remoção/tempo real.
No máximo 1000 passes por operação e 10000 movimentos por plano.


## Ajustes da revisão e evidência

Cada região escalonada recebe passe no seu alvo radial exato, inclusive quando
ap não divide o sobremetal. O último passe por região pode ser menor que ap;
o algoritmo não deixa material extra por depender apenas de uma grade global.
Também interrompe a sequência ao atingir o alvo, evitando passe duplicado por
ceil de ponto flutuante; profundidade sem resolução numérica falha fechado.

Primeira regressão completa: 484 passed/2 skipped em 127.27 s. Caso fracionário
acrescentado e corrigido: 16 testes específicos PASS em 3.48 s.
**Suíte API final: 485 passed (469 legados + 16 novos), 2 skipped, 0 failed em 131.63 s.** Ruff/mypy finais PASS, 190 fontes. Nenhum CI remoto.


## Validação final e entrega

Ruff PASS; mypy PASS em 190 fontes; 13 links relativos válidos; diff check PASS.
Skips de Redis real auth/jobs preservados. Python 3.14.6 experimental; sem
resumo de warnings, sem CI remoto. Log local ignorado:
`.pytest_cache/cam006a-final-pytest.log`.

Critérios atendidos no escopo CAM-006A sintético: passes e sobremetais testados,
limites fechados e autoridade/colisão não promovidas. Commit local e envio ao
CTO são os próximos passos; solicitar parecer e aguardar nova ordem.


## Commit e envio

Commit d3785d3bffa16189ff1e478957307988127ea0c4, 12 arquivos,
587 inserções/10 remoções. Working tree limpa após commit. Entrega enviada ao
Gemini na conversa CTO autorizada; solicitados parecer e nova ordem. Aguardando
resposta real. Sem push ou NC.

Parecer posterior recebido: AR por relatório. CAM-007 emitida e substituída por
CAM-007A após objeção técnica do Codex; ver registro CTO-CODEX-CAM-007.md.
