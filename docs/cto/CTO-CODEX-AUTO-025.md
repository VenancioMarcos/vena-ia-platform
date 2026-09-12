# CTO-CODEX-AUTO-025 — Testes locais dos contratos web

## Objetivo

Parecer AUTO-024/B APROVADO recebido no Gemini em 2026-09-10 para 116059d3.
AUTO-025 solicita testes das três fixtures e dos sete estados do contrato v3.

## Escopo

Usar TypeScript instalado para compilar testes isolados e runner nativo node:test.
Sem novas dependências ou alteração de manifests, backend ou código de produto.
Compatível com ADR-0037: testes não implementam validação de JSON externo,
geometria ou autoridade física. WEB-LINT-001 permanece aberto.

## Arquivos Criados

- apps/web/tests/turning-contracts.test.ts: round trip JSON, vínculos de endpoints,
  flags, dispatch/predicado dos sete estados e evidências distintas de falha.
- Este registro de entrega.

## Arquivos Modificados

README de fixtures e documentos de continuidade CTO/CONTEXT.

## Testes Realizados

- Runner nativo:14 passed,0 failed,0 skipped (569.4599ms), após compilação isolada.
- TypeScript completo: PASS; next lint exit0, zero erros e apenas WEB-LINT-001.
- Python:658 passed,2 skipped,0 failed em152.01s; Ruff PASS; diff PASS.
- next-env.d.ts regenerado pelo lint restaurado byte a byte ao HEAD.
- Node24.19.0 instalado difere de engines22.20.x; Python3.14.6 experimental.
  Nenhuma equivalência a CI remoto ou runtime homologado é alegada.
- Compilação inicial exigiu typeRoots explícito e anotação de relatório;
  comando reprodutível final consta no README de fixtures.

Quatro estados iniciais são amostras de teste construídas localmente;
somente as três fixtures existentes são exportações reais do backend.

## Critérios de Aceitação

Runner, typecheck, lint com apenas WEB-LINT-001, regressão Python, Ruff e diff PASS.
Não promover tipos/predicado de resultados tipados a validador de entrada externa.

## Próximos Passos

Validações concluídas. Commit local, relatar via VTP e aguardar próxima ordem real.
G9 pendente; autoridade física e envio a máquina false. Sem Git de rede/publicação.
