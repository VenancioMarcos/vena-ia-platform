# CTO-CODEX-AUTO-016 — Quantização agregada de plano

**Data:** 2026-09-09
**Estado:** implementação e validação concluídas; commit/envio como próximos passos.
**Base:** ebbe37e; AUTO-015 aprovada pelo Gemini por relatório, sem inspeção independente.

## Objetivo e escopo

Agregar relatórios numéricos de ambos os extremos de todos os movimentos.
Contagem significa movimentos, não pontos: len(move_reports)=2*evaluated_moves_count.
Ordem achatada por operação/movimento, start depois end; pontos compartilhados
repetidos preservam correspondência. Limite 10000 movimentos/20000 relatórios.
Precisão estrita 1..6 inclusive para plano vazio; revalidação profunda antes de
calcular. Falha em qualquer ponto aborta a função, sem sumário parcial.
Máximo positivo=max(0,desvios); extremo negativo=min(0,desvios), sem interpretar
sinal como dentro/fora de material físico. Vazio produz zeros e NOT_EVALUATED.
Schema valida contagem/extremos/coerência numérica; não atesta proveniência,
política da quantização declarada ou vínculo criptográfico com plano.

## Arquivos previstos

turning_toolpath_schemas.py, turning_quantization.py, testes do avaliador,
ADR0037/DEC047, CONTEXT/CHANGELOG, registros e continuidade CTO.

## Testes e critérios de aceitação

45 testes do avaliador passed em 3.51 s, incluindo 22 novos: fixtures
canônica/escalonada com planner real; sequência, todos os tipos, sinais, vazio,
contratos forjados/revalidação profunda, falhas numéricas e replay/imutabilidade.
Regressão completa 614 passed (=592+22), 2 skipped, zero falhas em 118.57 s.
Skips Redis real auth/jobs inalterados. Ruff PASS; mypy PASS193 fontes;
7 links relativos/fences e git diff --check PASS. Python3.14.6 experimental,
sem novo CI remoto. Log ignorado .pytest_cache/auto016-pytest.log.
Nenhuma emissão NC, fronteira física ou integração Digital Thread.

## Próximos passos

Commit local, enviar relatório com SHA real e pedir/aguardar próxima ordem.
NON_PRODUCTION; G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false;
CONTROLLER_PROFILE_UNRESOLVED; sem Git de rede.

## Parecer e próxima ordem

Commit 770ac7bc46228e93b657b6aa29de4be7c82d80ac, árvore limpa, enviado e
aprovado pelo Gemini por relatório. Recebida AUTO-017: integrar quarto estágio
numérico ao orquestrador com precisão e digest, sem NC/autoridade.
