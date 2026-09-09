# CTO-CODEX-AUTO-012 — Contrato numérico de quantização

**Data:** 2026-09-09
**Estado:** AUTO-012A aprovada pelo CTO; EXEC-014 retoma commit após liberação do revisor.
**Base:** dc75997, árvore limpa, 548 testes aprovados/2 ignorados na STAB-010.

## Objetivo

Modelar declaração de reconstrução radial e desvio numérico, sem emissão NC.

## Escopo e conflito antes de implementar

AUTO-012 retoma trabalho local após HOLD-011 por nova ordem técnica. O campo
is_boundary_safe não pode aceitar conclusão de segurança a partir apenas de
R/X/reconstrução/desvio: faltam Z, zonas, envelope e trajetória.
Proposta enviada: LiteralFalse, boundary_status=NOT_EVALUATED, limitação literal
NUMERICAL_QUANTIZATION_CHECK_ONLY. Raios/diâmetro finitos e não negativos;
reconstrução X/2 e desvio assinado reconstructed-original, sem tolerância que
esconda inconsistência. Não formatar NC nem afirmar que X veio de programa real.

## Arquivos criados

Este registro e apps/api/tests/modules/engineering/test_turning_quantization_schemas.py.

## Arquivos modificados

turning_toolpath_schemas.py, ADR-0037/DEC-047, CONTEXT, CHANGELOG e
documentos de continuidade CTO após decisão técnica.

## Testes realizados

21 testes específicos passed em 0.76 s; Ruff PASS e mypy PASS em 192 fontes.
Suíte completa: 569 passed (=548+21), 2 skipped em 155.99 s; zero falhas.

## Critérios de aceitação

Ajuste confirmado integralmente pelo CTO. Contrato/testes preservam
is_boundary_safe=false, boundary_status=NOT_EVALUATED e limitação fixa.

## Próximos passos

Aguardar resposta real do CTO, registrar decisão, implementar/testar e criar
commit local; enviar relatório e pedir/aguardar próxima ordem.
NON_PRODUCTION; G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false;
CONTROLLER_PROFILE_UNRESOLVED; sem NC, Git de rede, merge/tag ou publicação.

## Decisão recebida

CTO acolheu o ajuste integralmente e emitiu AUTO-012A: contrato numérico
sem segurança de fronteira inferida. Commit: feat(cam): add numerical quantization check schema contracts.

## Semântica numérica implementada

TurningQuantizationReport herda contrato estrito/frozen/extra forbid,
allow_inf_nan=false e revalidate_instances=always. Original R, X em diâmetro e
R reconstruído são finitos >=0; desvio é assinado, positivo significa aumento
de raio, sem afirmar localização do material. Limitações são tuple literal
obrigatória NUMERICAL_QUANTIZATION_CHECK_ONLY, não removível por payload válido.

O modelo compara os resultados das operações BINÁRIAS de float X/2 e
reconstructed-original por igualdade. Usa tolerância zero sobre esses resultados
para não esconder discrepância de uma ULP ou apagar valor pequeno com epsilon
absoluto. Isso é coerência da aritmética declarada, não igualdade de decimais
ideais nem avaliação de uma política textual de arredondamento. Um desvio
decimal informado independentemente pode precisar ser recalculado nas operações
declaradas; o schema não o normaliza. A sugestão genérica de epsilon da ordem
foi delimitada assim para preservar a conferência sem tolerância permissiva
acolhida no ajuste. Subfluxo que transforma X positivo em R zero é rejeitado;
subnormais representáveis são preservados. Erro de representação anterior não
é atestado pelo schema.

Não há valor Z, limites, envelope, trajetória, formato textual, fonte de NC,
controlador ou Digital Thread integrado. X é declaração numérica e não prova
de comando programado real. Campos extras de autoridade são rejeitados.
Testes positivos de desvio +/-/zero, negativos, NaN/Inf/coerções, uma ULP,
subfluxo/subnormal/magnitude extrema, replay/JSON, imutabilidade e model_copy
forjado cobrem o novo contrato. Nenhum formatter/quantizador NC adicionado.

## Validação final e bloqueio de commit

21 testes específicos passed em 0.76 s; suíte 569 passed/2 skipped em 155.99 s.
Ruff PASS; mypy PASS em 192 fontes; 6 links relativos/fences PASS; git diff --check
PASS. Skips Redis auth/jobs inalterados. Python local 3.14.6 experimental; nenhum
CI remoto alegado. Nenhum código alterado após a suíte completa.

Revisão automática rejeitou git add: limite de uso atingido; indicou liberação
em 10/09/2026 00:40 (fuso não especificado na mensagem). Nenhum staging/commit
realizado e nenhum contorno utilizado. HEAD permanece dc75997, árvore com as
alterações desta missão (não limpa). Entrega técnica pronta; commit pendente de
restabelecimento da revisão. Não afirmar commit ou working tree limpa ao CTO.

## Retomada EXEC-014

CTO recebeu relato de novo login do proprietário e emitiu EXEC-014. Repetição
do git add pelo revisor normal aceita; bloqueio anterior superado nesta chamada.
Somente arquivos da AUTO-012A e governança presentes; testes estão em
test_turning_quantization_schemas.py, arquivo correspondente permitido na ordem
original, sem duplicar test_turning_schemas.py. Commit e revalidação a seguir.
