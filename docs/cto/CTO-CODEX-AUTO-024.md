# CTO-CODEX-AUTO-024/A — Configuração local do lint web

## Objetivo

Resolver a configuração ausente do lint após aprovação AUTO-023/A pelo Gemini
no commit 870ffa2. Ordem recebida após envio expressamente autorizado pelo dono.

## Escopo

Somente configuração local compatível com ESLint/Next instalados, incluindo lib
e tests. Sem dependências, contratos, backend, Git de rede ou publicação.

## Arquivos criados/modificados

apps/web/.eslintrc.json, apps/web/next.config.ts, este registro, CONTEXT.md,
CURRENT_ORDER.md, EXECUTION_STATUS.md, ORDER_HISTORY.md e CHANGELOG.md.
Configuração next/core-web-vitals + next/typescript com pacotes existentes.
Override restrito a tests/**/*.typecheck.ts permite argumento _ não utilizado;
nenhuma regra suprimida globalmente nem arquivo de contratos/fixtures ignorado.

## Testes realizados

- next lint --no-cache: exit0, zero erros, um warning react-hooks/exhaustive-deps
  preexistente em app/projects/[projectId]/page.tsx:131 (jobControllers.current
  no cleanup). Aviso de depreciação next lint continua; sem migração nesta missão.
- ESLint 9.39.5/Next 15.5.22 já instalados: calculateConfigForFile/isPathIgnored
  confirmam 98 regras e ignored=false para contrato, teste estático e três fixtures.
- tsc --noEmit --incremental false: PASS. next-env.d.ts gerado pela CLI foi
  restaurado ao conteúdo exato do baseline antes desta checagem final.
- Pytest: 658 passed, 2 skipped, 0 failed em129.69s. Skips Redis real existentes.
- Diff PASS; backend, contratos, fixtures, manifests e locks intactos.
- Node24.19.0/Python3.14.6 locais fora das versões oficiais; nenhum CI remoto novo.

## Ressalva e backlog

CTO acolheu em parecer real a entrega AR condicionada à regressão Python verde,
agora satisfeita. AR usado aqui como entrega com ressalva explícita, sem afirmar
zero warnings. Backlog WEB-LINT-001: revisar captura/identidade de jobControllers
no cleanup da página de projeto e validar cancelamento de requisições ao desmontar.
Não corrigir via supressão automática ou alteração funcional nesta missão.
Configuração legacy é suportada pela CLI instalada; migração futura separada.

## Critérios de aceitação

Lint cobre contratos/fixtures/testes sem excluir esses arquivos, sem alterar
regras de negócio. Dependências e locks intactos, tree limpa após commit local.

## Próximos passos

Validar, registrar evidências, enviar relatório e aguardar parecer/próxima ordem.
G9 pendente; PHYSICAL_USE_AUTHORIZED=false; CONTROLLER_PROFILE_UNRESOLVED;
machine-send/DNC/NC-transfer/cycle-start=false.
