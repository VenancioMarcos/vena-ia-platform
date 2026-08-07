# Specialized Assistance v1

## Fronteira pública

`POST /engineering/workflow-assistance` recebe inputs reproduzíveis do workflow,
reconstrói o snapshot autorizado e retorna `vena-ia.specialized-assistance/v1`.
Não existe lookup falso de workflow persistido. Os perfis allowlisted são:

* `CAD_ANALYSIS`;
* `MANUFACTURING_ENGINEERING`;
* `RESEARCH`;
* `DOCUMENTATION_REPORTING`.

Eles são modos bounded de explicação, não agentes autônomos. Reutilizam `AIService`
e não recebem tools, memória, fila, provider, vector store ou autoridade de escrita.

## Autoridade e replay

`vena-ia.integrated-engineering-workflow/v1` permanece a autoridade imutável. A
resposta generativa é separada de `source_workflow`; testes comparam o snapshot
antes/depois e verificam workflow status, recommendation, planning, CNC neutral,
`executable_output`, rules e catalog versions. `deterministic_input_trace` cobre
profile, pergunta, workflow/schema, evidence e template, mas não exige texto idêntico.

## Context allowlist e falha segura

Cada profile recebe somente fatos necessários. Tokens, secrets, logs internos, PII,
authority fields e machine targets não entram no context builder. Catálogos são
marcados `GLOBAL_AUTHENTICATED_NOT_ORGANIZATION_SCOPED`; a assistência não os chama
de catálogo da organização. Falha de provider retorna `FAILED`, sem mutar o workflow.

Output vazio, claim de autoridade produtiva/científica ou linha com sintaxe potencial
G/M-code é bloqueado. Todo contrato fixa `NON_PRODUCTION`,
`REQUIRES_HUMAN_REVIEW`, `simulation_only=true` e `executable_output=false`.

## Apresentação Package 3

O dashboard mantém `AI ASSISTANCE` separada do resultado determinístico e apresenta
profile, status, resposta, evidence, citations, missing evidence, warnings,
limitations, review status e input trace. Erro do provider e output bloqueado ficam
visíveis; nenhum texto da IA altera o snapshot fonte.

## Limites

Não há toolpath, coordenadas, postprocessor, G/M-code, NC/DNC, transmissão, machine
control, produção, conformidade, certificação ou decisão científica.

## Registro de Entrega

### Objetivo

Adicionar explicação especializada e Research grounded sem transferir autoridade à IA.

### Escopo

Package 2 exclusivamente: contratos, context builder, AIService/RAG/Research reuse,
output validation, API, testes e documentação.

### Arquivos criados/modificados

Módulo assistance em `apps/api/app/modules/engineering`, extensão aditiva dos schemas
Research, testes focais e documentação técnica/de governança.

### Testes realizados

Ruff, mypy, testes assistance/Research, regressão Package 1 e regressão terminal.

### Critérios de aceitação

Snapshot imutável, citations estruturadas, missing evidence fail-closed, provider
failure seguro, limites científicos e ausência de CNC executável.

### Próximos passos

Packages 1–3 foram publicados em `v2.0.0`. Orchestration, tools de escrita e agentes
stateful continuam proibidos sem nova decisão formal.
