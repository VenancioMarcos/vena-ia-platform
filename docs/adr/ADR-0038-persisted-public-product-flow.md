# ADR-0038 — Fluxo público controlado com revisão persistida

**Status:** Aceita
**Data:** 2026-09-21
**Decisão relacionada:** DEC-049

## Contexto

O Beta 1 já possuía cadastro, projetos, upload STEP, geração analítica controlada
e download de candidato. Esses estágios estavam separados: novas contas não
recebiam o contexto organizacional mínimo, o relatório técnico não fazia parte da
jornada STEP e a confirmação de revisão existia apenas no estado do navegador.

## Decisão

O cadastro passa a criar, na mesma transação, uma organização padrão, membership
`OWNER` e catálogos iniciais `MATERIAL`, `MACHINE` e `TOOL`. Cada execução do
ambiente controlado grava um registro vinculado ao usuário, projeto, documento,
organização, versão e hashes dos artefatos. O download só é aceito quando uma
revisão humana persistida existe e os hashes recebidos continuam idênticos aos do
resultado registrado. O feedback é armazenado por resultado, usuário, projeto e
versão, com uma avaliação por usuário.

## Consequências

- A jornada cadastro → projeto → STEP → resultado → revisão → download → feedback
  pode ser concluída sem preparação administrativa manual.
- Atualizar a página não elimina a evidência de revisão no servidor.
- Um resultado alterado, pertencente a outro usuário ou ainda não revisado falha
  fechado.
- A aprovação permite somente o download controlado de um candidato. G9,
  autoridade física e capacidades de máquina continuam bloqueados.

## Alternativas consideradas

Manter a confirmação somente no navegador foi rejeitado porque não produz
evidência auditável e permite perder o estado entre sessões. Tratar a revisão como
aprovação de G9 foi rejeitado porque ampliaria a autoridade do produto além do
escopo autorizado.
