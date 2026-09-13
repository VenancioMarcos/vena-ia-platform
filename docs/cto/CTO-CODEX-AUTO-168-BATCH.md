# CTO-CODEX-AUTO-164 a AUTO-168 — Auditor dimensional CNC

## Objetivo

Publicar e integrar o visualizador da Rota CNC 8 e criar um auditor server-side,
analítico e fail-closed para consistência entre limites nominais do BRep e extremos
de movimentos programados em torneamento.

## Escopo

- AUTO-164: branch da Rota 8 publicada e Draft PR #56 aberto.
- AUTO-165: Frontend CI aprovado em 1m03s; PR promovido a Ready, MERGEABLE/CLEAN.
- AUTO-166: PR #56 integrado por squash em `b43aca7` após autorização explícita;
  branch remota removida e `main=origin/main`.
- AUTO-167/168: auditor preparado localmente sobre a baseline integrada na branch
  `codex/v7.0-cnc-geometry-dimensional-auditor`, sem push.

## Arquivos Criados

- `apps/api/app/modules/cnc/services/geometry_auditor.py`
- `apps/api/tests/unit/cnc/test_geometry_auditor.py`
- Este registro.

## Arquivos Modificados

- `CONTEXT.md`
- `docs/cto/CURRENT_ORDER.md`
- `docs/cto/EXECUTION_STATUS.md`
- `docs/cto/ORDER_HISTORY.md`

## Implementação

O contrato `vena-ia.cnc-geometry-dimensional-audit/v1` recebe limites nominais
R/Z provenientes do BRep e segmentos programados já analisados em X-diâmetro/Z.
Registra raio mínimo/máximo, limites axiais e desvios assinados de raio máximo,
Z mínimo e Z máximo. O gate `manifest_generation_allowed` somente abre quando
todos os desvios estão dentro da tolerância e não há achados.

O auditor rejeita de forma determinística raio programado negativo, reversão de
sentido radial entre movimentos lineares e qualquer divergência dimensional. A
função `require_geometry_dimensions_consistent` lança erro contendo o relatório
analítico completo, preservando a evidência sem produzir manifesto subsequente.
Movimentos rápidos não são tratados como reversão de corte.

## Testes Realizados

- Auditor focado: 14 aprovados.
- Backend API: 763 aprovados, 2 ignorados.
- Operações: 69 aprovados, 7 ignorados; total Python 832/9.
- Web compilado + `node:test`: 77 aprovados.
- TypeScript e Next lint: aprovados sem erros ou warnings.
- Ruff: aprovado.
- mypy: 215 arquivos aprovados.
- `git diff --check`: aprovado.

Uma tentativa direta de executar fontes `.ts` sem compilação falhou apenas por
resolução de módulos; a execução válida recompilou os testes dentro da árvore Web e
aprovou os 77 casos. Nenhuma dependência foi instalada ou obtida pela rede.

## Critérios de Aceitação

Os cálculos são determinísticos, usam tolerância absoluta explícita e conservam a
convenção `LATHE_X_DIAMETER_Z`. O relatório e seus desvios são contratos Pydantic
estritos, imutáveis e revalidados. Achados mantêm o gate fechado, e todas as flags
de governança continuam nos valores restritivos. Nenhuma saída executável, controle
de máquina, envio, DNC, transferência NC ou ciclo físico foi adicionado.

## Limitações e Próximos Passos

O serviço exige que o chamador forneça limites BRep autoritativos e segmentos já
interpretados; não infere geometria nem tolerância. A ligação a um gerador de
manifesto futuro deve chamar o gate obrigatório antes de construir o manifesto.
Enviar o VTP-AUTO-168-BATCH ao CTO e aguardar nova ordem. A branch permanece local.
