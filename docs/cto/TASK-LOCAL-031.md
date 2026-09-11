# TASK-LOCAL-031 — Lint e responsividade

## Objetivo

Após aceite030 em e4da6ad, resolver WEB-LINT-001 e validar Mobile/Tablet.
Ordem formal recuperada em 2026-09-11 na conversa CTO 62dacc664840eafe;
complementa a instrução compacta com pytest, Ruff e três viewports.

## Escopo

Cleanup captura o registro vivo de AbortControllers na montagem. A identidade
não é substituída no código atual; entradas são adicionadas/removidas no mesmo
objeto. Object.values é calculado no cleanup, incluindo jobs registrados depois
do setup. Sem supressão de lint nem alteração de regras de negócio.
CSS min-w-0/break-words corrige overflow real no motivo de falha.
A proporção métrica R:Z 1:1 é preservada; canvas original continua 640x400,
reduzido uniformemente. A instrução de preservar 1:1 foi interpretada como escala
geométrica, não converter o canvas existente em quadrado.

## Arquivos Criados

- apps/web/tests/project-cleanup.test.ts
- Este registro.

## Arquivos Modificados

Página de projeto, TurningViewerContainer, WEB-LINT-001, CONTEXT,
CURRENT_ORDER, EXECUTION_STATUS, ORDER_HISTORY e ADR-0037.

## Testes Realizados

41 testes web PASS, 0 failed/0 skipped, 1148.074ms. Inclui três testes do corpo
real do efeito extraído por AST: cancelamento inicial e jobs tardios, retenção
da referência de montagem e setup-cleanup-setup. AbortControllers reais;
harness controlado, não teste de montagem React nem integração HTTP.
Lint exit0 sem errors/warnings; tsc --noEmit --incremental false PASS;
Ruff PASS; Python 658 passed/2 skipped/0 failed em168.24s (Redis opcional).
Reprodução: comando de compilação030 acrescentando project-cleanup.test.ts,
outDir temp/local031-web-tests, seguido de node --test para os seis arquivos,
a partir de apps/web com NODE_PATH apontando a seu node_modules.

QA via navegador local /cam/turning: três cenários em375x667,390x844,768x1024.
Em todos os nove casos scrollWidth igual a clientWidth: sem overflow horizontal.
Área útil móvel360/375px devido à barra vertical; tablet753/768px conforme barra.
SVG presente no sucesso/violação e ausente na falha. Título, controles, badges,
metadados e gráfico conferidos visualmente em screenshots; rolagem vertical normal.
Erro original em390x844: scrollWidth398/clientWidth375; depois375/375.
Gráfico móvel309.6x193.5 e tablet640x400 mantêm a mesma proporção do viewBox.
Viewport restaurado, servidor temporário encerrado; next-env restaurado do HEAD.
Node24.19.0 versus engines22.20.x;Python3.14.6 experimental;sem CI remoto.

## Critérios de Aceitação

Lint limpo, tipos/regressões aprovados e layout responsivo sem transbordamento.
Limite: operações assíncronas que criem novos jobs somente depois do cleanup
não são corrigidas por esta mudança. Harness não certifica todo ciclo React/HTTP.

## Próximos Passos

Commit local, relatório VTP ao CTO e aguardar parecer/ordem real.
G9 pendente;autoridade física false;sem API/backend/manifests/Git remoto/publicação.
