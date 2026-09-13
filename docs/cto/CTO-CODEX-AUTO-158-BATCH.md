# AUTO-154 a AUTO-158 — Rota CNC 7

## Objetivo
Executar a ordem completa lida no Gemini em 2026-09-13, conversa
https://gemini.google.com/app/62dacc664840eafe: integrar PR #54 e implementar
relatório técnico JSON autenticado, sem saída executável ou autoridade física.

## Escopo
AUTO-154: PR #54 confirmado OPEN, ready, MERGEABLE/CLEAN no head
292871a7447e5663604b98d119b482835eb86047, Backend e Frontend CI SUCCESS. Após
autorização explícita do proprietário, squash merge concluído em `9d8b2dbe`; main
local/remota alinhadas e branch remota removida. A deleção local recusada pelo Git
por estar em uso foi resolvida ao mover o checkout original para main, sem perda.
AUTO-155–158 foram executadas sobre essa baseline, sem push.

O GET depende da última simulação bem-sucedida e vinculada ao plano CAM do
proprietário. Sem ela: 422. Plano ausente/alheio: 404; sem autenticação: 401.
Cache limitado, process-local, sem migration: perda/evicção exige nova simulação.
O compilador revalida plano e vínculo com a fonte e recalcula auditorias a partir
do programa gerado no servidor. Texto ISO avulso não cria relatório de plano.
Nome do plano ausente é null; horário é o da captura analítica UTC, não de máquina.
Estimativas seguem Rota 6: distâncias X-diâmetro/Z e aproximação modal existente;
não são tempos físicos, especialmente para G96/CSS, aceleração e troca de ferramenta.

## Arquivos Criados
- `apps/api/app/modules/cnc/services/machining_report.py`
- `apps/api/app/modules/cnc/report_repository.py`
- `apps/api/tests/unit/cnc/test_machining_report.py`
- Este registro.

## Arquivos Modificados
- Inicialização, schemas e router CNC.
- Fixtures globais e teste de integração do router CNC.
- `CONTEXT.md` e registros CTO de ordem, status e histórico.

## Testes Realizados
- Unitários e integração focados: 32 aprovados.
- Backend API: 749 aprovados, 2 ignorados; operações: 69 aprovados, 7 ignorados.
  Total local consolidado: 818 aprovados, 9 ignorados. A primeira execução das
  operações teve um timeout ambiental de 20 s no subprocesso de registro ORM; o
  caso passou isolado em 7,50 s e a suíte operacional completa repetida passou.
- Web `node:test`: 74 aprovados; TypeScript e Next lint aprovados sem warnings.
- Ruff, mypy em 214 arquivos e `git diff --check`: aprovados.
- Python 3.14.6 e Node 24.19.0 locais são experimentais frente à policy 3.13.11/
  22.20.0; CI da baseline #54 permanece a evidência homologada dessas versões.

## Critérios de Aceitação
Manifesto completo; carimbo obrigatório e flags literais; falha fechada em
fontes ausentes/corrompidas; isolamento por proprietário; testes e checks locais.
Todos atendidos. O relatório nunca inclui `program_text` nem promove qualquer flag.

## Próximos Passos
Emitir VTP-AUTO-158-BATCH ao CTO e aguardar nova ordem. Branch permanece local.
