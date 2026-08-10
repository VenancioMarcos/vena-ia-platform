# General Geometry Topology Evidence v1

## Objetivo

`vena-ia.geometry-topology-evidence/v1` registra evidência geométrica geral e
reproduzível do B-Rep importado pelo OpenCascade. Ele não reconhece intenção de
manufatura e não substitui `geometry-analysis/v1` ou `geometry-features/v1`.

## Escopo e arquitetura

O `GeometryEvidenceBuilder` recebe o shape já carregado pelo
`OpenCascadeGeometryKernel`. O resultado é efêmero e aditivo no endpoint CAD
autorizado. Não há segundo parser/kernel, persistência, migration ou microserviço.

## Contrato

O payload inclui:

* SHA-256 da fonte, formato, kernel, binding e versões do schema/stable-ID;
* unidade original, unidade normalizada, escala e representação de transformação;
* validade/tipo do shape e contagens de solid/shell/face/wire/edge/vertex;
* IDs, bounds, orientação, métricas, contenção, adjacência e conectividade;
* surface types plane/cylinder/cone/sphere/torus/BSpline/other;
* curve types line/circle/ellipse/BSpline/other;
* tolerâncias de kernel, modelagem e manufatura separadas;
* warnings, unsupported, limitations, provenance e evidence references.

## Stable IDs e ambiguidade

O ID é SHA-256 truncado de schema de ID, versão do kernel, classe topológica,
descritor canônico arredondado e ocorrência. Não usa endereço de memória, object
identity ou hash incidental do binding. Elementos com descritor indistinguível
recebem `ambiguity_group`; a identidade é válida somente dentro das versões de
kernel e algoritmo declaradas. Replay do mesmo arquivo/corpus é teste obrigatório.

## Units, transform e tolerance

OCCT expõe o shape transferido em coordenadas globais normalizadas. `mm`, `m` e `in`
possuem escala explícita para milímetro. Unidade `UNKNOWN` retorna
`UNIT_AMBIGUOUS` sem elementos. `kernel_tolerance` e `modeling_tolerance` são
evidência geométrica; `manufacturing_tolerance` é sempre `NOT_PROVIDED` nesta versão.

## Bounds e segurança

Upload STEP mantém o limite existente de 50 MiB. A travessia possui limite de 50.000
elementos, deduplica subshapes e transforma falhas em estado seguro. Topologia
inválida não produz relações. O corpus é exclusivamente sintético e versionável.

## Limitações

Sem manufacturing interpretation, stock/removal, setup, process planning, tooling,
toolpath, postprocessor, G/M-code, NC/DNC, machine-send ou autoridade física. Toda
saída exige revisão humana. `CAD_TO_GCODE_CONTROLLED_VALIDATION_READY = FALSE` e
`PHYSICAL_USE_AUTHORIZED = FALSE`.

## Registro de Entrega

### Objetivo

Criar a fundação geométrica geral necessária antes da interpretação de manufatura.

### Escopo

Contrato/read model aditivo, integração no CAD, corpus sintético, testes e docs.

### Arquivos criados

`evidence.py`, testes focais, esta especificação e ADR-0031.

### Arquivos modificados

Kernel, service, schemas, rota CAD, arquitetura, roadmap, decisões, riscos, contexto,
changelog e status CTO.

### Testes realizados

Ruff, mypy, Pytest focal/integral, regressões CAD/features/workflow, OpenAPI,
Alembic single head e diff/secret checks.

### Critérios de aceitação

Replay, IDs versionados, unidade ambígua/topologia inválida fail-closed, relações,
classificações, tolerâncias separadas, compatibilidade e ausência de output CNC.

### Próximos passos

Revisão do CTO. Package 2 não inicia nesta missão.
