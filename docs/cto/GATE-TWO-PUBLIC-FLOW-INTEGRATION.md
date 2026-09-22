# Relatório de Entrega — GATE TWO — Public Flow Integration

**Data:** 2026-09-21
**Estado:** `GATE_TWO_PUBLIC_FLOW_INTEGRATION_READY_FOR_CTO_REVIEW`
**Branch:** `codex/gate-two-public-flow-integration`
**Baseline autorizado:** `5fa8cc31cdbd111c50925b5ab239534c4649298b`

## 1. Identificação

Execução do Gate Dois autorizado após homologação do Gate Um, limitada à jornada
pública do Beta 1 e sem abertura antecipada do Gate Três.

## 2. Objetivo

Entregar um caminho contínuo de cadastro, login, criação de projeto, upload STEP,
processamento controlado, visualização técnica, revisão humana persistida,
download do candidato e feedback vinculado ao resultado.

## 3. Escopo executado

Foram integrados onboarding automático, fluxo STEP, viewer técnico existente,
persistência de revisão, gate de download, feedback e cobertura ponta a ponta.
Nenhum deploy, serviço externo, merge ou publicação foi executado.

## 4. Branch e baseline

A implementação está na branch local `codex/gate-two-public-flow-integration`,
criada no baseline preservado `5fa8cc3`, conforme a ordem do CTO.

## 5. Onboarding automático

O cadastro cria atomicamente uma organização padrão, membership `OWNER` e três
catálogos organizacionais iniciais: `MATERIAL`, `MACHINE` e `TOOL`. Falha na
transação impede estado parcial.

## 6. Jornada de projeto e STEP

O projeto aceita PDF e STEP. Um STEP recém-enviado aparece imediatamente e conduz
o usuário ao ambiente controlado; o processamento genérico de PDF/RAG não é
oferecido para STEP.

## 7. Preparação assistida

A primeira organização, os três catálogos e o primeiro documento STEP são
selecionados automaticamente. Fixture, datum, holdout e referência selada recebem
valores conservadores e revisáveis quando o usuário não os informa.

## 8. Resultado técnico integrado

`MachiningTechnicalReportViewer` passou a renderizar também o resultado do
ambiente controlado, exibindo modelo geométrico, toolpath, digital thread, G9,
classificação e ausência de autorização física.

## 9. Persistência do resultado

Cada execução cria `controlled_result_records` com usuário, organização, projeto,
documento, versão e hashes canônicos do G-code candidato, validação cega, digital
thread e token de download.

## 10. Revisão humana persistida

As rotas `GET/POST /product-flow/results/{result_id}/review` registram nota,
revisor e instante da revisão. Marcar a confirmação somente no navegador não
libera o download.

## 11. Gate de download

O endpoint de download exige resultado pertencente ao usuário, revisão persistida
e igualdade de organização, artefatos e token com os hashes registrados. Ausência
de revisão retorna 409; alteração de vínculo retorna 422.

## 12. Feedback integrado

As rotas `GET/POST /product-flow/results/{result_id}/feedback` persistem nota de 1
a 5 e comentário opcional, vinculados ao resultado, projeto, versão e usuário. A
restrição única impede avaliações duplicadas do mesmo usuário para o resultado.

## 13. Banco de dados e migração

A migração `a71c9e4d2b80` cria `controlled_result_records` e `result_feedback`,
índices, chaves estrangeiras, checks de estado/rating e downgrade reversível. O
grafo Alembic possui uma única head.

## 14. Contratos e API

Os contratos Pydantic permanecem estritos. O resultado expõe `result_id`; o
download o exige. Schemas próprios validam acknowledgement literal, nota mínima,
rating e limites de comentário.

## 15. Testes realizados

- Backend completo: `1100 passed, 2 skipped`.
- Backend focado: `45 passed`.
- Web unitário: `122 passed` via script agora executado pelo Frontend CI.
- Playwright completo: `10 passed` em desktop e largura reduzida.
- TypeScript estrito e build Next de produção: aprovados.
- Ruff: aprovado; mypy: 246 fontes aprovadas; Alembic: head única.
- `git diff --check`: aprovado.

## 16. Critérios de aceitação

Todos os estágios pedidos são percorridos no cenário do navegador. O teste prova
que a confirmação local mantém o download desabilitado, a revisão persistida o
libera, o arquivo é baixado e o feedback 5/5 é registrado. O teste backend usa um
STEP real e confirma a mesma sequência pela API.

## 17. Segurança e invariantes

Permanecem: `PHYSICAL_USE_AUTHORIZED=FALSE`,
`G9=PENDING_AUTHORITATIVE_REVIEW`, `NO_HUMAN_REVIEW_BYPASS=TRUE`,
`MACHINE_SEND=FALSE`, `DNC=FALSE`, `NC_TRANSFER=FALSE`,
`CYCLE_START=FALSE` e `executable_output=false`. A revisão autoriza apenas o
download controlado do candidato e não aprova G9.

## 18. Estado final e próxima ação

O Gate Dois está implementado, documentado e validado localmente, pronto para
parecer formal do CTO. Aguardar a próxima ordem sem iniciar Gate Três, push,
merge, release ou deploy.

## Registro de Entrega — PROJECT.md §19

**Objetivo:** integrar a jornada pública controlada do Beta 1.

**Escopo:** onboarding, STEP, resultado técnico, revisão persistida, download e
feedback.

**Arquivos criados:** módulo `product_flow`, migração `a71c9e4d2b80`, runner Web,
ADR-0038 e este relatório.

**Arquivos modificados:** autenticação, engenharia, contratos, projeto Web,
ambiente controlado, viewer, CI, testes e documentos de continuidade.

**Testes realizados:** descritos na seção 15.

**Critérios de aceitação:** descritos na seção 16.

**Próximos passos:** solicitar parecer do CTO e aguardar nova ordem.
