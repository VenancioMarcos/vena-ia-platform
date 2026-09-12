# CTO-CODEX-POST-009 — Pré-requisitos do pós-processador

**Data:** 2026-09-09
**Estado:** POST-009A documental concluída; emissão POST-009 cancelada pelo CTO.
**Base:** 5f50559, CAM-008A aprovada tecnicamente no escopo por relatório;
548 passed/2 skipped, Ruff/mypy PASS em 192 fontes.

## Objetivo

Resolver o escopo de pós-processamento sem inferir semântica de dialeto ou
promover planejamento sintético a trajetória física válida.

## Escopo e conflito documentado antes de implementar

POST-009 pede cabeçalho G18/G21/G90, modos G94/G95, avanço F, recuo seguro para
troca e emissão de candidato. ADR-0037 exige controlador/manual resolvidos;
FANUC_ISO_COMPATIBLE e GENERIC_LATHE_ISO não identificam modelo/versão/sistema.
O plano não fornece valor F, ferramenta/offset/compensação, posição inicial ou
troca física, sequência de entrada/saída validada ou material remanescente.
Rotular NON_PRODUCTION não supre dados nem prova validade técnica do cabeçalho.
Quantização para três decimais exige revalidar o trajeto arredondado e pode não
preservar exatamente X=2*R; RETRACT não permite inferir G00/G01 seguro.

Fonte primária reverificada em 2026-09-09: [Haas — códigos de torno](https://www.haascnc.com/service/service-content/guide-procedures/lathe---g-codes.html).
Nesse controlador, G90/G94/G95 são ciclos de torneamento/faceamento/rosqueamento
rígido com ferramenta acionada. Contraexemplo à universalidade, não escolha de
Haas. A correção já foi acolhida na SPEC-003 e registrada no ADR-0037, linhas 140–147.

Proposta enviada diretamente ao CTO: POST-009A documental, matriz de lacunas,
contrato de revisão e template de coleta dos dados de controlador/máquina,
ferramenta, setup, feed/spindle, entrada/saída e quantização. Sem implementar NC.

## Arquivos criados

- Este registro de entrega e conflito.
- [TURNING_CONTROLLER_PREREQUISITES.md](../engineering/TURNING_CONTROLLER_PREREQUISITES.md):
  matriz de requisitos/lacunas, quantização, template e contrato de revisão.

## Arquivos modificados

ADR-0037, DEC-047, CONTEXT, CHANGELOG, CURRENT_ORDER, EXECUTION_STATUS,
ORDER_HISTORY e registro do parecer CAM-008A.

## Testes realizados

Inspeção de contratos/ADR e fonte oficial. Nenhum código de produto modificado.
Reexecução da suíte completa solicitada explicitamente na ordem POST-009A:
548 passed/2 skipped em 170.51 s, zero falhas; Redis auth/jobs inalterados.
Ruff PASS; mypy PASS em 192 fontes. Python 3.14.6 local experimental;
nenhum CI remoto alegado. Log local ignorado .pytest_cache/post009a-pytest.log.
Validação documental PASS: 18 links relativos/âncoras, 2 tabelas com colunas
consistentes, fences balanceadas e espaçamento de títulos. Diff check PASS.
Nenhum código de produto alterado.

## Critérios de aceitação

Escopo corrigido confirmado integralmente. Documento cobre 26 requisitos
identificados, matriz das seis camadas, fonte primária, quantização com exemplo
numérico e fronteira violada após arredondamento, template preenchível e etapas
de revisão. Nenhuma família genérica é prova de semântica; emissão continua bloqueada.

## Próximos passos

Commit documental local, enviar relatório e pedir/aguardar nova ordem real.
A emissão depende de pacote técnico real ainda não fornecido; não inventar dados.
NON_PRODUCTION; G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false.

## Parecer e delimitação confirmados

Gemini declarou o conflito procedente e cancelou POST-009, substituindo-a por
POST-009A documental. A repetição de G94/G95 como equivalências na descrição da
nova ordem foi tratada como assunto a comprovar, conforme a decisão explícita de
não universalizar códigos. Não foi necessário novo pedido ao proprietário.

O pacote não seleciona máquina, comando, ferramenta ou parâmetros de processo.
O template usa PENDENTE e IDs opacos, sem credenciais ou dados de cliente. Contrato
de revisão separa declaração, evidência, especificação futura e autoridade humana.
Exemplos de arredondamento são matemática decimal, não tolerâncias de máquina.
O preenchimento do documento não libera candidato NC, runtime ou G9.

Commit solicitado: docs(turning): document controller prerequisites and postprocessor gap matrix.

## Commit e envio

Commit f3fb048b79bffd35782207e4de00cf620546003b; 10 arquivos,
393 inserções/8 remoções. Árvore limpa após commit. Envio ao CTO realizado
após verificar que a primeira tentativa de preenchimento falhou sem envio.
Solicitados parecer e próxima ordem; aguardando resposta real. Sem push/NC.

Parecer recebido: APROVADO TECNICAMENTE NO ESCOPO por relatório. STAB-010
emitida para auditoria e consolidação de marco documental local.
