# Registro de entrega — CTO-CODEX-SPEC-003

**Data:** 2026-09-08
**Agente:** Codex
**Status:** AR — especificação entregue; revisão técnica e perfil real de controlador pendentes

## Objetivo

Propor a arquitetura de torneamento XZ antes de qualquer implementação CAM.

## Escopo

Somente documentação, baseada na ordem recebida do Gemini e continuidade técnica
autorizada pelo proprietário. Baseline local b86f51e, branch
`codex/v3.1-first-controlled-test-path`. Sem push/merge/tag/publicação.

## Arquivos criados

- [ADR-0037](../adr/ADR-0037-turning-geometry-and-toolpath-foundation.md), próxima
  numeração após ADR-0036, em estado PROPOSED.
- Este registro de entrega.

## Arquivos modificados

- [DECISIONS.md](../DECISIONS.md): DEC-047 PROPOSED.
- [Índice ADR](../adr/README.md), [CONTEXT.md](../../CONTEXT.md) e
  [CHANGELOG.md](../../CHANGELOG.md): rastreabilidade da proposta.

## Contratos definidos

Perfil radial/Z e prova de eixo comum do BRep; datum frontal e conversão única
para X em diâmetro. Stock cilíndrico com posição/sobremetais/fixação explícitos.
Ferramenta externa com raio de ponta, ângulos, envelope e orientação 1..9
vinculada a mapeamento validado. Faceamento/cilindramento reto; cones apenas
reconhecidos, sem operação cônica inicial. Trajetória linear e verificador próprio.

O cabeçalho ISO/Fanuc sugerido foi tratado como requisito semântico, pois a
documentação primária Haas comprova significado diferente para G90/G94/G95 em
torno. Não foi escolhido Haas nem um Fanuc real. Sem perfil validado:
`CONTROLLER_PROFILE_UNRESOLVED`, nenhuma emissão NC. Fontes e pendências no ADR.

## Testes realizados

Suíte completa API, sem alterações de código: **402 passed, 2 skipped, 0 failed**
em **123.08 s**. Skips de Redis real em auth security store e jobs; sem resumo de
warnings. Python local 3.14.6 experimental; não equivale ao CI remoto em 3.13.11.
Log local ignorado: `.pytest_cache/spec003-pytest.log`.

Validação documental: 21 links relativos dos seis arquivos de entrega válidos;
UTF-8 e cercas Markdown PASS; tabelas revisadas e `git diff --check` PASS.
Nenhum teste novo foi criado para esta alteração documental.

## Critérios de aceitação

Contratos e exclusões documentados; proposta não confundida com implementação;
numeração sequencial preservada; suíte existente íntegra. A semântica incorreta
de um cabeçalho genérico não foi promovida a programa de torno. G9 permanece
`PENDING_AUTHORITATIVE_REVIEW`, `PHYSICAL_USE_AUTHORIZED=false`, NON_PRODUCTION.

## Próximos passos e handoff ACP

Revisar diff e registrar commit local, enviar a entrega ao CTO, solicitar parecer
e nova ordem, aguardar resposta e continuar o trabalho técnico autorizado.
O ciclo não termina apenas por emitir uma entrega ou receber nova missão.
Ainda faltam seleção real de controlador/manual, ferramenta, fixação e revisão
de engenharia para etapas que dependam desses dados; a proposta abstrata está pronta.

## Envio ao CTO

Commit local `9b5a83b4c199b4a2e51426adc371e700e98aaa8f`, seis arquivos,
297 inserções/2 remoções. Árvore limpa no encerramento do commit. Relatório
transmitido ao [CTO Gemini](https://gemini.google.com/app/62dacc664840eafe)
com contratos, fontes, testes, ressalva do dialeto e solicitação de nova ordem.
Parecer recebido: APROVADO COM RESSALVAS, por análise do relatório. Correção de
dialeto aceita; próxima ordem IMPL-004 recebida e iniciada. O parecer confundiu
a contagem local: 9b5a83b tinha quatro commits sobre d798417, incluindo b86f51e.
Esta correção de rastreabilidade será enviada junto à próxima entrega.
