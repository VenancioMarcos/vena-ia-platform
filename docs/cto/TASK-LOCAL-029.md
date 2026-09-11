# TASK-LOCAL-029 — Seletor de fixtures local

## Objetivo

Após aceite028 emcd14b92, CTO solicitou contêiner cliente local com seleção das
três fixtures, metadados, badges neutros e SVG. Sem chamadas de rede.

## Escopo

Componente isolado usa useState. Exibe plano quantizado; falha de reconstrução
possui plano nominal retido, mas quantized_plan nulo: não substituir silenciosamente.
Contagens e unidades derivadas do plano exibido. initialSelection opcional permite
SSR dos três estados e define somente seleção inicial. Não adiciona rota.

## Arquivos Criados

- apps/web/components/cam/TurningViewerContainer.tsx
- apps/web/tests/turning-viewer-container.test.ts
- Este registro.

## Arquivos Modificados

CONTEXT, continuidade CTO e incremento ADR-0037.

## Testes Realizados

Concluída em2026-09-11:37 testes web PASS,0 failed/0 skipped em677.8292ms.
Python658 passed,2 skipped,0 failed em133.49s;tsc/Ruff/diff PASS;lint exit0
apenas WEB-LINT-001. SSR cobre estados iniciais; não prova interação de troca no browser.
Node24.19.0 difere de engines22.20.x;Python3.14.6 experimental. Sem CI remoto.
next-env.d.ts restaurado ao HEAD após lint.
Usar runner028 incluindo turning-viewer-container.test.ts/.js e pasta local029.

## Critérios de Aceitação

Web,tsc,lint apenas WEB-LINT-001,Python,Ruff,diff PASS. Sem manifests/backend/rede.

## Próximos Passos

Validações concluídas; commit local, VTP ao CTO e aguardar próxima instrução real.
NON_PRODUCTION;G9 pendente;autoridade física false.
