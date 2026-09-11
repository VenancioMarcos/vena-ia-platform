# TASK-LOCAL-027 — Bordas numéricas da projeção RZ

## Objetivo

Parecer final AUTO-026 AR recebido no Gemini para32e1df8. A resposta iniciou
AUTO-027 sobre componente React, mas terminou com TASK-LOCAL-027 delimitada a
regressões numéricas; seguimos a instrução final completa, sem implementar UI.

## Escopo

Somente testes: R/Z próximos de zero, linhas de extensão1e-9 mm, padding em
viewports1/2/16/32px e recuperação tela/peça. Tolerâncias de1e-9px,1e-10mm e1e-12px
nos casos definidos, inferiores ao teto1e-5 solicitado. Não garantem precisão
universal fora desses casos. Compatível com ADR-0037, sem mudança arquitetural.

## Arquivos Criados

Este registro.

## Arquivos Modificados

apps/web/tests/rz-projection.test.ts, CONTEXT e continuidade CTO.

## Testes Realizados

29 testes web PASS,0 failed/0 skipped em225.1205ms; TypeScript completo PASS.
Python658 passed,2 skipped,0 failed em129.58s;diff PASS. Runner conforme AUTO-026, usando temp/local027-web-tests.
Node24.19.0 difere de engines22.20.x; Python3.14.6 experimental.

## Critérios de Aceitação

Web/Python/tsc verdes, diff aprovado e árvore limpa após commit local.
Sem backend, schemas, API, configuração global ou rede Git.

## Próximos Passos

Validações concluídas; commit local, enviar VTP ao CTO e aguardar próxima ordem real.
G9 pendente, autoridade física/envio a máquina false. WEB-LINT-001 segue aberto.
