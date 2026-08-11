# Manufacturing Geometry Model v1

## Objetivo

Construir a ponte determinística geometry→manufacturing→planning sem confundir
geometria com intenção e sem produzir trajetória ou código executável.

## Contratos

* `vena-ia.manufacturing-geometry-model/v1` — stock/final/removal/protected/unknown,
  access, datum, WCS, setup, intent, recursos, operações candidatas e limitações.
* `vena-ia.verified-process-plan/v1` — ordem/dependências e parâmetros preliminares.
* `vena-ia.planning-verification-evidence/v1` — coerência, coverage, missing inputs,
  resource compatibility, precedence, setup feasibility e replay hash.

## Regras

Stock só é aceito como `PROVIDED` ou `DERIVED_FROM_AUTHORIZED_CONFIGURATION` com
bounds mm e provenance. `MISSING`, `AMBIGUOUS`, `INVALID` e não contenção falham
fechado. O envelope final nunca é promovido a stock.

As regiões fora do envelope final são seis slabs máximos, não sobrepostos. Material
dentro do envelope mas fora do B-Rep permanece `UNKNOWN_WITHIN_FINAL_ENVELOPE`; não
há claim de decomposição booleana detalhada. Faces finais são protegidas por default.

Accessibility usa somente normais planares cardinais para candidatos 3-axis/2.5D.
Datum/WCS/setup exigem revisão/fixture. Não existe offset ou setup produtivo.

`ASK_ONLY_WHEN_BLOCKING` lista field, reason, gate, tipo/unidade e evidence ausente.
Operação exige manufacturing intent explícito e recursos autorizados. Cilindro não
vira drilling; target adicional confirmado é obrigatório. Roughing precede finishing
somente quando ambos decorrem de inputs explícitos.

## Segurança

`executable_output=false` em modelo e operações. Planning verification não é
material-removal simulation, cutter sweep, collision ou machine kinematics.

`CAD_TO_GCODE_CONTROLLED_VALIDATION_READY = FALSE`

`PHYSICAL_USE_AUTHORIZED = FALSE`

Sem toolpath, cutter location, postprocessor, RS274, G/M-code, NC/DNC, machine-send,
cycle start ou controle direto de máquina.

## Registro de Entrega

### Objetivo

Interpretar evidência geométrica sob stock/intent/resources explícitos e gerar plano
candidato verificável, não executável.

### Escopo

Modelos, serviço, endpoint, corpus sintético, autorização, replay e documentação.

### Arquivos criados

Manufacturing schemas/service, testes, esta especificação e ADR-0032.

### Arquivos modificados

Rota Engineering, evidence geométrica, arquitetura, roadmap, decisões, riscos,
contexto, changelog e status CTO.

### Testes realizados

Focais CAD/manufacturing/Engineering/workflow, Ruff, mypy, OpenAPI, auth/cross-org,
Alembic e Backend CI.

### Critérios de aceitação

Stock fail-closed, protected/removal/unknown, access/setup, missing inputs, recursos,
precedência/replay, no false manufacturing claim e zero output executável.

### Próximos passos

Revisão técnica da v2.2 completa. v2.3 não inicia nesta missão.
