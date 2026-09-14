# Registro de Entrega — VTP-AUTO-258-BATCH

**Status:** A
**Data:** 2026-09-14
**Branch:** `codex/v7.9-cnc-operational-risk-matrix`
**Baseline:** `1f6bb75c99336ff003bde8c03a602fe6a6a31e92`

## Objetivo

Publicar e integrar o otimizador multicritério da Rota 17 e implementar uma matriz
analítica consolidada de risco operacional CNC, sem conceder autoridade física.

## Escopo

- Draft PR #65, CI remoto, transição para Ready, squash merge e sincronização da main.
- Agregação ponderada dos riscos dimensional, dinâmico, energético e de desgaste.
- Estado crítico compulsório para violações de envelope, geometria ou colisão.
- Contrato Pydantic que recalcula escores, nível e recomendações de mitigação.
- Validação cruzada contra snapshots de geometria, placa, estabilidade, Kienzle e Taylor.
- Integração no relatório JSON, exportador textual e painel Web por categoria.

## Arquivos Criados

- `apps/api/app/modules/cnc/services/risk_matrix_evaluator.py`
- `apps/api/tests/unit/cnc/test_risk_matrix_evaluator.py`
- `docs/cto/CTO-CODEX-AUTO-258-BATCH.md`

## Arquivos Modificados

- `apps/api/app/modules/cnc/schemas.py`
- `apps/api/app/modules/cnc/services/machining_report.py`
- `apps/api/app/modules/cnc/services/text_report_exporter.py`
- `apps/api/tests/unit/cnc/test_machining_report.py`
- `apps/web/src/components/cnc/MachiningTechnicalReportViewer.tsx`
- `apps/web/tests/machining-technical-report-viewer.test.ts`
- `CONTEXT.md` e registros em `docs/cto/`.

## Testes Realizados

- 874 testes da API aprovados e 2 ignorados; 171 testes do domínio CNC aprovados.
- 39 testes focados de matriz/relatório e 17 testes Web aprovados.
- TypeScript completo e estrito, Next lint, Ruff, mypy em 205 fontes e
  `git diff --check`: aprovados.
- Nenhuma dependência externa de rede instalada.

## Critérios de Aceitação

- Pesos: dimensional 35%, dinâmico 25%, energético 20% e desgaste 20%.
- Cada alerta analítico ativo vale 75 pontos na categoria; violação dimensional,
  cinemática ou colisão vale 100 pontos e força `CRITICAL_INTERVENTION_MANDATORY`.
- O nível consolidado é determinístico: baixo, moderado, alto com mitigação ou crítico.
- O manifesto rejeita matriz adulterada ou transplantada de outro snapshot.
- JSON, laudo e viewer incluem scores, nível, mitigações e a nota pericial obrigatória.
- Não há controle de autorização, transmissão, sobrescrita ou execução física.
- `PHYSICAL_USE_AUTHORIZED=FALSE`, `G9=PENDING_AUTHORITATIVE_REVIEW`,
  `NO_HUMAN_REVIEW_BYPASS=TRUE`, `MACHINE_SEND/DNC/NC_TRANSFER/CYCLE_START=false`,
  `emission_status=CONTROLLER_PROFILE_UNRESOLVED` e `executable_output=false`.

## Próximos Passos

Enviar `VTP-AUTO-258-BATCH` ao CTO e aguardar parecer e próxima ordem. A branch
permanece local, sem push.
