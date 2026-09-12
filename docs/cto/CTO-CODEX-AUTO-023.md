# CTO-CODEX-AUTO-023 — Contratos web de torneamento sintético

Data: 2026-09-10. Baseline f6335c3, AUTO-022 aprovada por relatório pelo Gemini.

## Objetivo

Espelhar synthetic-turning/v3 em TypeScript e fornecer três fixtures de resultados
reais da orquestração local, como preparação para uma futura visualização.

## Escopo

Tipos readonly em apps/web/lib, união discriminada dos sete estados e fixtures
geradas pelo serviço Python existente. Nomes da missão que não existem no backend
serão aliases explícitos dos contratos reais, sem criar novos campos de transporte.
Sem endpoint, componente visual, dependência, alteração de backend ou emissão NC.
Compatível com DEC-047/ADR-0037; validação numérica/runtime continua no Python.

## Arquivos criados

- apps/web/lib/turning-contracts.ts.
- apps/web/tests/turning-contracts.typecheck.ts.
- apps/web/tests/fixtures/cylinder-success.ts, quantized-violation.ts e
  reconstruction-failure.ts (três payloads completos, sem cast de dados não validados).
- apps/web/tests/fixtures/generate_turning_fixtures.py e README.md.
- Este registro AUTO-023.

## Arquivos modificados

AUTO-023A adicional: apps/api/tests/fixtures/cad/generate_turning_step.py,
test_turning_profile_extractor.py e dois STEP AP203 (cylinder/asymmetric).
CONTEXT.md, CHANGELOG.md, CURRENT_ORDER.md, EXECUTION_STATUS.md,
ORDER_HISTORY.md, docs/DECISIONS.md e ADR-0037. Nenhum código de produção backend, manifest ou lock alterado.

## Testes realizados

- Exportação e replay --check: três resultados Pydantic válidos, payloads idênticos
  ao serviço real. Sem monkeypatches, usando os cenários E2E originais do cilindro.
- TypeScript 5.9.3 instalado: tsc --noEmit --incremental false PASS no projeto web
  completo, incluindo 12 rejeições @ts-expect-error e narrowing exaustivo dos sete
  estados. Execução local Node 24.19.0; engines do projeto pede 22.20.x, sem alterar
  a configuração ou representar esta execução como validação no Node oficial.
- Ruff PASS; mypy PASS193 fontes. Regressão inicial: 657 passed, 2 skipped, 1 failed em 120.59 s.
  Falha de reprodução STEP confirmada isoladamente (1 failed em 3.50 s). Diff
  limitado a PERSON/ORGANIZATION nos dois AP203, com metadados de ambiente.
  Consulta enviada ao CTO propondo AUTO-023A para normalização administrativa
  não pessoal, sem tocar geometria ou afrouxar comparação byte a byte.
- Lint web existente NÃO APROVADO: next lint (Next 15.5.22 instalado) está deprecated
  e terminou exit1 solicitando configuração ESLint ausente. Sem instalar/migrar
  dependências. next-env.d.ts regenerado pela tentativa foi restaurado exatamente
  ao conteúdo prévio, e typecheck repetido para conferir a árvore final.
- Validação final AUTO-023A: 658 passed, 2 skipped, 0 failed em 107.25 s.
  Typecheck final PASS, Ruff PASS, mypy PASS193; replay dos três payloads PASS.
  Links/fences e diff PASS. Sem runtime/manifest/lock/next-env.d.ts modificado.
- Status da entrega: A no escopo aprovado AUTO-023/A; lint permanece ressalva
  explícita de tooling acolhida pelo CTO, não declarado como aprovado.

Limites: TypeScript é estrutural; não reproduz todos os validators numéricos e de
proveniência Python nem substitui validação runtime. A checagem de tipo aprovada
não significa lint aprovado. Nenhum endpoint sintético foi criado.

## Critérios de aceitação

Três casos reais: sucesso cylinder_d50_l100, violação quantizada e falha de
reconstrução; campos nulos/presenças e flags false coerentes com os estados.
Tipos não prometem validar finitude, hashes, limites ou geometria em runtime.

## Próximos passos

Concluir implementação, validar, commit local e enviar relatório ao CTO.
Pedir e aguardar parecer/próxima ordem real sem encerrar após receber missão.
G9 pendente, PHYSICAL_USE_AUTHORIZED=false, CONTROLLER_PROFILE_UNRESOLVED;
machine-send/DNC/NC-transfer/cycle-start=false. Sem Git de rede/publicação.


## Resolução AUTO-023A aprovada pelo CTO

Parecer real recebido autorizou somente normalização administrativa. PERSON e
ORGANIZATION usam literais sintéticos fixos, preservando IDs de entidades. Teste
existente mantém igualdade byte a byte e agora também verifica os literais.
Comparação programática de antigo/novo excluindo somente essas entidades:
PASS para as quatro fixtures; somente dois AP203 mudaram. Teste isolado após
correção: 1 passed em 2.85 s. Replay web/Pydantic continuou idêntico, sem regenerar
ou inventar hashes; BRep não depende dessas entidades administrativas.

O parcial foi enviado e aprovado pelo CTO antes do fechamento. A alegação de
árvore limpa durante implementação foi corrigida na conversa e acolhida. Lint
falhou por configuração ausente/depreciação; não foi demonstrado que Node24
causou essa falha. O desvio de engine é uma limitação separada de validação.
Auditoria AUTO-022 pesquisou credenciais conhecidas, não todos os metadados:
commits e bundle anteriores retêm os metadados ambientais antigos. Não reescrever
histórico nesta missão; revisão de privacidade antes de qualquer publicação.
