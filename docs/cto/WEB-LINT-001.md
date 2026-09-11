# WEB-LINT-001 — Referência mutável no cleanup de requisições

Status: ABERTO, não bloqueante para AUTO-024. Data: 2026-09-10.
Origem: AUTO-024/A, baseline d541dc0; registro formal solicitado em AUTO-024/B.

## Evidência

next lint --no-cache termina exit0 com warning react-hooks/exhaustive-deps em
apps/web/app/projects/[projectId]/page.tsx:131. Cleanup consulta
jobControllers.current, cuja identidade pode mudar antes da desmontagem.
O aviso requer análise; não constitui por si só demonstração de defeito funcional.

## Escopo de futura correção

Revisar ciclo de vida e identidade do registro de AbortControllers. Confirmar
cancelamento de todas as requisições pertinentes ao desmontar/trocar projeto,
incluindo jobs criados depois do efeito inicial e a execução em Strict Mode.
Não capturar um snapshot incompleto de controllers apenas para silenciar o lint.
Não suprimir react-hooks/exhaustive-deps como substituto da análise.

## Critérios de aceitação futuros

Cancelamento correto coberto por teste de ciclo de vida; ausência do warning;
lint e typecheck aprovados; sem alteração dos contratos sintéticos ou autoridade.
Implementação depende de missão técnica específica. Nenhuma correção neste registro.

## Entrega AUTO-024/B

Objetivo/escopo: tornar o aviso rastreável e fechar documentalmente AUTO-024.
Arquivos: este item e documentos de continuidade CTO/CONTEXT.
Validação: diff e estado Git, sem alterações sob apps/; baseline Python658/2 e
tsc/lint exit0 preservados, sem repetir suíte para registro documental.
Próximo passo: reportar commit ao CTO, pedir e aguardar parecer/nova ordem real.
Sem instalação, Git de rede, alteração de compose, domínio ou CNC.
