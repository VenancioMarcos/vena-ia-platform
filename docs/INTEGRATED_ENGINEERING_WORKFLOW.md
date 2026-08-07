# Integrated Engineering Workflow v1

## Objetivo e contrato

`POST /engineering/workflows` aceita referências explícitas a um documento STEP,
uma feature local e, quando disponíveis, itens de catálogo e contexto de processo.
A resposta usa `vena-ia.integrated-engineering-workflow/v1` e compõe:

`geometry-analysis/v1` → `geometry-features/v1` →
`engineering-recommendation/v1` → `feature-planning/v1` →
`cnc-neutral-plan/v1` → `integrated-engineering-report/v1`.

O serviço é síncrono, efêmero e determinístico. Ele baixa/analisa o STEP uma única
vez e passa o resultado já carregado ao planning. O `workflow_id` é SHA-256 canônico
do contrato e dos inputs; timestamps são a única diferença esperada em replay.

## Estados fechados

* `COMPLETE_PRELIMINARY`: cadeia preliminar composta, nunca aprovada para produção;
* `PARTIAL`: evidência existe, mas incompatibilidade ou outra limitação impede avanço;
* `BLOCKED_MISSING_INPUT`: toda ausência permanece listada;
* `BLOCKED_UNSUPPORTED_FEATURE`: não há candidate allowlisted;
* `FAILED`: reservado a falha explícita, nunca convertido em sucesso.

`REQUIRES_HUMAN_REVIEW` é obrigatório no workflow e no relatório. Nenhum input via
body/header define usuário, owner, Organization, Team, role ou regra. A autenticação
e o acesso ao documento permanecem sob JWT+banco e ownership do projeto; acesso
cross-user ou cross-org falha como 404.

## Inputs e rastreabilidade

Catálogos material/máquina/ferramenta são referências existentes. Manufacturing
intent, tolerância, acabamento, fixture, coolant, condição do material, tool number
e clearance são explícitos; não existem defaults ocultos. O fluxo preserva source
document, schema versions, kernel/rule versions, catalog versions, feature,
recommendation, planning, plano CNC neutro e report refs.

Catálogos Engineering continuam globais autenticados no Package 1. O workflow não
altera sua tenancy nem os apresenta como recursos Organization-scoped.

## Limites absolutos

CAM preliminar significa somente process planning: operation candidates, assumptions,
compatibilidade, parâmetros e estimativas. O contrato não aceita nem produz toolpath,
coordenadas, cutter-location data, pós-processador, G-code, M-code, NC/DNC,
transmissão ou controle de máquina. `NON_PRODUCTION` e revisão humana permanecem
obrigatórios. Packages 2 e 3 não fazem parte desta entrega.

## Registro de Entrega

### Objetivo

Compor o primeiro workflow determinístico integrado da plataforma.

### Escopo

Package 1 exclusivamente: contratos, orquestração, API, testes e documentação.

### Arquivos criados/modificados

Módulo workflow em `apps/api/app/modules/engineering`, extensão aditiva do módulo
`cnc`, testes focais e documentos técnicos/de governança relacionados.

### Testes realizados

Ruff, mypy, testes focais e regressão integral; os resultados terminais são
registrados em `docs/cto/EXECUTION_STATUS.md` e na Draft PR funcional.

### Critérios de aceitação

Cadeia rastreável, replay determinístico, estados fail-closed, isolamento preservado,
revisão humana obrigatória e ausência de output CNC executável.

### Próximos passos

Revisão do CTO. Package 2 permanece `NOT_STARTED` até ordem oficial específica.
